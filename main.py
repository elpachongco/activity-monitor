from src.uploader import Uploader
from src.tracker import Tracker
from scripts.make_db import createDB

import os
from dotenv import load_dotenv

#from config.keywords import IGNORES, CENSORS

from pathlib import Path
import logging

from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

def main():
	load_dotenv()
	logger = setupLogger()

	DB_NAME = os.getenv("DB_NAME") or "activity.sqlite"
	DB_PATH = str(Path.cwd() / DB_NAME)
	TABLE_NAME = os.getenv("TABLE_NAME") or "activity_data"

	# Create new db if it doesn't exist.
	createDB(DB_PATH, TABLE_NAME)

	tracker = Tracker()
	logger.info("Activity Database at %s", DB_PATH)
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
		with Uploader(DB_PATH, TABLE_NAME) as uploader:
			uploader.upload(activity)

		# No limiter for while loop, since tracker.track() is blocking and will
		# stop the loop while user is focused on the same window.

def setupLogger():
	format = "%(asctime)s %(filename)s: %(levelname)s %(message)s"
	formatter = Formatter(format)
	level = logging.DEBUG

	logger = logging.getLogger()

	logger.setLevel(level)
	handler = TimedRotatingFileHandler(filename='logs/tracker.log', when='H', interval=48, backupCount=3)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger

if __name__ == "__main__":
	main()
