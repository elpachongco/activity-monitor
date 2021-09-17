from flask import Flask, request, Response, make_response
import sqlite3
app = Flask(__name__)

# This program receives GET requests from the frontend, queries the database
# then responds in JSON (python dictionary)
# 
# running (windows):
# $ pipenv run flask run --host=0.0.0.0

dbPath = '../../activity.db'
db = sqlite3.connect(dbPath, check_same_thread=False)
db.row_factory = sqlite3.Row

@app.route('/data/', methods=['GET'])
def getActivity():

    period = request.args.get('period')
    dateFilter = parsePeriod(period)

    # print(dateFilter)
    activityData = db.execute("""
        SELECT *
        FROM activity_data 
        WHERE actStart > STRFTIME('%Y-%m-%d %H:%M:%f', 
            'now', 'localtime', {df})
        ORDER BY actStart DESC
    """.format(
       df=dateFilter 
    ))

    # fetchall() returns a list of SQL ROW objects. 
    # Creates a dictionary with key "rows" that contain a list of tuples
    # that each represent a row in the table.
    queryData = {"rows": 
        [tuple(row) for row in activityData.fetchall()]
    }

    # response = make_response(queryData)
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # return response

    #### return DATA, STATUS CODE, Dictionary of headers
    return queryData, 200, {'Access-Control-Allow-Origin': '*'}

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
    elif period == 'All':
        return "'-50 years'"