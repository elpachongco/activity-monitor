#! /usr/bin/env python3
import webbrowser
import os
from subprocess import Popen
from pathlib import Path

runFlaskCmd = ["poetry", "run", "flask", "run", "-p", "9000", "--host", "0.0.0.0"]
# change working directory (cwd), run flask
Popen(runFlaskCmd, cwd="./client/")

webbrowser.open("http:\\\localhost:9000")
