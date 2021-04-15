# This python script controls the whole program. 
# Responsible for initiating the programs
# The aim is for this program to run continuously
import time, os
import shelve
import threading

programRunStart = time.localtime(time.time()).tm_mday # Returns date (day)

spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ" 

# Worksheet names
currentdaySheet = "Today's Activity Log" 
archiveSheet = "Previous Activity Data"
calculationSheet = "Calculations"

# python program names
actLoggerFileName = "activitylogger.py"
eodArchiverFileName = "eodArchiver.py"


# This is here so that the common spreadsheet data (id & stuff) is just in one place
# Store the data to a shelf  
with shelve.open("sharedVariable", flag="c") as sharedVariable:
    sharedVariable['spreadsheetID'] = spreadsheetID
    sharedVariable['currentdaySheet'] = currentdaySheet
    sharedVariable['archiveSheet'] = archiveSheet
    sharedVariable['calculationSheet'] = calculationSheet
    sharedVariable['dayNumber'] = 0

def startProgram(pyFileName):
    os.system('py ' + str(pyFileName))   # not sure if this would work on other windows systems
    print("start program:" + str(pyFileName) + "done")


# The logger will need the 'runLogger' set to True
with shelve.open("sharedVariable", flag="c") as sharedVariable:
    sharedVariable['runLogger'] = True    

# Start logger in a separate thread
threadObj = threading.Thread(target= startProgram, args=[actLoggerFileName])
threadObj.start()

previousDay = programRunStart 
while True:
    # Get current date (day)
    thisDay = time.localtime(time.time()).tm_mday

    if thisDay > previousDay:  # It's a different day
        # Terminate the activity logger
        with shelve.open("sharedVariable", flag="c") as sharedVariable:
            sharedVariable['runLogger'] = False
            sharedVariable['dayNumber'] += 1

        # Record archival data, then reset the daily data columns
        startProgram(eodArchiverFileName)  # Threading is unnecesary

        # Turn the activity logger on again
        threadObj = threading.Thread(target= startProgram, args=[actLoggerFileName])
        threadObj.start()

        #Set the current day as the new previous day
        previousDay = thisDay