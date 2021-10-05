#! /usr/bin/env python3
''' 
Starts the dashboard. 
Runs flask & Starts the browser 
'''

import webbrowser
import os
from subprocess import Popen
from pathlib import Path

## SET Environment variables
#flaskProgramLocation = Path.cwd() / 'backend' / 'app.py'
#os.environ["FLASK_APP"] = str(flaskProgramLocation)

# change working directory (cwd), run flask
runFlaskCmd = ["pipenv", "run", "flask", "run", "-p" ,"5000"]
Popen(runFlaskCmd, cwd="./backend/")

# open index.html
#indexPage = Path.cwd() / 'frontend'/ 'index.html'

#webbrowser.open("http:\\\localhost:5000")
