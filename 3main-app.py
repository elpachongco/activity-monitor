# Todo list:
#     1. add blacklist feature that will not list activities if a word is included in the window name
#             ex. is Binance where the window name changes every second. This may cause the program to reach googles api limits




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
    return str(buf.value), str(exeName)  # Return the window text, name of program running the window.


def writeToSpreadsheet(spreadSheetDict, column, row, inputDict ):   # ❌😫 Needs editing, This function is super specific for this program only
    # Function that writes to the spreadsheet
    # spreadSheetDict accepts spreadSheetInf Dictionary
    # inputDict accepts activityDict
    spreadsheet = spreadSheetDict["instance"]
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

def userIsActiveCheck(timeGap):  #Dictionary now - Edit - DONE ✔✔✅😊
    # Decide whether user is inactive by comparing the inactivity time to accepted delay between last input time and current time
    timeGapTolerance = 800  # time in ms considered when deciding if gap means the user is active or not
    if timeGap <= timeGapTolerance:  
        return True
    elif timeGap > timeGapTolerance:
        return False


# ========== User configurable variables ============
# Column address - generate letters using ASCII letter codes
cellEntryStartRow = 2   # what row the data will start to be entered  
activMinTime = 1.42  # min sec that must pass before action is considered.


# ========== non-configurable program variables =============

currentWindowName = ''   # temp storage for window name data.
currentProcess = '' 
userAwake = False   # user Awake is when the user goes from being inactive to active
totalInactDuration = 0
totalWindowDuration = 0

#  === Dicts 😞
currentDaySS = {"instance": spreadsheet, "sheet": currentdaySheet}   # FIX ARRANGEMENTS OF DICTIONARIES 
activityDict = {"processName": "", "windowName": "" , "actStart": "", "actEnd": "", "inactDuration": ""}   # Latest activity and all related info will be stored here.
cellColumn = {"startTime": "A", "endTime": "B", "inactiveTime": "E", "programName": "F", "windowName": "G"}
inactivityTime = {"start": 0, "end": 0 }   # Every time user gets inactive, add current time to start.

# === counters 
loopCount = 0   # counts while Loops, no purpose
windowChangeCount = 0  # Current number of window changes, cell row location is attached to this var

# === start preparation
activityDict["actStart"] = time.time()   # Called when the program starts.

while True:
    loopCount += 1

    # === Section needs more cleaning
    # Detects user Inactivity
    windll.user32.GetLastInputInfo(byref(lastInputInfo))   # Store last input time to class
    lastInputTime = lastInputInfo.dwTime   # Access last input time - then store to var
    tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison against last input time
    userIsActive = userIsActiveCheck(tickCount-lastInputTime)  
    currentWindowName, currentProcess = getActivityInfo()

    # Logs time of user inactivity -- DONE 😊
    if userIsActive:
        if userAwake == True:
            inactivityTime["end"] += time.time()  # when user awakes, inactivity ends
            userAwake = False  # User should first be inactive before awakening again
    elif not userIsActive:
            if userAwake == False:
                inactivityTime["start"] += time.time()
                userAwake = True

    if activityDict["windowName"] != '':   # When the program is run for the first time, windowName is = "" 

        if currentWindowName != activityDict["windowName"]:                
            activityDict["actEnd"] = time.time()      
            totalWindowDuration = activityDict["actEnd"] - activityDict["actStart"]
            if totalWindowDuration  >= activMinTime: 
                cellNumber = str(windowChangeCount + cellEntryStartRow)

                totalInactDuration = inactivityTime["end"] - inactivityTime["start"]
                activityDict["inactDuration"] = totalInactDuration
                writeToSpreadsheet(currentDaySS, cellColumn , windowChangeCount + cellEntryStartRow , activityDict)

                activityDict["actStart"] = time.time()  # Set a new start time for the new activity
                
                # Reset inactivity timers when the user changes program
                inactivityTime["start"] = 0 
                inactivityTime["end"] = 0
                
                windowChangeCount += 1   # new detected window means that a window change happened

    activityDict["windowName"] = currentWindowName
    activityDict["processName"] = currentProcess
    # print(loopCount) # can be used to track how fast the while loop is
#    prevProcessName = currentProcess  # Might actually be unnecessary...


