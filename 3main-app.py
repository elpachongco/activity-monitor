# Todo list:
#     1. add blacklist feature that will not list activities if a word is included in the window name
#             ex. is Binance where the window name changes every second. This may cause the program to reach googles api limits
#              another ex is when I'm watching the tech tip 🙀
#     2. Better initialization - when the script is ran, save all the current spreadsheet data then clear it to make way for new data
#     3. Better google sheets dashboard. might use google data studio.
#     4. BUG#1 occurence of -1,617,418,605.75 and the positive equivalent, sometimes
#        - hypothesis: the bug is caused by the variable "activityMinTime" 
#     5. Auto program sleep if user is inactive for a set amount of time


# This is an activity monitor app for Windows.
import ezsheets as ezsh   # googlesheets api wrapper
import time, os, csv   
import ctypes  
from ctypes import wintypes, windll, create_unicode_buffer, byref
# wintypes for creating windows specific data types
# windll to access different windows dll lib (kernel32, system32)
# create_unicode_buffer storage for window names
# byref is for pointers, what ever that is

# Some rules of this program are there just to work around the 100 read & write limit of the GoogleAPI

# spreadsheet ID, file name, or link ❌ HAVENT TRIED IT
spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ"  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Instantiate the spreadsheet
archiveSheet = "Previous Activity Data"   # name of sheet/workspace to put archival data in
currentdaySheet = "Today's Activity Log"   # name of sheet to put current day's data in



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
    
    # I have a feeling that the 

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
    readCSV = csv.reader(processNameCSV)   # Read the CSV
    listCSV = list(readCSV)   # Make it a list 
    exeName = listCSV[10][0]   # Position of the program name in the list 
    
    return str(buf.value), str(exeName)  # Return the window text, name of program running the window.

def userIsActiveCheck(timeGap):  #Dictionary now - Edit - DONE ✔✔✅😊
    # Decide whether user is inactive by comparing the inactivity time to accepted delay between last input time and current time
    timeGapTolerance = 800  # time in ms considered when deciding if gap means the user is active or not
    if timeGap <= timeGapTolerance:  
        return True
    elif timeGap > timeGapTolerance:
        return False


# ========== User configurable variables ============
# Column address - generate letters using ASCII letter codes
cellEntryStartRow = 2  # what row the data will start to be entered  
activMinTime = 1.3  # min sec that must pass before action is considered.

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

    if not userIsActive:
        if userAwake == False:
            inactivityTime["start"] += time.time()
            userAwake = True
            print(f"Cell: {windowChangeCount}")
            print("xxxxxxxxxxxxxxxxxxxxxx")
            print("Start: " + str(inactivityTime["start"]))
    elif userIsActive:
        if userAwake == True:   # 
            inactivityTime["end"] += time.time()  # when user awakes, inactivity ends
            userAwake = False  # User should first be inactive before awakening again
            print("End: " + str(inactivityTime["end"]))

    if activityDict["windowName"] != '':   # When the program is ran for the first time, windowName is = "" 
        if currentWindowName != activityDict["windowName"]: 

            # Handles the missing end time when the user is inactive and a change of window occurs (e.g. waiting for a webpage to load)
            if userAwake == True:
                inactivityTime["end"] += time.time()
                userAwake = False 

            activityDict["actEnd"] = time.time()                    
            totalWindowDuration = activityDict["actEnd"] - activityDict["actStart"]
            if totalWindowDuration  >= activMinTime: 
                cellNumber = str(windowChangeCount + cellEntryStartRow)

                totalInactDuration = str(inactivityTime["end"] - inactivityTime["start"])
                activityDict["inactDuration"] = totalInactDuration
                writeToSpreadsheet(currentDaySS, cellColumn , windowChangeCount + cellEntryStartRow , activityDict)
                print("FStart: " + str(inactivityTime["start"]))
                print("FEnd: " + str(inactivityTime["end"]))
                print(f"total Inactivity: {totalInactDuration}" )
                print('===============')

                activityDict["actStart"] = time.time()  # Set a new start time for the new activity
                
                windowChangeCount += 1   # new detected window means that a window change happened
            
                # Attempt to solve bug#1. More info on github
                inactivityTime["start"] = 0     
                inactivityTime["end"] = 0

    activityDict["windowName"] = currentWindowName
    activityDict["processName"] = currentProcess   