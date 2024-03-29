from collections import defaultdict
import json
import logging
import sqlite3
from datetime import datetime
from logging import Formatter

from logging.handlers import TimedRotatingFileHandler

from flasgger import Swagger
from flask import Flask, redirect, render_template, request

format = "%(asctime)s %(filename)s: %(levelname)s %(message)s"
formatter = Formatter(format)
level = logging.DEBUG

logger = logging.getLogger()
logger.setLevel(level)
handler = TimedRotatingFileHandler(
    filename="../../logs/server.log", when="H", interval=48, backupCount=3
)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__, static_folder="./Public/", static_url_path="")

# Setup swagger as the documentation generator.
# Documentation @ /apidocs
app.config["SWAGGER"] = {"title": "Activity Monitor API"}
swagger = Swagger(app)

# Path to sqlite database
dbPath = "../../activity.sqlite"

# open a read-only connection to the db using uri
# Allow connection as a non-creator of db
db = sqlite3.connect("file:" + dbPath + "?mode=ro", check_same_thread=False, uri=True)

db.row_factory = sqlite3.Row

DB_TABLE_COLUMNS = [
    "startMS",
    "endMS",
    "lengthMS",
    "idleMS",
    "windowName",
    "processName",
]


@app.route("/api/activities/latest", methods=["GET"])
def activities():
    """Get the latest activity from database.
    ---
    parameters:
        - name: limit
          description: limit number of results
          in: query
          type: integer
          default:
                1
          example:
                limit=1

    responses:
        200:
            description: Successful request. Error property will contain a
                blank string `\"\"`.
            schema:
                $ref: '#/definitions/SuccessfulResponse'

        400:
            description: Bad request. Error property will contain a message string.
            schema:
                $ref: '#/definitions/ErrorResponse'
    """
    headers = {"Access-Control-Allow-Origin": "*"}

    limit = request.args.get("limit") or "1"
    if not limit.isdigit():
        return {"error": "Limit should be a digit.", "result": {}}, 400

    activityData = db.execute(
        """
        SELECT * FROM activity_data ORDER BY startMS DESC LIMIT {limit};
        """.format(
            limit=limit
            )
    )

    a = defaultdict(list)
    for row in activityData:
        [a[key].append(row[key]) for key in row.keys()]

    return {"error": "", "result": a}, 200, headers


@app.route("/api/activities/interval/all", methods=["GET"])
def interval_total():
    """Aggregate activities by interval
    ---
    parameters:
        - name: interval
          in: query
          description: Interval to apply the method to.
            Determines the grouping of the intervals.
            minute (%M) -- groups data by minute only
            i.e. This will group august 3 2023 8:04am and any other time at minute 4.
            minute-day (%M-%H) -- groups data by minute and day of month (00-31).
            i.e. This will group august 3 2023 8:04am and january 3 2023 12:04pm.

            Below is a list containing the possible values and their sqlite datetime
            selector.

            ```
            [('minute', '%M'), ('minute-hour', '%M-%H'), ('minute-day', '%M-%d'),
            ('minute-month', '%M-%m'), ('minute-year', '%M-%Y'), ('hour', '%H'),
            ('hour-yearday', '%H-%j'), ('hour-weekday', '%H-%w'),
            ('hour-monthday', '%H-%d'), ('hour-month', '%H-%m'), ('hour-year', '%H-%Y'),
            ('day', '%d'), ('day-week', '%w'), ('day-year', '%j'), ('month', '%m')]
            ```
            See strftime values `https://www.sqlite.org/lang_datefunc.html`
          default: day
          enum: ['minute', 'minute-hour', 'minute-day', 'minute-month', 'minute-year',
                 'hour', 'hour-yearday', 'hour-weekday', 'hour-monthday', 'hour-month',
                 'hour-year', 'day', 'day-week', 'day-year', 'month']

        - name: method
          in: query
          enum: [sum, avg, count, max, min]

        - name: order
          in: query
          default: ascending
          enum: [descending, ascending]

        - name: order-by
          in: query
          enum: [lengthMinutes, interval, idleMinutes]

    """

    headers = {"Access-Control-Allow-Origin": "*"}

    method = request.args.get("method") or "sum"
    if method not in ["sum", "avg", "count", "max", "min"]:
        return {"error": "Invalid method", "result": {}}, 400, headers

    order = request.args.get("order") or "ascending"
    if order not in ["ascending", "descending"]:
        return {"error": "Invalid order", "result": {}}, 400, headers
    order = "ASC" if order == "ascending" else "DESC"

    orderBy = request.args.get("order-by") or "interval"
    if orderBy not in ["lengthMinutes", "interval", "idleMinutes"]:
        return {"error": "Invalid orderBy", "result": {}}, 400, headers

    validIntervals = {
        "minute": "%M",
        "minute-hour": "%M-%H",
        "minute-day": "%M-%d",
        "minute-month": "%M-%m",
        "minute-year": "%M-%Y",
        "hour": "%H",
        "hour-yearday": "%H-%j",
        "hour-weekday": "%H-%w",
        "hour-monthday": "%H-%d",
        "hour-month": "%H-%m",
        "hour-year": "%H-%Y",
        "day": "%d",
        "day-week": "%w",
        "day-year": "%j",
        "month": "%m",
    }

    interval = request.args.get("interval") or "day"
    if interval not in validIntervals.keys():
        return {"error": "Invalid interval", "result": {}}, 400, headers

    interval = validIntervals[interval]

    activityData = db.execute(
        """
        SELECT
        STRFTIME('{interval}', startMS/1000, 'unixepoch', 'localtime') as interval,
        CAST({agg}(lengthMS)as REAL) / 1000 / 60 as lengthMinutes,
        CAST({agg}(idleMS) as REAL) / 1000 / 60 as idleMinutes
        FROM activity_data
        GROUP BY STRFTIME('{interval}', startMS / 1000, 'unixepoch', 'localtime')
        ORDER BY {orderBy} {order}
        """.format(
            agg=method,
            interval=interval,
            order=order,
            orderBy=orderBy
        )
    )

    a = defaultdict(list)
    for row in activityData:
        [a[key].append(row[key]) for key in row.keys()]

    return {"error": "", "result": a}, 200, headers


