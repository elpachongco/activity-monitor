# NOTE -- plan
# When called, get window name, start time, track inactivities, 
# then return when user switches window 

import ctypes, time, os, csv, logging, sys
from ctypes import wintypes, windll, create_unicode_buffer, byref
# ctypes handles some of Windows-specific functions

# TODO -- 
# Currently, this program tries to 1. Get ignore keywords, 2. See user activity, 
# and 3. upload to a DB (sheets). 
# This has to be removed. functions should be separated into different 
# programs that do its own purpose 

# TODO  
# implement sampling interval for the while loop

def getKeywordList():
	# args: None
	# returns: list of ignores, list of censors
	pass

#def writeToSpreadsheet(spreadSheetDict, column, row, inputDict ): 

class LASTINPUTINFO(ctypes.Structure):
	# Special class for storing lastinputinfo data from windows
	_fields_ = [
		("cbSize", ctypes.c_ulong),
		("dwTime", ctypes.c_ulong) ]

def getActivityInfo():
	# Get current active/foreground window. 
	# RETURNS: str name of window, str name of process

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

def getUserIsActive(timeGap): 
	# Decide whether user is inactive by comparing the                                             
	# inactivity time to accepted delay between last input 
	# time and current time
	timeGapTolerance = 800  # time in ms considered when deciding if gap means the user is active or not
	if timeGap <= timeGapTolerance:  
		return True
	elif timeGap > timeGapTolerance:
		return False

# Inactivity time data storage
ACTIVMINTIME = .8  # min sec that must pass before action is considered an action.

class Tracker():
	# Get foreground window, track inactivity. Return when window changes
	
	activity = {"processName": "", "windowName": "" , "actStart": 0.0, "actEnd": 0.0, "inactDuration": ""}

	whileInterv = 0.2

	def __init__(self):
		self.lastInputInfo = LASTINPUTINFO()  
		self.lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   
	
	def track(self): 

		print("started on tracker")
		currentWindowName = '' # temp storage for window name.
		currentProcess = '' 
		totalWindowDuration = 0 
		userFromSleep = False   # user Awake is when the user goes from being inactive to active
		inactiveDur = {"start": 0, "end": 0 }   # Every time user gets inactive, add current time to start.

		self.activity['actStart'] = time.time()

		while True:  
			
			time.sleep(self.whileInterv)

			# Detects user Inactivity
			windll.user32.GetLastInputInfo(byref(self.lastInputInfo))   # Store last input time to class
			lastInputTime = self.lastInputInfo.dwTime   # Access last input time - then store to var
			tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison against last input time
			userIsActive = getUserIsActive(tickCount-lastInputTime)  
			currentWindowName, currentProcess = getActivityInfo()

			# Logs time of user inactivity 
			if not userIsActive:
				if not userFromSleep:
					inactiveDur["start"] += time.time()
					userFromSleep = True
			else:
				if userFromSleep:   # 
					inactiveDur["end"] += time.time()  # when user awakes, inactivity ends
					userFromSleep = False  # User should first be inactive before awakening again

			# When the program is ran for the first time, windowName is = ""
			if self.activity["windowName"] != '':    
				if currentWindowName != self.activity["windowName"]: 

					if userFromSleep:
						# Handles the missing end time when the user is inactive 
						# and a change of window occurs (e.g. when waiting for a 
						# webpage to load, the windowName is "New Tab", which
						# changes when the page loads)

						inactiveDur["end"] += time.time()
						userFromSleep = False 

					self.activity["actEnd"] = time.time()                    
					totalWindowDuration = self.activity["actEnd"] - self.activity["actStart"]            

					if totalWindowDuration >= ACTIVMINTIME: 

						self.activity["inactDuration"] = str(inactiveDur["end"] - inactiveDur["start"])

						inactiveDur["start"] = 0     
						inactiveDur["end"] = 0
						print("end")

						break

			self.activity["windowName"] = currentWindowName
			self.activity["processName"] = currentProcess   

		return self.activity