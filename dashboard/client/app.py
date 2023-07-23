from flask import Flask, request, redirect
import sqlite3
from datetime import datetime

# This program receives GET requests from the frontend, queries the database
# then responds in JSON (python dictionary)
#
# Let SQL do the complicated computations
# running (windows):
# $ pipenv run flask run --host=0.0.0.0
# Also set flask to dev mode (powershell) to enable hot reload
# $env:FLASK_ENV="development"

app = Flask(__name__, static_folder="./Public/", static_url_path="")

# Path to sqlite database
dbPath = "../../activity.db"

# open a read-only connection to the db using uri
# Allow connection as a non-creator of db
db = sqlite3.connect("file:" + dbPath + "?mode=ro", check_same_thread=False, uri=True)

db.row_factory = sqlite3.Row

TABLE_COLUMNS = ["actStart", "actEnd", "inactDuration", "windowName", "processName"]


@app.route("/api/activities/all", methods=["GET"])
def activities():
    """
    Get all activities from database. Sorted chronologically.
    query params:
    returns:
    json dict, status code, headers
    """
    queryData = {}

    activityData = db.execute(
        """
        SELECT * FROM activity_data;
        """
    )

    # fetchall() returns a list of SQL ROW objects.
    # Creates a dictionary with key "rows" that contain a list of dict
    # that each represent a row in the table.

    queryKeys = ["actStart", "actEnd", "inactDuration", "processName", "windowName"]
    for key in queryKeys:
        queryData[key] = []
        # queryData[key] = [dict(row)[key] for row in activityData.fetchall()]

    for row in activityData.fetchall():
        for key in queryKeys:
            queryData[key].append(dict(row)[key])

    headers = {"Access-Control-Allow-Origin": "*"}
    statusCode = 200

    return queryData, statusCode, headers


@app.route("/api/activities/filter", methods=["GET"])
def filter_activities():
    """
    Get and filter activities from database.
    query params:
        order-by:
            default value:
                actStart
            possible values:
                actStart, actEnd, inactDuration, windowName, processName

        order:
            default value:
                ascending
            possible values:
                ascending, descending

        fields:
            Which fields to return

            default value:
                actStart,actEnd,inactDuration,windowName,processName
            possible values:
                any of the ff: actStart, actEnd, inactDuration, windowName, processName
                if one or more, join with values with comma
                fields=actStart,actEnd,inactDuration

        timestamp_from:
            date and time to retrieve data from

            default value:
                'now'

            possible values:
                iso8601 timestamp
                2023-07-23T11:36:01.111

        timestamp_to:
            date and time to retrieve data to

            default value:
                'now'

            possible values:
                iso8601 timestamp
                2023-07-23T11:36:01.111

        limit:
            limit number of results

            default value:
                1
            possible values:
                uint

    returns:
    {
        "error": string. '' or '<message>'
        "result": string
    }, status code, headers
    """
    headers = {"Access-Control-Allow-Origin": "*"}

    print("laskjdf", len(request.args))
    # Get query params. If not present, use default.
    orderBy = request.args.get("order-by") or "actStart"
    order = request.args.get("order") or "ascending"
    fields = request.args.get("fields") or ",".join(TABLE_COLUMNS)
    timestampFrom = request.args.get("timestamp_from") or "now"
    timestampTo = request.args.get("timestamp_to") or "now"
    limit = request.args.get("limit") or "1"

    # Separate fields by comma, turn it to array
    fieldsList = fields.split(",")

    # make all items of fieldsList unique with set
    # See if all the items of fieldsList are all TABLE_COLUMNS
    if not len(set(fieldsList).difference(TABLE_COLUMNS)) == 0:
        return {"error": "bad query parameter: `fields`"}, 400, headers

    if orderBy not in TABLE_COLUMNS:
        return {"error": "bad query parameter: `orderBy`"}, 400, headers

    if order == "ascending":
        order = "ASC"
    elif order == "descending":
        order = "DESC"
    else:
        return {"error": "bad query parameter: `order`."}, 400, headers

    if not limit.isdigit():
        return {"error": "bad query parameter: `limit`."}, 400, headers

    if not isTimestampValid(timestampFrom):
        return {"error": "bad query parameter: `from`."}, 400, headers

    if not isTimestampValid(timestampTo):
        return {"error": "bad query parameter: `to`."}, 400, headers

    activityData = db.execute(
        """
        SELECT {fields} from activity_data

        /* see https://www.sqlite.org/lang_datefunc.html */
        WHERE actStart >= DATETIME('{tsFrom}') AND actStart <= DATETIME('{tsTo}')
        ORDER BY {orderBy} {order}
        LIMIT {limit}
        ;
        """.format(
            fields=fields,
            orderBy=orderBy,
            order=order,
            tsFrom=timestampFrom,
            tsTo=timestampTo,
            limit=limit,
        )
    )

    # fetchall() returns a list of SQL ROW objects.
    # Create a dictionary with key "rows" that contain a list of dict
    # that each represent a row in the table.

    queryData = {}
    queryKeys = fieldsList
    for key in queryKeys:
        queryData[key] = []
        # queryData[key] = [dict(row)[key] for row in activityData.fetchall()]

    for row in activityData.fetchall():
        for key in queryKeys:
            queryData[key].append(dict(row)[key])

    return {"error": "", "result": queryData}, 200, headers


@app.route("/data/", methods=["GET"])
def getActivities():
    period = request.args.get("period")
    dateFilter = parsePeriod(period)

    activityData = db.execute(
        """
        SELECT *
        FROM activity_data
        WHERE actStart > STRFTIME('%Y-%m-%d %H:%M:%f',
            'now', 'localtime', {df})
        """.format(
            df=dateFilter
        )
    )

    # fetchall() returns a list of SQL ROW objects.
    # Creates a dictionary with key "rows" that contain a list of dict
    # that each represent a row in the table.
    queryData = {}

    queryKeys = ["actStart", "actEnd", "inactDuration", "processName", "windowName"]
    for key in queryKeys:
        queryData[key] = []
        # queryData[key] = [dict(row)[key] for row in activityData.fetchall()]

    for row in activityData.fetchall():
        for key in queryKeys:
            queryData[key].append(dict(row)[key])

    headers = {"Access-Control-Allow-Origin": "*"}
    statusCode = 200

    return queryData, statusCode, headers


@app.after_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/", methods=["GET"])
def index():
    """
    Serve the dashboard at /
    """
    return redirect("/index.html")


def parsePeriod(period):
    # Returns modifiers for the DATETIME() sqlite function.
    # This should be a switch statement but only python >=3.10 supports it
    if period == "24h":
        return "'-24 hours'"
    elif period == "3d":
        return "'-3 days'"
    elif period == "7d":
        return "'-7 days'"
    elif period == "1M":
        return "'-1 months'"
    elif period == "3M":
        return "'-3 months'"
    elif period == "6M":
        return "'-6 months'"
    elif period == "1Y":
        return "'-1 years'"
    elif period == "all":
        return "'-50 years'"
    else:
        return "'start of day'"

def isTimestampValid(timestamp):
    if timestamp == 'now':
        return True
    else:
        # A non try/except way would be better...
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            return True
        except:
            return False


