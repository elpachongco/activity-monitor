from flask import Flask, request, redirect
import sqlite3
from datetime import datetime
from flasgger import Swagger

# This program receives GET requests from the frontend, queries the database
# then responds in JSON (python dictionary)
#
# Let SQL do the complicated computations
# running (windows):
# $ pipenv run flask run --host=0.0.0.0
# Also set flask to dev mode (powershell) to enable hot reload
# $env:FLASK_ENV="development"

app = Flask(__name__, static_folder="./Public/", static_url_path="")

# Setup swagger as the documentation generator.
# Documentation @ /apidocs
app.config["SWAGGER"] = {"title": "Activity Monitor API"}
swagger = Swagger(app)

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
    """Get and filter activities from database.
    ---
    parameters:
        - name: order-by
          description: Column to base ordering on
          in: query
          type: string
          enum: [actStart, actEnd, inactDuration, windowName, processName]
          default:
                actStart
          example:
                fields=actStart,actEnd,inactDuration

        - name: order
          description: Type of ordering
          in: query
          type: string
          enum: [ascending, descending]
          default:
            ascending
          example:
                fields=actStart,actEnd,inactDuration

        - name: fields
          description: Which fields to return
          in: query
          type: array
          items:
            type: string
          minItems: 0
          maxItems: 5
          uniqueItems: true
          enum: [actStart,actEnd,inactDuration,windowName,processName]
          default:
                [actStart,actEnd,inactDuration,windowName,processName]
          example:
                fields=actStart,actEnd,inactDuration

        - name: timestamp-from
          description: ISO8601 timestamp to retrieve data from or "now".
          in: query
          type: string
          default:
                'now'
          example:
                timestamp-from=2023-07-23T11:36:01.111

        - name: timestamp-to
          description: ISO8601 timestamp to retrieve data to  or "now".
          in: query
          type: string
          default:
                'now'
          example:
                timestamp-to=2023-07-23T11:36:01.111

        - name: limit
          description: limit number of results
          in: query
          type: integer
          default:
                1
          example:
                limit=1

    definitions:
        SuccessfulResponse:
            type: object
            properties:
                error:
                    type: string
                result:
                    type: object
                    properties:
                        requested_field:
                            type: array
                            items:
                                type: string

        ErrorResponse:
            type: object
            properties:
                error:
                    type: string
                result:
                    type: object

    responses:
        200:
            description: Successful request. Error property will contain a blank string `\"\"`.
            schema:
                $ref: '#/definitions/SuccessfulResponse'

        400:
            description: Bad request. Error property will contain a message string.
            schema:
                $ref: '#/definitions/ErrorResponse'
    """

    headers = {"Access-Control-Allow-Origin": "*"}

    # Get query params. If not present, use default.
    orderBy = request.args.get("order-by") or "actStart"
    order = request.args.get("order") or "ascending"
    fields = request.args.get("fields") or ",".join(TABLE_COLUMNS)
    timestampFrom = request.args.get("timestamp-from") or "now"
    timestampTo = request.args.get("timestamp-to") or "now"
    limit = request.args.get("limit") or "1"

    # Separate fields by comma, turn it to array
    fieldsList = fields.split(",")

    # ---------- Query param validation
    if orderBy not in TABLE_COLUMNS:
        return {"error": "bad query parameter: `orderBy`"}, 400, headers

    if order == "ascending":
        order = "ASC"
    elif order == "descending":
        order = "DESC"
    else:
        return {"error": "bad query parameter: `order`."}, 400, headers

    # make all items of fieldsList unique with set
    # See if all the items of fieldsList are all TABLE_COLUMNS
    if not len(set(fieldsList).difference(TABLE_COLUMNS)) == 0:
        return {"error": "bad query parameter: `fields`"}, 400, headers

    if not limit.isdigit():
        return {"error": "bad query parameter: `limit`."}, 400, headers

    if not isTimestampValid(timestampFrom):
        return {"error": "bad query parameter: `from`."}, 400, headers

    if not isTimestampValid(timestampTo):
        return {"error": "bad query parameter: `to`."}, 400, headers
    # ---------- xxxx

    activityData = db.execute(
        """
        SELECT {fields} from activity_data

        /* see https://www.sqlite.org/lang_datefunc.html */
        WHERE actStart >= DATETIME('{tsFrom}') AND actStart <= DATETIME('{tsTo}')
        ORDER BY {orderBy} {order}
        LIMIT {limit};
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
    if timestamp == "now":
        return True
    else:
        # A non try/except way would be better...
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            return True
        except:
            return False
