import time, threading, logging
from config.keywords import IGNORES, CENSORS

from src.uploader import Uploader 
from src.tracker import Tracker

uploader = Uploader()
tracker = Tracker()

while True:

	# call method: tracker.track()
	# ARGS: 
	# RETURN: Py Dictionary with String values, and keys: 
	#	{"processName": , "windowName": "actStart": ,
	#	"actEnd": , "inactDuration":}
	activInfo = tracker.track()

	# Call method: None uploader.upload()
	# ARGS: Python Dictionary returned by tracker.track(). Must have keys:
	# 		"procesName", "windowName", "actStart", "actEnd", "inactDuration".
	#		All values must be a string.
	# RETURN: None
	uploader.upload(activInfo)