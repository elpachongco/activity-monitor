import time, threading, logging
from config.keywords import IGNORES, CENSORS

from src.uploader import Uploader 

from src.tracker import Tracker

#threadObj = threading.Thread(target=startProgram, args=[logger])
#threadObj.setDaemon(True)
#threadObj.start()

uploader = Uploader()
tracker = Tracker()

while True:
	# Get current date (day)
	# thisDay = time.localtime(time.time()).tm_mday

	# Get start time
	tStart = time.time()

	# call function: list tracker.track()
	# ARGS: 
	# RETURN: float/int Inactivity duration, str Process name, str Window name
	activInfo = tracker.track()
	print("returned to main")
	# Get total duration of activity
	tDuration = time.time() - tStart

	# Call function: None uploader.upload()
	# ARGS: int start time, int end time, int inactivity, str process name, str window name
	# RETURN: None
	uploader.upload(activInfo)