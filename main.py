from src.uploader import Uploader 
from src.tracker import Tracker

from config.keywords import IGNORES, CENSORS
from os import environ
from pathlib import Path

# set environment variable "ACTIVITY_DB" 
# to path of activity.db
environ["ACTIVITY_DB"] = Path.cwd() / "activity.db"

uploader = Uploader()
tracker = Tracker()

while True:

	# call method: tracker.track()
	# ARGS: 
	# RETURN: Py Dictionary with String values, and keys: 
	#	{"processName": , "windowName": "actStart": ,
	#	"actEnd": , "inactDuration":}
	activity = tracker.track()

	# Call method: None uploader.upload()
	# ARGS: Python Dictionary returned by tracker.track(). Must have keys:
	# 		"procesName", "windowName", "actStart", "actEnd", "inactDuration".
	#		All values must be a string.
	# RETURN: None
	uploader.upload(activity)
