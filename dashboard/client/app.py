from flask import Flask, request, Response, make_response, redirect
import sqlite3 
from pathlib import Path 

app = Flask(__name__, static_folder="./Public/", static_url_path="")

# This program receives GET requests from the frontend, queries the database
# then responds in JSON (python dictionary)
#
# Let SQL do the complicated computations 
# running (windows):
# $ pipenv run flask run --host=0.0.0.0
# Also set flask to dev mode (powershell)
# $env:FLASK_ENV="development"

# Path to sqlite database 
dbPath = "../../activity.db"

db = sqlite3.connect(dbPath, check_same_thread=False)
db.row_factory = sqlite3.Row

def parsePeriod(period):

    # Returns modifiers for the DATETIME() sqlite function.
    # This should be a switch statement but only python >=3.10 supports it
    if period == 'today':
        return "'start of day'"
    elif period == '24h':
        return "'-24 hours'"
    elif period == '3d':
        return "'-3 days'"
    elif period == '7d':
        return "'-7 days'"
    elif period == '1M':
        return "'-1 months'"
    elif period == '3M':
        return "'-3 months'"
    elif period == '6M':
        return "'-6 months'"
    elif period == '1Y':
        return "'-1 years'"
    elif period == 'all':
        return "'-50 years'"

@app.route('/data/', methods=['GET'])
def getActivities():

    period = request.args.get('period')
    dateFilter = parsePeriod(period)

    activityData = db.execute("""
        SELECT *
        FROM activity_data 
        WHERE actStart > STRFTIME('%Y-%m-%d %H:%M:%f', 
            'now', 'localtime', {df})
        """.format(
       df=dateFilter 
    ))

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
            queryData[key].append( dict(row)[key] )

    headers = {'Access-Control-Allow-Origin': '*'}
    statusCode = 200

    return queryData, statusCode, headers 

@app.route('/', methods=['GET'])
def index():
    return redirect('/index.html')