import csv
import ctypes
import logging
import platform
import subprocess
import time

logger = logging.getLogger()

if platform.system() == "Windows":
    # ctypes handles the Windows-specific functions
    from ctypes import byref, create_unicode_buffer, windll, wintypes


class LASTINPUTINFO(ctypes.Structure):
    # Special class for storing lastinputinfo data from windows
    _fields_ = [("cbSize", ctypes.c_ulong), ("dwTime", ctypes.c_ulong)]


def getActivityInfo(os):
    # Get window name and process name of current foreground window
    # Makes use of windows API
    # RETURNS: str name of window, str name of process
    if os == "Windows":
        # Get the unique window ID of the foreground window
        windowId = windll.user32.GetForegroundWindow()

        # get title length of the window id (windowId)
        titleLength = windll.user32.GetWindowTextLengthW(windowId)

        # Create a buffer to put the title on
        # titleLength + 1 because C strings require an additional character
        # '\0' to terminate strings, I assume
        titleBuffer = create_unicode_buffer(titleLength + 1)

        # Get window text of the given window ID (windowId), store it to the
        # second argument (titleBuffer), and use 3rd arg as max length of text incl '\0'.
        windll.user32.GetWindowTextW(windowId, titleBuffer, titleLength + 1)

        # creates a dword type variable which will store the Process ID of the
        # foreground window
        pid = wintypes.DWORD()

        # Get process id of the given window ID (arg 1) and store it to
        # pid variable
        windll.user32.GetWindowThreadProcessId(windowId, byref(pid))

        # Run command 'tasklist', lookup which program has the pid
        # and store CSV output to var
        tasklist = os.popen(
            f'tasklist /FI \
						"pid eq {pid.value}" /FO CSV'
        )

        processNameCSV = tasklist.read()
        tasklist.close()

        # Returns a csv reader object
        readCSV = csv.reader(processNameCSV)
        listCSV = list(readCSV)

        # Position of the program name in the list
        # I wouldn't consider this portable so this might change.
        exeName = listCSV[10][0]

        # Return the window name, & process name running the window.
        return titleBuffer.value, exeName

    if os == "Linux":
        result = subprocess.run(
            ["timeout", "1", "xdotool", "getwindowfocus", "getwindowpid"],
            capture_output=True,
            text=True,
        )

        # pid is blank if no window is focused.
        if result.stdout == "":
            return "", ""

        proc = int(result.stdout)

        result = subprocess.run(
            ["timeout", "1", "ps", "-p", str(proc), "-o", "comm="],
            capture_output=True,
            text=True,
        )
        processName = result.stdout.strip("\n")

        result = subprocess.run(
            ["timeout", "1", "xdotool", "getwindowfocus", "getwindowname"],
            capture_output=True,
            text=True,
        )

        windowName = result.stdout.strip("\n")
        return windowName, processName

    logger.error("OS is Unknown: %s", os)
    raise Exception("OS is Unknown: %s", os)


def getUserIsActive(lastInputInfo, os, minGap=800):
    # Compares gap between last time of input from mouse or kb and current time.
    # ARGS:
    # 	lastInputInfo -> Instance of class LASTINPUTINFO(ctypes.Structure),
    # 	minGap -> Int, minimum time between activity in mseconds
    # 	os -> string, the platform the user is using

    ### TODO: Fix minGap linux implementation.

    # Store last input time to class
    if os == "Windows":
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        lastInputTime = lastInputInfo.dwTime

        currentTime = windll.kernel32.GetTickCount()

        timeGap = currentTime - lastInputTime

        return timeGap <= minGap

    if os == "Linux":
        # Returns: 234324.2 234234.3
        # See proc man page for /proc/uptime
        # result = subprocess.run(["cat", "/proc/uptime"], capture_output=True, text=True)
        # Get first item only
        # currentTimeMs = float(result.stdout.split(" ")[0]) * 1000

        result = subprocess.run(
            # Implementation depends on this command:
            # timeout .1 xinput test-xi2 --root
            # If an input is made, EVENT is present.
            # timeout should be < mingap
            ["timeout", str((minGap / 1000) / 2), "xinput", "test-xi2", "--root"],
            capture_output=True,
            text=True,
        )
        # print( "EVENT" in result.stdout)
        return "EVENT" in result.stdout

    logger.error("OS is Unknown: %s")
    raise Exception("OS is Unknown: %s", os)


