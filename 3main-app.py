# This is an activity monitor app for Windows.
import ezsheets as ezsh   # googlesheets api wrapper
import time, os, csv, logging   
import ctypes  
from ctypes import wintypes, windll, create_unicode_buffer, byref
# ctypes handles some of Windows-specific functions
import sys  # only for the sys.exit()


# spreadsheet ID, file name, or link ❌ HAVENT TRIED IT
spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ"  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Create the spreadsheet object
archiveSheet = "Previous Activity Data"   # name of sheet/workspace to put archival data in
currentdaySheet = "Today's Activity Log"   # name of sheet to put current day's data in

# Get ignorelist and censorlist
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
                print(item)
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
logging.basicConfig(format='%(asctime)s \n %(message)s', filename='main-app.log', filemode= 'w', encoding='utf-8', level=logging.INFO)

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


# ========== User configurable variables ============
cellEntryStartRow = 2  # what row the data will start to be entered  
activMinTime = .8  # min sec that must pass before action is considered.


# ========== non-configurable program variables =============
currentWindowName = ''   # temp storage for window name data.
currentProcess = '' 
userAwake = False   # user Awake is when the user goes from being inactive to active
totalInactDuration = 0
totalWindowDuration = 0

#  === Dicts 
currentDaySS = {"instance": spreadsheet, "sheet": currentdaySheet}   # FIX ARRANGEMENTS OF DICTIONARIES 
activityDict = {"processName": "", "windowName": "" , "actStart": "", "actEnd": "", "inactDuration": ""}   # Latest activity and all related info will be stored here.
cellColumn = {"startTime": "A", "endTime": "B", "inactiveTime": "E", "programName": "F", "windowName": "G"}
inactivityTime = {"start": 0, "end": 0 }   # Every time user gets inactive, add current time to start.

# === counters 
loopCount = 0   # counts while Loops, no purpose
windowChangeCount = 0  # Current number of window changes, cell row location is attached to this var

# === start preparation
activityDict["actStart"] = time.time()   # Called when the program starts.    

# The program censors the window name if a word from this text file is found.   
ignoreList, censorList = getKeywordList()
# The program will not list the the whole activity if an item in the list is found.
print(ignoreList)
print(censorList)
while True:  # == True
    loopCount += 1 
        # This will do for now but it should later be modified to a appropriate solution (multiprocessing ques and pipes?)
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
                        print("censor")
                        # Use this instead if you want to uncensor the first letter   
                        # activityDict["windowName"] = str(activityDict["windowName"])[0] + "[redacted]" 

                ignoreActivity = False
                for item in ignoreList:  # Only write if to spreadsheet if it doesn't contain ignore words
                    if item in activityDict["windowName"].lower():
                        print("ignore")
                        ignoreActivity = True

                if ignoreActivity == False:
                    writeToSpreadsheet(currentDaySS, cellColumn , windowChangeCount + cellEntryStartRow , activityDict)
                    windowChangeCount += 1   

                    # Logging purpose
                    logging.info("FStart: " + str(inactivityTime["start"])  +"\nFEnd: " + str(inactivityTime["end"]) + f"\ntotal Inactivity: {totalInactDuration}" + "\n" + '='*12 + "\n")
                
                activityDict["actStart"] = time.time()  # Set a new start time for the new activity
                            
                inactivityTime["start"] = 0     
                inactivityTime["end"] = 0

    activityDict["windowName"] = currentWindowName
    activityDict["processName"] = currentProcess   

# This will execute when the while loop stops
sys.exit()


# Todo list:

# In progress:

# Queued:
# 11. User sheets.updateRow() instead
# 2. Initialization - when the script is ran, save all the current spreadsheet data then clear it to make way for new data
# 9. End of day data saving 
# 10. Should ignoreList be in just one file?
# 11. Put all variables in one file

# DONE:
# 7. Make the program invisible .pyw, logging... - In progress - logging DONE, headless mode not sensible atm
# 1. add blacklist feature that will not list activities if a word is included in the window name
#     ex. is Binance where the window name changes every second. This may cause the program to reach googles api limits
#         another ex is when I'm watching the tech tip 🙀
# 6. Workaround for sites that change their page name e.g. messaging sites where notifications change window name, trading where price is displayed every sec
# 8. Handle Blacklisting and censoring in a file instead of in-program -DONE
# 3. Better google sheets dashboard. might use google data studio.
# 12. ignorelist and censorlist in one file
