#! /usr/bin/env python3
import webbrowser
import os
from subprocess import Popen
from pathlib import Path

runFlaskCmd = ["pipenv", "run", "flask", "run", "-p" ,"5000", "--host", "0.0.0.0"]
# change working directory (cwd), run flask
Popen(runFlaskCmd, cwd="./client/")

webbrowser.open("http:\\\localhost:5000")