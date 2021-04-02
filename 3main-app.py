# This is an activity monitor app for Windows.
import ezsheets as ezsh   # googlesheets api wrapper
import time, os, csv   # os & csv for cmd commands.  # time logging and sleep()

import ctypes, sys
from ctypes import wintypes, windll, create_unicode_buffer, byref
# wintypes for creating windows specific data types
# windll to access different windows dll lib (kernel32, system32)
# create_unicode_buffer storage for window names
# byref is for pointers, what ever that is

# Some rules of this program are there just to work around the 100 read & write limit of the GoogleAPI

# spreadsheet ID, file name, or link ❌
spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ"  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Instantiate the spreadsheet
archiveSheet = "Previous Activity Data"   # name of sheet/workspace to put archival data in
currentdaySheet = "Today's Activity Log"   # name of sheet to put current day's data in

def getActivityInfo():
    # Gets information on current active/foreground window. 
    h_wnd = windll.user32.GetForegroundWindow()   # foreground window unique ID for each window independent of app - HWND
    length = windll.user32.GetWindowTextLengthW(h_wnd)  # get length of title of said window
    buf = create_unicode_buffer(length + 1)   # Create a buffer to put the title on (function requirement)
    windll.user32.GetWindowTextW(h_wnd, buf, length + 1) # function returns result to variable buf (buffer)
    pid = wintypes.DWORD()   # creates a dword type variable to store the process ID of the window
    windll.user32.GetWindowThreadProcessId(h_wnd, byref(pid)) # Function stores the PID of the specified window to pid.
    processNameCSV = os.popen(f"tasklist /FI \"pid eq {pid.value}\" /FO CSV").read() # Run a command and store output to var (CSV)
    readCSV = csv.reader(processNameCSV)   # Read the CSV
    listCSV = list(readCSV)   # Make it a list 
    exeName = listCSV[10][0]   # Position of the program name in the list 
    return str(buf.value), str(exeName), time.time()   # Return the window text, name of program running the window, and time (epoch).

#Essential for keeping track of which pages are most oftenly used.
# Most browsers put current page title as window name with browser name in the end
# ex. - "Youtube.com - Brave" - can be used to track which sites are most visited
browserExeNames =  ("brave.exe", "firefox.exe", "chrome.exe")

def writeToSpreadsheet(spreadSheetDict, cellLocation, inputDict ):   # ❌😫 Needs editing
    # Function that writes to the spreadsheet
    # spreadSheetDict accepts spreadSheetInf Dictionary
    # inputDict accepts activityDict
    spreadsheet = spreadsheetObj[sheet]
    spreadsheet[cellLocation] = inputDict

class LASTINPUTINFO(ctypes.Structure):
    # Special class for storing lastinputinfo data from windows
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwTime", ctypes.c_ulong) ]
lastInputInfo = LASTINPUTINFO()  # Instantiate class
lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   # set size of class - microsoft requirement

def userActivityCheck(activityList):  #❌ Dictionary now
    # This function determines whether the user is active by looking at the inputActivity list.
    # The list contains 7 states.
    timeGapTolerance = 800  # time in ms considered when deciding if gap means the user is active or not
    inactiveStates = 0  # storage of number of inactive states in the list
    for x, y in enumerate(activityList):
        if y > timeGapTolerance:
            inactiveStates += 1
    percentageOfStates = .75 # Percentage of the inactiveStates before proclaiming the user is Inactive
    if inactiveStates <= inactiveStates*percentageOfStates:  
        return True
    elif inactiveStates > inactiveStates*percentageOfStates: 
        return False


# ========== User configurable variables ============
# Column address - generate letters using ASCII letter codes
startTimeCol = chr(65)  # column A
endTimeCol = chr(66) # Column B
programNameCell = chr(69)
windowNameCell = chr(70)

cellEntryStartRow = 2   # what row the data will start to be entered  
activityMinTime = 0  # min sec that must pass before action is considered.


# ========== Program only variables =============

# === Time ===
startTime = time.time() # Gets time when the script was first ran
endTime = 0  # used to keep track of program/activity end time

prevWindowName = ''
prevProcessName = ''

inactiveTimes = 0 
userInactivityStart = 0
userPrevInactivityEnd = 0

#  === Dicts 😞
spreadSheetInf = {"instance": spreadsheet, "currentDaySheet": currentdaySheet, "archiveSheet":archiveSheet}
activityDict = {"processName": "", "windowName": "" , "actStart": "", "actEnd": ""}   # Latest activity and all related info will be stored here.
currentActLog = []   # Keeps track of times that the user went active and inactive.
inactivityTimes = {"start": 0, "end": 0 }   # Every time user gets inactive, add current time to start.

# === counters 
loopCount = 0   # counts while Loops
windowChangeCount = 0  # Current number of window changes
while True:
    loopCount += 1

    windll.user32.GetLastInputInfo(byref(lastInputInfo))   # Store last input time to class
    lastInputTime = lastInputInfo.dwTime   # Access last input time - then store to var
    tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison
    userIsActive = userActivityCheck(tickCount-lastInputTime)  # Send the last 7 list values to func, may be expanded
    activityDict["windowName"], activityDict["processName"], activityTimestamp = getActivityInfo()

    if prevWindowName != '': 
            if activityDict["windowName"] == prevWindowName:
                pass
            if activityDict["windowName"] != prevWindowName:                
                if endTime-startTime >= activityMinTime:   # Only perform action if action is greater than 1sec
                    cellNumber = str(windowChangeCount + cellEntryStartRow)
                    print(activityDict)                    
                    startTime = activityTimestamp
                    windowChangeCount += 1

    prevWindowName = activityDict["windowName"]
    prevProcessName = activityDict["processName"]

print(loopCount)

