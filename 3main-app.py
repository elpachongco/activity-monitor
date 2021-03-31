# This is an activity monitor app for Windows.
import ezsheets as ezsh   # googlesheets api wrapper
import time, os, csv   # os & csv for cmd commands.  # time logging and sleep()

import ctypes, sys
from ctypes import wintypes, windll, create_unicode_buffer, byref
# wintypes for creating windows specific data types
# windll to access different windows dll lib (kernel32, system32)
# create_unicode_buffer storage for window names
# byref is for pointers

# This program works around the 100 read & write limit of the GoogleAPI

# spreadsheet ID, file name, or link ❌
spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ"  

spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Instantiate the spreadsheet
archiveSheetTitle = "Previous Activity Data"   # name of sheet/workspace to put archival data in
currentdaySheetTitle = "Today's Activity Log"   # name of sheet to put current day's data in
# logSheet = spreadsheet[currentdaySheetTitle]   # spreadsheet object - current day 
# archiveSheet = spreadsheet[archiveSheetTitle]   # spreadsheet object - archival

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

def writeToSpreadsheet(spreadsheetObj, sheet, cellLocation, inputText ):
    # Function that writes to the spreadsheet
    spreadsheet = spreadsheetObj[sheet]
    spreadsheet[cellLocation] = inputText

class LASTINPUTINFO(ctypes.Structure):
    # Special class for storing lastinputinfo data from windows
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwTime", ctypes.c_ulong) ]
lastInputInfo = LASTINPUTINFO()  # Instantiate class
lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   # set size of class - microsoft requirement

def userActivityCheck(activityList):
    # This function determines whether the user is active by looking at the inputActivity list.
    # The list contains 7 states.
    inactiveStates = 0
    timeGapTolerance = 300  # time in ms considered when deciding if gap means the user is active or not
    for x, y in enumerate(activityList):
        if y > timeGapTolerance:
            inactiveStates += 1
    if inactiveStates <= 5:  # 
        return True
    elif inactiveStates > 5:
        return False
    pass

# Columns
startTimeCol = chr(65)
endTimeCol = chr(66)
programNameCell = chr(69)
windowNameCell = chr(70)
#timeSpentCell = chr(69)

cellEntryStartRow = 2   # what row the data will start to be entered  
loopCount = 0 
startTime = time.time() # Get time when the script was first ran
endTime = 0
windowChangeCount = 0  # Current number of window changes

activityMinTime = 2.3  # min sec that must pass before action is considered.
prevWindowName = ''
prevProcessName = ''
windowName = ''
userStates = []
lastActiveTime = 0
lastInactiveTime = 0
while True:
    loopCount += 1

    windll.user32.GetLastInputInfo(byref(lastInputInfo))   # Store last input time to class
    lastInputTime = lastInputInfo.dwTime   # Access last input time - then store to var
    tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison
    userStates.append(tickCount-lastInputTime)

    userIsActive = userActivityCheck(userStates[-7:])  # Send the last 7 list values to func

    windowName, processName, activityTimestamp = getActivityInfo()
    if prevWindowName != '': 
        if not userIsActive:
            lastActiveTime = time.time()
            if windowName == prevWindowName:
                print(userIsActive)            
                continue
            '''
            elif windowName != prevWindowName:
                endTime = time.time()
                if endTime-startTime >= activityMinTime:   # Only perform action if action is greater than 1sec
                    cellNumber = str(windowChangeCount + cellEntryStartRow)
                    """
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, programNameCell + cellNumber, prevProcessName)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, windowNameCell + cellNumber, prevWindowName)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, startTimeCol + cellNumber, startTime)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, endTimeCol + cellNumber, endTime)
                    """
                    print(prevProcessName + "\n" + prevWindowName + "\n" + str(endTime-startTime))
                    startTime = activityTimestamp
                    windowChangeCount += 1
                elif endTime-startTime < activityMinTime:
                    endTime += time.time() - endTime '''
        elif userIsActive:            
            if windowName != prevWindowName:
                endTime = time.time()
                if endTime-startTime >= activityMinTime:   # Only perform action if action is greater than 1sec
                    cellNumber = str(windowChangeCount + cellEntryStartRow)
                    """
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, programNameCell + cellNumber, prevProcessName)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, windowNameCell + cellNumber, prevWindowName)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, startTimeCol + cellNumber, startTime)
                    writeToSpreadsheet(spreadsheet, currentdaySheetTitle, endTimeCol + cellNumber, endTime)
                    """
                    print(prevProcessName + "\n" + prevWindowName + "\n" + str(endTime-startTime))
                    startTime = activityTimestamp
                    windowChangeCount += 1
                elif endTime-startTime < activityMinTime:
                    endTime += time.time() - endTime
            elif windowName == prevWindowName:
                #print(userIsActive)            
                continue

    prevWindowName = windowName
    prevProcessName = processName

print(loopCount)
