import time, threading, logging
from config.keywordList import IGNORES, CENSORS
# from config.config import 

from src.uploader import upload 
# Uploads data to sqlite db

from src.tracker import track

#threadObj = threading.Thread(target=startProgram, args=[logger])
#threadObj.setDaemon(True)
#threadObj.start()

while True:
	# Get current date (day)
	thisDay = time.localtime(time.time()).tm_mday

	# Get start time
	start = time.time()

	# call function: list getActivity()
	# ARGS: 
	# RETURN: float/int Inactivity duration, str Process name, str Window name

	# Get end time
	end = time.time()

	# Call function: None upload()
	# ARGS: int start time, int end time, int inactivity, str process name, str window name
	# RETURN: None