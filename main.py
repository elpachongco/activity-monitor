from src.uploader import Uploader
from src.tracker import Tracker

from config.keywords import IGNORES, CENSORS

from os import environ
from pathlib import Path
import logging

logging.basicConfig(filename='server.log', level=logging.DEBUG, format="%(asctime)s %(filename)s: %(levelname)s %(message)s")

environ["ACTIVITY_DB"] = str(Path.cwd() / "activity.db")
tracker = Tracker()
logging.info("Setup done")
logging.info("Activity Database at %s", environ["ACTIVITY_DB"])

def main():
	logging.info("ran as application, main function loop started")
	while True:
		# call method: tracker.track()
		# ARGS: 
		# RETURN: Py Dictionary with String values, and keys: 
		#	{"processName": , "windowName": "actStart": ,
		#	"actEnd": , "inactDuration":}
		activity = tracker.track()
		#activity = {"processName": "test", "windowName": "test", "actStart":  "2023-01-01T00:00:00.000", "actEnd": "2023-01-01T00:00:00.000", "inactDuration":"0"}

		# Call method: None uploader.upload()
		# ARGS: Python Dictionary returned by tracker.track(). Must have keys:
		# 		"procesName", "windowName", "actStart", "actEnd", "inactDuration".
		#		All values must be a string.
		# RETURN: None
		with Uploader(environ["ACTIVITY_DB"]) as uploader:
			uploader.upload(activity)

		# No limiter for while loop, since tracker.track() is blocking and will
		# stop the loop while user is focused on the same window.


if __name__ == "__main__":
	main()
