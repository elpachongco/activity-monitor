# Python program that will log my activity and store it into a spreadsheet so I can monitor my activity
import ezsheets as ezsh
from ctypes import wintypes, windll, create_unicode_buffer, byref
import time, os, csv
spreadsheetID = "1ImM0Ph_LP26BqJPKBauNl18mZVEvziyS0O5X9ecElMQ"

"""
1. Look at current active window
2. If there is mouse/keyboard activity - time it
3. if input devices become inactive - log the activity with time data
4. if current window changes while activity remains - log it ? 
5. The data is then indexed and compressed into another spreadsheet the next day. This will make it impossible to see the specific activities but will still make analysis possible. 
"""
spreadsheet = ezsh.Spreadsheet(spreadsheetID)
archiveSheetTitle = "Previous Activity Data"
currentdaySheetTitle = "Today's Activity Log"
logSheet = spreadsheet[currentdaySheetTitle]
archiveSheet = spreadsheet[archiveSheetTitle]

def getForegroundWindowTitle():
    h_wnd = windll.user32.GetForegroundWindow()   # Get HWND of the foreground window
    length = windll.user32.GetWindowTextLengthW(h_wnd)  # get length of title of said window
    buf = create_unicode_buffer(length + 1)   # Create a buffer to put the title on
    windll.user32.GetWindowTextW(h_wnd, buf, length + 1)
    pid = wintypes.DWORD()  
    windll.user32.GetWindowThreadProcessId(h_wnd, byref(pid)) # Get PID of the process
    processNameCSV = os.popen(f"tasklist /FI \"pid eq {pid.value}\" /FO CSV").read() # Get exe name from PID
    
    # Handling CSV Output
    readCSV = csv.reader(processNameCSV)
    listCSV = list(readCSV)   # Turn the CSV into a list
    exeName = listCSV[10][0]   # Gets the name of the .exe file that runs the program

    # Return the window title, Program name, and current time.
    return str(buf.value), str(exeName), time.time() 

def insertToSpreadsheet(spreadsheet, cellCoordinate, cellInput):
    spreadsheet[cellCoordinate] = cellInput



cycleCount = 2  # Data logging starts on row 2
refreshRate = 10  # No. of sec between the times of looking at activity

# Ascii numbers to be used with chr() function
windowTitleCol = 68  # Column to put window title in 
programNameCol = 67  # Column to put the program title in
timeStampCol = 65  # Columnt to put the timeStamp in
while True:
    forgroundWindowTitle, programName, timeStamp = getForegroundWindowTitle()
    time.sleep(refreshRate)    
    try:
        cycleCount = cycleCount + 1


    except: 
        print("error encountered, restarting loop")
        pass



"""
Notes:

1. Make it so that if in the next loop, it's still the same program, just add the sleep time to the total time to avoid unnecesary duplication
    2. Have a clever way to identify if the name is a duplicate or not (use if x in y instead of if x == y)... found - using hwnd comparisosn == DONE, using PID and CMD commands

3. Have the program name and tabname / window title be in different cell

4. Make it only activate if there's input activity 
5. Make a function for end of day analysis. Will basically find any duplicates and tally total number of hours
"""