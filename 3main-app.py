#! python3
# This is an activity monitor app for Windows.
import ezsheets as ezsh   # googlesheets api wrapper
import time, os, csv   # os & csv for cmd commands.  # time logging and sleep()

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
logSheet = spreadsheet[currentdaySheetTitle]   # spreadsheet object - current day 
archiveSheet = spreadsheet[archiveSheetTitle]   # spreadsheet object - archival

def getForegroundWindowTitle():
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
browserExeNames =  ["brave.exe", "firefox.exe", "chrome.exe"]

class LASTINPUTINFO(ctypes.Structure):
    # Special class for storing lastinputinfo data from windows
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwTime", ctypes.c_ulong) ]
lastInputInfo = LASTINPUTINFO()  # Instantiate class
lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)   # set size of class - microsoft requirement

windll.user32.GetLastInputInfo(byref(lastInputInfo))   # Store last input time to class
lastInputTime = lastInputInfo.dwTime   # Access last input time - then store to var
tickCount = windll.kernel32.GetTickCount()   # Get Current time in ms, for comparison


while True:
    try:
        
    except:
         pass # Ignore the error, do one more loop
