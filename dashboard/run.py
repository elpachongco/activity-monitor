#! python

''' 
Starts the dashboard. 
Runs flask & Starts the browser 
'''

import webbrowser
import os
from subprocess import Popen
from pathlib import Path

# SET Environment variables
flaskProgramLocation = Path.cwd() / 'backend' / 'app.py'
#os.environ["ACTIVITY_DB"] = str(
os.environ["FLASK_APP"] = str(flaskProgramLocation)

# Command and arguments as list 
runFlask = ["pipenv", "run", "flask", "run"]
# Run in a separate process
Popen(runFlask)

# Location of frontend index.html
indexPage = Path.cwd() / 'frontend'/ 'index.html'

webbrowser.open_new_tab("file:///" + str(indexPage))
