import ctypes, time, os, csv, logging, sys
from ctypes import wintypes, windll, create_unicode_buffer, byref
# ctypes handles some of Windows-specific functions
import ezsheets as ezsh, shelve   # googlesheets api wrapper

# Create the spreadsheet
sharedVariable = shelve.open("sharedVariable", "r")
spreadsheetID = sharedVariable["spreadsheetID"]  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Create the spreadsheet object
currentdaySheet = sharedVariable['currentdaySheet'] 
sharedVariable.close()

# Get values from the sharedVariable
with shelve.open("sharedVariable", flag="c") as sharedVariable:
	sharedVariable['runLogger'] = True
	windowChangeCount = sharedVariable['windowChangeCount'] 

# Extracts ignorelist and censorlist from keywordList.txt 
def getKeywordList():
	ignore = []
	censor = []
	with open("keywordList.txt") as keywordList:
		keywordList = keywordList.readlines()
	isIgnore = False
	isCensor = False
	for index, item in enumerate(keywordList):
		item = item.rstrip(" \n").lstrip().lower()
		if item != '':
			if item[0] == '#':
				if "ignore" in item:
					isIgnore = True
					isCensor = False
					continue
				elif "censor" in item:
					isIgnore = False
					isCensor = True
					continue
				elif "ignore" or "censor" not in item:
					continue
			if isIgnore == True:
				ignore.append(item)
			elif isCensor == True:
				censor.append(item)
	return ignore, censor   # List

# Basic logging
logging.basicConfig(format='%(asctime)s \n %(message)s', filename='app.log', filemode= 'w', encoding='utf-8', level=logging.INFO)


def writeToSpreadsheet(spreadSheetDict, column, row, inputDict ): 
	# spreadSheetDict accepts currentDaySS Dictionary
	# inputDict accepts activityDict
	spreadsheet = spreadSheetDict["spreadsheetObj"]
	spreadsheet = spreadsheet[spreadSheetDict["sheet"]]
	row = str(row)

	# there's probably a better way to do this
	spreadsheet[cellColumn["startTime"] + row] = str(inputDict["actStart"])
	spreadsheet[cellColumn["endTime"] + row] = str(inputDict["actEnd"])
	spreadsheet[cellColumn["inactiveTime"] + row] = str(inputDict["inactDuration"])
	spreadsheet[cellColumn["programName"] + row] = str(inputDict["processName"])
	spreadsheet[cellColumn["windowName"] + row] = str(inputDict["windowName"])

class LASTINPUTINFO(ctypes.Structure):
	# Special class for storing lastinputinfo data from windows
	_fields_ = [
		("cbSize", ctypes.c_ulong),
		("dwTime", ctypes.c_ulong) ]
lastInputInfo = LASTINPUTINFO()  # Instantiate class
lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   # set size of class - microsoft requirement

def getActivityInfo():
	# Get information on current active/foreground window. 
	h_wnd = windll.user32.GetForegroundWindow()   # foreground window unique ID for each window independent of app - HWND
	length = windll.user32.GetWindowTextLengthW(h_wnd)  # get length of title of said window
	buf = create_unicode_buffer(length + 1)   # Create a buffer to put the title on (function requirement)
	windll.user32.GetWindowTextW(h_wnd, buf, length + 1) # function returns result to variable buf (buffer)
	pid = wintypes.DWORD()   # creates a dword type variable to store the process ID of the window
	windll.user32.GetWindowThreadProcessId(h_wnd, byref(pid)) # Function stores the PID of the specified window to pid.
	
	# Run a command and store output to var (CSV)
	processNameCSV = os.popen(f"tasklist /FI \"pid eq {pid.value}\" /FO CSV").read()  
	readCSV = csv.reader(processNameCSV)   # Read the CSVI
	listCSV = list(readCSV)   # Make it a list 
	exeName = listCSV[10][0]   # Position of the program name in the list 
	
	return str(buf.value), str(exeName)  # Return the window text, name of program running the window.

def userIsActiveCheck(timeGap): 
	# Decide whether user is inactive by comparing the inactivity time to accepted delay between last input time and current time
	timeGapTolerance = 800  # time in ms considered when deciding if gap means the user is active or not
	if timeGap <= timeGapTolerance:  
		return True
	elif timeGap > timeGapTolerance:
		return False

# Stores the spreadsheetObject and the sheet Object. Todo: Fix by using only the sheet object
currentDaySS = {"spreadsheetObj": spreadsheet, "sheet": currentdaySheet}

