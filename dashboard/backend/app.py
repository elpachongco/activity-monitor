from flask import Flask 
import sqlite3

"""
This program receives GET requests from the frontend, queries the database
then responds in JSON

running (windows):
$ pipenv run flask run --host=0.0.0.0
"""


dbPath = '../activity.db'

app = Flask(__name__)

db = sqlite3.connect(dbPath, check_same_thread=False)
db.row_factory = sqlite3.Row

@app.route('/')
def getActivity():
    # Return a json response of the db

    activityData = db.execute("""
        SELECT * FROM activity_data 
    """)

    print(activityData.description)

    return "success"

    # Return query as dictionary 
    # Flask will auto format it as JSON