import time, os, sys, threading
import shelve

programRunStart = time.localtime(time.time()).tm_mday # Returns date (day)

spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ" 

# Worksheet names
currentdaySheet = "Today's Activity Log" 
archiveSheet = "Previous Activity Data"
calculationSheet = "Calculations"

# python program names
actLoggerFileName = "activitylogger.py"
eodArchiverFileName = "eodArchiver.py"

# Establish sharedVariable which will contain data for sharing to the other applications
with shelve.open("sharedVariable", flag="c") as sharedVariable:
	# Store the spreadsheet information so that it's just in one place  
	sharedVariable['spreadsheetID'] = spreadsheetID
	sharedVariable['currentdaySheet'] = currentdaySheet
	sharedVariable['archiveSheet'] = archiveSheet
	sharedVariable['calculationSheet'] = calculationSheet
	
	# Handles the program's ability to continue stuff after shutdowns
	if 'dayNumber' not in sharedVariable:
		sharedVariable['dayNumber'] = 0 
	if 'windowChangeCount' not in sharedVariable:
		sharedVariable['windowChangeCount'] = 0

	# Handles the -clear argument
	if len(sys.argv) > 1:
		if sys.argv[1].upper() == '-CLEAR':
			sharedVariable['dayNumber'] = 0 
			sharedVariable['windowChangeCount'] = 0


	dayNumber = sharedVariable['dayNumber']

def startProgram(pyFileName):
	# Takes in file names of python programs
	os.system('py ' + str(pyFileName))   # not sure if this would work on other windows systems
	print("start program:" + str(pyFileName) + " - done")

# Necessary for  the program to continue running even when activity logger is running
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
		elif errorQuestion.upper() == "B":
			continue  
		sys.exit()