# Storage for current activity data
activityDict = {"processName": "", "windowName": "" , "actStart": "", "actEnd": "", "inactDuration": ""}

# Columns to put the data in 
cellColumn = {"startTime": "A", "endTime": "B", "inactiveTime": "E", "programName": "F", "windowName": "G"}

# Inactivity time data storage
inactivityTime = {"start": 0, "end": 0 }   # Every time user gets inactive, add current time to start.

activMinTime = .8  # min sec that must pass before action is considered an action.
cellEntryStartRow = 2  # what row the data will start to be entered  

activityDict["actStart"] = time.time()   # Called when the program starts.    

# Extract the ignoreList and censorList from keywordList.txt
ignoreList, censorList = getKeywordList()

# Variables that are used inside the while loop
currentWindowName = ''   # temp storage for window name data.
currentProcess = '' # Same as above but for process name
totalInactDuration = 0 # Stores inactivity computation
totalWindowDuration = 0 # Same as above but for window duration
userAwake = False   # user Awake is when the user goes from being inactive to active

# This allows the activity logger to be controlled by the main_app
sharedVariable = shelve.open("sharedVariable", flag="r")
while sharedVariable['runLogger'] == True:  # == True
	sharedVariable.close()
	# Detects user Inactivity
	windll.user32.GetLastInputInfo(byref(lastInputInfo))   # Store last input time to class
	lastInputTime = lastInputInfo.dwTime   # Access last input time - then store to var
	tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison against last input time
	userIsActive = userIsActiveCheck(tickCount-lastInputTime)  
	currentWindowName, currentProcess = getActivityInfo()

	# Logs time of user inactivity 
	if not userIsActive:
		if userAwake == False:
			inactivityTime["start"] += time.time()
			userAwake = True
	elif userIsActive:
		if userAwake == True:   # 
			inactivityTime["end"] += time.time()  # when user awakes, inactivity ends
			userAwake = False  # User should first be inactive before awakening again

	# When the program is ran for the first time, windowName is = ""
	if activityDict["windowName"] != '':    
		# Window change
		if currentWindowName != activityDict["windowName"]: 

			# Handles the missing end time when the user is inactive and a change of window occurs (e.g. waiting for a webpage to load)
			if userAwake == True:
					inactivityTime["end"] += time.time()
					userAwake = False 

			activityDict["actEnd"] = time.time()                    
			totalWindowDuration = activityDict["actEnd"] - activityDict["actStart"]            

			# Don't execute if the window change is less than activMinTime 
			if totalWindowDuration  >= activMinTime: 
					cellNumber = str(windowChangeCount + cellEntryStartRow)

					totalInactDuration = str(inactivityTime["end"] - inactivityTime["start"])
					activityDict["inactDuration"] = totalInactDuration

					# Censoring, not so elegant solution. Feels like there should be a better way to this...
					for item in censorList:
						if item in activityDict["windowName"].lower():
							activityDict["windowName"] = "[redacted]" # hehe
							# Use this instead if you want to uncensor the first letter   
							# activityDict["windowName"] = str(activityDict["windowName"])[0] + "[redacted]" 

					ignoreActivity = False
					for item in ignoreList:  # Only write if to spreadsheet if it doesn't contain ignore words
						if item in activityDict["windowName"].lower():
							ignoreActivity = True

					if ignoreActivity == False:
						writeToSpreadsheet(currentDaySS, cellColumn , windowChangeCount + cellEntryStartRow , activityDict)
						windowChangeCount += 1   

						# Save this so that it can be referenced when program shuts down unexpectedly
						with shelve.open("sharedVariable", flag="c") as sharedVariable:
							sharedVariable['windowChangeCount'] = windowChangeCount

						# Logging purpose. Disable this if you don't want the program to put your activity on the logs
						logging.info("FStart: " + str(inactivityTime["start"])  +"\nFEnd: " + str(inactivityTime["end"]) + f"\ntotal Inactivity: {totalInactDuration}" + "\n" + '='*12 + "\n")
					
					activityDict["actStart"] = time.time()  # Set a new start time for the new activity
									
					inactivityTime["start"] = 0     
					inactivityTime["end"] = 0

	activityDict["windowName"] = currentWindowName
	activityDict["processName"] = currentProcess   

	# After a loop, read sharedVariable again
	sharedVariable = shelve.open("sharedVariable", flag="r")
	
# Else
sharedVariable.close() # Shelf will remain open when the while loop ends

with shelve.open("sharedVariable", flag="c") as sharedVariable:
	sharedVariable['windowChangeCount'] = 0

# sys.exit()