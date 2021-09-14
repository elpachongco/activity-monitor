import ctypes, time, os, csv, logging, sys
from ctypes import wintypes, windll, create_unicode_buffer, byref
from datetime import datetime
# ctypes handles the Windows-specific functions

class LASTINPUTINFO(ctypes.Structure):
	# Special class for storing lastinputinfo data from windows
	_fields_ = [
		("cbSize", ctypes.c_ulong),
		("dwTime", ctypes.c_ulong) ]

def getActivityInfo():
	# Get window name and process name of current foreground window
	# Makes use of windows API
	# RETURNS: str name of window, str name of process

	# Get the unique window ID of the foreground window 
	windowId = windll.user32.GetForegroundWindow()   

	# get title length of the window id (windowId)
	titleLength = windll.user32.GetWindowTextLengthW(windowId)  

	# Create a buffer to put the title on 
	# titleLength + 1 because C strings require an additional character 
	# '\0' to terminate strings, I assume
	titleBuffer = create_unicode_buffer(titleLength + 1)   
	
	# Get window text of the given window ID (windowId), store it to the 
	# second argument (titleBuffer), 
	# and use 3rd arg as max length of text incl '\0'. 
	windll.user32.GetWindowTextW(windowId, titleBuffer, titleLength + 1) 

	# creates a dword type variable which will store the Process ID of the 
	# foreground window
	pid = wintypes.DWORD()   

	# Get process id of the given window ID (arg 1) and store it to
	# pid variable
	windll.user32.GetWindowThreadProcessId(windowId, byref(pid)) 
	
	# Run command 'tasklist', lookup which program has the pid
	# and store CSV output to var
	processNameCSV = os.popen(f"tasklist /FI \
					\"pid eq {pid.value}\" /FO CSV").read()  

	# Returns a csv reader object
	readCSV = csv.reader(processNameCSV)   
	listCSV = list(readCSV)   
	# Position of the program name in the list 
	# I wouldn't consider this portable so this might change.
	exeName = listCSV[10][0]   

	# Return the window name, & process name running the window.
	return titleBuffer.value, exeName 

def getUserIsActive(lastInputInfo, minGap=800): 
	# Compares gap between last time of input from mouse or kb and current time.
	# ARGS: 
	# 	lastInputInfo -> Instance of class LASTINPUTINFO(ctypes.Structure), 
	#	minGap -> Int, minimum time in mseconds

	# Store last input time to class
	windll.user32.GetLastInputInfo(byref(lastInputInfo))   
	lastInputTime = lastInputInfo.dwTime

	currentTime = windll.kernel32.GetTickCount()   

	timeGap = currentTime - lastInputTime

	if timeGap <= minGap:  
		return True
	elif timeGap > minGap:
		return False

class Tracker():
	# Get foreground window, track inactivity. Return when window changes
	
	activity = {
		"actStart": None,
		"actEnd": None,
		"processName": "", 
		"windowName": "" , 
		"inactDuration": 0.0
	}

	# Activity will not be considered unless the user 
	# spent time greater than this value. 
	ACTIVMINTIME = .8 # Seconds

	# Min time for each while loop. Helps in lowering 
	# memory by reducing API calls to the OS. 
	WHILEINTERVAL = 0.2 # Seconds

	def __init__(self):
		self.lastInputInfo = LASTINPUTINFO()  
		self.lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   
	
	def track(self): 
		currentWindow = '' 
		currentProcess = '' 
		tWindowDuration = 0 
		userFromSleep = False   # User returned from inactivity
		# Every time user gets inactive, add current time to start.
		inactiveDur = {"start": 0, "end": 0 }   

		self.activity['actStart'] = datetime.now()

		while True:  
		# Instead of a while True, while currentWindow \
		# == self.activity["windowName"] might be possible

			time.sleep(self.WHILEINTERVAL)

			# Detects user Inactivity
			userIsActive = getUserIsActive(self.lastInputInfo) 
			currentWindow, currentProcess = getActivityInfo()

			# Logs time of user inactivity 
			if not userIsActive:
				if not userFromSleep:
					inactiveDur["start"] += time.time()
					userFromSleep = True
			else:
				if userFromSleep:    
					# when user awakes, inactivity ends
					inactiveDur["end"] += time.time()  
					# User should first be inactive before awakening again
					userFromSleep = False  

			# When the program is ran for the first time, windowName is ""
			if self.activity["windowName"] != '':    
				if currentWindow != self.activity["windowName"]: 

					if userFromSleep:
						# Handles the missing end time when the user is inactive 
						# and a change of window occurs (e.g. when waiting for a 
						# webpage to load, the windowName is "New Tab", which
						# changes when the page loads)

						inactiveDur["end"] += time.time()
						userFromSleep = False 

					self.activity["actEnd"] = datetime.now()

					tWindowDuration = self.activity["actEnd"] - \
						self.activity["actStart"]            

					if tWindowDuration.total_seconds() >= self.ACTIVMINTIME: 

						self.activity["inactDuration"] = inactiveDur["end"] - \
														inactiveDur["start"]

						inactiveDur["start"] = 0     
						inactiveDur["end"] = 0
						break
 
			self.activity["windowName"] = currentWindow
			self.activity["processName"] = currentProcess   

		# Convert dict values to string 
		# As required by main.py
		self.activity["actStart"] = self.activity["actStart"]\
			.isoformat(sep=' ', timespec='milliseconds')
		self.activity["actEnd"] = self.activity["actEnd"]\
			.isoformat(sep=' ', timespec='milliseconds')
		for key in self.activity:
			self.activity[key] = str(self.activity[key])

		return self.activity