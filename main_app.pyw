# This python script controls the whole program. 
# Responsible for initiating the programs
# The aim is for this program to run continuously
import time, os, sys
import shelve
import threading

programRunStart = time.localtime(time.time()).tm_mday # Returns date (day)
# programRunStart = time.localtime(time.time()).tm_min + time.localtime(time.time()).tm_hour  # Temporary

spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ" 

# Worksheet names
currentdaySheet = "Today's Activity Log" 
archiveSheet = "Previous Activity Data"
calculationSheet = "Calculations"

# python program names
actLoggerFileName = "activitylogger.py"
eodArchiverFileName = "eodArchiver.py"

# This is here so that the common spreadsheet data (id & stuff) is just in one place
# Store the data to a shelf, this will overwrite any data written on the shelf
# Everytime this program starts, everything will get deleted.
# The goal is for this tool to be running non stop

with shelve.open("sharedVariable", flag="c") as sharedVariable:
	sharedVariable['spreadsheetID'] = spreadsheetID
	sharedVariable['currentdaySheet'] = currentdaySheet
	sharedVariable['archiveSheet'] = archiveSheet
	sharedVariable['calculationSheet'] = calculationSheet
	if 'dayNumber' not in sharedVariable:
		sharedVariable['dayNumber'] = 0 
	if 'windowChangeCount' not in sharedVariable:
		sharedVariable['windowChangeCount'] = 0

	if len(sys.argv) > 1:
		if sys.argv[1].upper() == '-CLEAR':
			sharedVariable['dayNumber'] = 0 
			sharedVariable['windowChangeCount'] = 0
	
	dayNumber = sharedVariable['dayNumber']
	#  sharedVariable['dayNumber'] = 
	sharedVariable['runLogger'] = True    

def startProgram(pyFileName):
	os.system('py ' + str(pyFileName))   # not sure if this would work on other windows systems
	print("start program:" + str(pyFileName) + " - done")

# Start logger in a separate thread
threadObj = threading.Thread(target= startProgram, args=[actLoggerFileName])
threadObj.start()

previousDay = programRunStart 
while True:
	try:
		# Get current date (day)
		thisDay = time.localtime(time.time()).tm_mday

		if thisDay != previousDay:  # Crude. Hope this doesn't mess things up.
			with shelve.open("sharedVariable", flag="c") as sharedVariable:
				sharedVariable['runLogger'] = False
				sharedVariable['windowChangeCount'] = 0
				sharedVariable['dayNumber'] += 1

			startProgram(eodArchiverFileName)

			threadObj = threading.Thread(target= startProgram, args=[actLoggerFileName])
			threadObj.start()

			previousDay = thisDay

	except:
		# Either continue the loop or exit the program
		errorQuestion = input("Continue running or exit? \nExit - a | Continue running - b\n")
		if errorQuestion.upper() == "A":
			sys.exit()
		if errorQuestion.upper() == "B":
			continue  
		sys.exit()