@app.route("/api/activities/filter", methods=["GET"])
def filter_activities():
    """Get and filter activities from database.
    ---
    parameters:
        - name: order-by
          description: Column to base ordering on
          in: query
          type: string
          enum: ["startMS", "endMS", "lengthMS", "idleMS", "windowName", "processName"]
          default:
                startMS
          example:
                order-by=idleMS

        - name: order
          description: Type of ordering
          in: query
          type: string
          enum: [ascending, descending]
          default:
            ascending
          example:
                order=ascending

        - name: fields
          description: Which fields to return
          in: query
          type: array
          items:
            type: string
          minItems: 0
          maxItems: 5
          uniqueItems: true
          enum: ["startMS", "endMS", "lengthMS", "idleMS", "windowName", "processName"]
          default:
                ["startMS", "endMS", "lengthMS", "idleMS", "windowName", "processName"]
          example:
                fields=startMS,endMS,idleMS

        - name: timestamp-start
          description: ISO8601 timestamp to retrieve data from or "now".
          in: query
          type: string
          default:
                'now'
          example:
                timestamp-start=2023-07-23T11:36:01.111

        - name: timestamp-end
          description: ISO8601 timestamp to retrieve data to  or "now".
          in: query
          type: string
          default:
                'now'
          example:
                timestamp-end=2023-07-23T11:36:01.111

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
    orderBy = request.args.get("order-by") or "startMS"
    order = request.args.get("order") or "ascending"
    fields = request.args.get("fields") or ",".join(DB_TABLE_COLUMNS)
    timestampFrom = request.args.get("timestamp-start") or "now"
    timestampTo = request.args.get("timestamp-end") or "now"
    limit = request.args.get("limit") or "1"

    # Separate fields by comma, turn it to array
    fieldsList = fields.split(",")

    # ---------- Query param validation
    if orderBy not in DB_TABLE_COLUMNS:
        return (
            {
                "error": f"Query parameter: `orderBy` should be one of DB_TABLE_COLUMNS.\
                        DB_TABLE_COLUMNS: {DB_TABLE_COLUMNS}"
            },
            400,
            headers,
        )

    if order == "ascending":
        order = "ASC"
    elif order == "descending":
        order = "DESC"
    else:
        return (
            {
                "error": "Query parameter: `order` should either be 'ascending' or \
                        'descending'."
            },
            400,
            headers,
        )

    # make all items of fieldsList unique with set
    # See if all the items of fieldsList are all DB_TABLE_COLUMNS
    if not len(set(fieldsList).difference(DB_TABLE_COLUMNS)) == 0:
        return (
            {
                "error": f"Query parameter: `fields` should contain any of \
                        DB_TABLE_COLUMNS only. \
                        WANT: {DB_TABLE_COLUMNS} Got: {fieldsList}"
            },
            400,
            headers,
        )

    if not limit.isdigit():
        return {"error": "Query parameter: `limit` should be a digit."}, 400, headers

    if not isTimestampValid(timestampFrom):
        return (
            {
                "error": "Query parameter: `timestamp-start` should be 'now' or an \
                        IS08601 timestamp with the format %Y-%m-%dT%H:%M:%S.%f."
            },
            400,
            headers,
        )

    if not isTimestampValid(timestampTo):
        return (
            {
                "error": "Query parameter: `timestamp-end` should be 'now' or an \
                        IS08601 timestamp with the format %Y-%m-%dT%H:%M:%S.%f."
            },
            400,
            headers,
        )
    # ---------- xxxx

    # Return epoch MS fields as iso8601 timestamps
    queryFields = fieldsList.copy()
    for i, field in enumerate(fieldsList):
        if field in ["startMS", "endMS"]:
            # DATETIME(startMS / 1000, 'unixepoch') as field
            queryFields[i] = (
                "DATETIME(" + field + " / 1000,  'unixepoch', 'localtime') as " + field
            )

    activityData = db.execute(
        """
        SELECT {fields} from activity_data

        /* see https://www.sqlite.org/lang_datefunc.html */
        WHERE DATETIME(startMS/1000, 'unixepoch', 'localtime') >= DATETIME('{tsFrom}')
        AND DATETIME(startMS/1000, 'unixepoch', 'localtime') <= DATETIME('{tsTo}')
        ORDER BY {orderBy} {order}
        LIMIT {limit};
        """.format(
            fields=",".join(queryFields),
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


@app.route("/data", methods=["GET"])
def getActivities():
    """Old endpoint for dashboard
    ---
    parameters:
        - name: period
          description: Return data from now to this
          in: query
          type: string
          enum: [24h, 3d, 7d, 1M, 3M, 6M, 1Y, all]
          default:
                'start of day'
          example:
                period=24h

    responses:
        200:
            description: Successful request. Error property will contain a \
                    blank string `\"\"`.
            schema:
                $ref: '#/definitions/SuccessfulResponse'

        400:
            description: Bad request. Error property will contain a message string.
            schema:
                $ref: '#/definitions/ErrorResponse'
    """

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
        except ValueError:
            return False


@app.route("/dashboard")
def dashboard():
    val = 24
    return render_template("dashboard.html", val=json.dumps(val))