class Tracker:
    # Get foreground window, track inactivity. Return when window changes

    # Activity will not be considered unless the user
    # spent time greater than this value.
    ACTIVMINSECONDS = 0.8  # Seconds

    # Min time for each while loop. Helps in lowering
    # memory by reducing API calls to the OS.
    WHILEINTERVAL = 0.5  # Seconds

    lastInputInfo = None

    def __init__(self):
        self.os = platform.system()
        logger.info("OS detected: %s", self.os)

        if self.os == "Windows":
            self.lastInputInfo = LASTINPUTINFO()
            self.lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    def track(self):
        """
        Start a loop tracking the current activity

        returns:
            activity = {
                "startMS": None,
                "endMS": None,
                "processName": "",
                "windowName": "",
                "idleMS": 0.0,
                "lengthMS": 0
            }
        """
        activity = {
            "startMS": 0,
            "endMS": 0,
            "processName": "",
            "windowName": "",
            "idleMS": 0.0,
            "lengthMS": 0,
        }

        currentWindow = ""
        currentProcess = ""
        idle = False  # User returned from inactivity

        # Every time user gets inactive, add current time to start.
        # if inactivity ends, add current time to end.
        idleStartSeconds = 0.0
        idleEndSeconds = 0.0

        activity["startMS"] = time.time()

        while currentWindow == activity["windowName"]:
            time.sleep(self.WHILEINTERVAL)

            # Detects user Inactivity
            userIsActive = getUserIsActive(self.lastInputInfo, self.os)
            currentWindow, currentProcess = getActivityInfo(self.os)

            # When track() is ran for the first time, windowName, procesName is ""
            # Set current window as windowname, and proceed to next loop cycle.
            if activity["windowName"] == "":
                activity["windowName"] = currentWindow
                activity["processName"] = currentProcess
                continue

            if not userIsActive:
                if not idle:
                    idleStartSeconds += time.time()
                    idle = True
            else:
                # If user is active and idle == True, user came back from inactivity
                if idle:
                    idleEndSeconds += time.time()
                    # User is no longer idle. Set idle = False for the next inactivity.
                    idle = False

            if currentWindow != activity["windowName"]:
                if idle:
                    # Handles the missing end time when the user is inactive
                    # and a change of window occurs (e.g. when waiting for a
                    # webpage to load, the windowName is "New Tab", which
                    # changes when the page loads, "new tab" -> "youtube.com")
                    idleEndSeconds += time.time()
                    idle = False

                activity["endMS"] = time.time()

                activity["lengthMS"] = int(
                    (activity["endMS"] - activity["startMS"]) * 1000
                )

                if activity["lengthMS"] < self.ACTIVMINSECONDS * 1000:
                    continue

                activity["idleMS"] = int((idleEndSeconds - idleStartSeconds) * 1000)

                activity["startMS"] = int(activity["startMS"] * 1000)
                activity["endMS"] = int(activity["endMS"] * 1000)
                activity = dictValToStr(activity)

                return activity


def toIso8601(activityDict, keys):
    # ARGS: Dictionary, Keys of values to be converted
    # Converts the values of the keys from dictionary
    # into format specified by sqlite3 iso861
    activity = activityDict
    for key in keys:
        activity[key] = activity[key].isoformat(sep=" ", timespec="milliseconds")
    return activity


def dictValToStr(activityDict):
    # ARGS: dictionary to convert
    # Converts all values for all keys to string.
    activity = activityDict
    for key in activity:
        activity[key] = str(activity[key])
    return activity
