import ctypes, time, os, csv, logging, sys
from datetime import datetime
import platform
import subprocess

if platform.system() == "Windows":
    # ctypes handles the Windows-specific functions
    from ctypes import wintypes, windll, create_unicode_buffer, byref


class LASTINPUTINFO(ctypes.Structure):
    # Special class for storing lastinputinfo data from windows
    _fields_ = [("cbSize", ctypes.c_ulong), ("dwTime", ctypes.c_ulong)]


def getActivityInfo(os="Windows"):
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
            ["xdotool", "getwindowfocus", "getwindowpid"],
            capture_output=True,
            text=True,
        )

        proc = int(result.stdout)

        result = subprocess.run(
            ["ps", "-p", str(proc), "-o", "comm="],
            capture_output=True,
            text=True,
        )
        processName = result.stdout

        result = subprocess.run(
            ["xdotool", "getwindowfocus", "getwindowname"],
            capture_output=True,
            text=True,
        )

        windowName = result.stdout
        return windowName, processName


def getUserIsActive(lastInputInfo, minGap=800, os="Windows"):
    # Compares gap between last time of input from mouse or kb and current time.
    # ARGS:
    # 	lastInputInfo -> Instance of class LASTINPUTINFO(ctypes.Structure),
    # 	minGap -> Int, minimum time between activity in mseconds
    # 	os -> string, the platform the user is using

    # Store last input time to class
    if os == "Windows":
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        lastInputTime = lastInputInfo.dwTime

        currentTime = windll.kernel32.GetTickCount()

        timeGap = currentTime - lastInputTime

        return timeGap <= minGap

    if os == "Linux":
        # Returns: 234324.2 234234.3
        result = subprocess.run(["cat", "/proc/uptime"], capture_output=True, text=True)
        # Get first item only
        currentTimeMs = float(result.stdout.split(" ")[0]) * 1000
        timeGap = currentTimeMs - 0

        result = subprocess.run(
            ["timeout", str(minGap / 1000), "xinput", "test-xi2", "--root"],
            capture_output=True,
            text=True,
        )
        print("EVENT" in result.stdout)
        return "EVENT" in result.stdout


class Tracker:
    # Get foreground window, track inactivity. Return when window changes

    activity = {
        "actStart": None,
        "actEnd": None,
        "processName": "",
        "windowName": "",
        "inactDuration": 0.0,
    }

    # Activity will not be considered unless the user
    # spent time greater than this value.
    ACTIVMINTIME = 0.8  # Seconds

    # Min time for each while loop. Helps in lowering
    # memory by reducing API calls to the OS.
    WHILEINTERVAL = 0.2  # Seconds

    def __init__(self):
        self.os = platform.system()
        self.lastInputInfo = LASTINPUTINFO()
        self.lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    def track(self):
        currentWindow = ""
        currentProcess = ""
        tWindowDuration = 0
        userFromSleep = False  # User returned from inactivity

        # Every time user gets inactive, add current time to start.
        # if inactivity ends, add current time to end.
        inactiveDur = {"start": 0, "end": 0}

        self.activity["actStart"] = datetime.now()

        while True:
            # Instead of a while True, while currentWindow
            # == self.activity["windowName"] might be possible

            time.sleep(self.WHILEINTERVAL)

            # Detects user Inactivity
            userIsActive = getUserIsActive(self.lastInputInfo, os=self.os)
            currentWindow, currentProcess = getActivityInfo(os=self.os)

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
            if self.activity["windowName"] != "":
                if currentWindow != self.activity["windowName"]:
                    if userFromSleep:
                        # Handles the missing end time when the user is inactive
                        # and a change of window occurs (e.g. when waiting for a
                        # webpage to load, the windowName is "New Tab", which
                        # changes when the page loads)

                        inactiveDur["end"] += time.time()
                        userFromSleep = False

                    self.activity["actEnd"] = datetime.now()

                    tWindowDuration = (
                        self.activity["actEnd"] - self.activity["actStart"]
                    )

                    if tWindowDuration.total_seconds() >= self.ACTIVMINTIME:
                        self.activity["inactDuration"] = (
                            inactiveDur["end"] - inactiveDur["start"]
                        )

                        inactiveDur["start"] = 0
                        inactiveDur["end"] = 0
                        break

            self.activity["windowName"] = currentWindow
            self.activity["processName"] = currentProcess

        # Converts the listed key's values into
        # iso8601 time format specified by sqlite3
        self.toIso8601(self.activity, ["actStart", "actEnd"])

        # Convert dict values to string
        self.dictValToStr(self.activity)

        return self.activity

    def toIso8601(self, activityDict, keys):
        # ARGS: Dictionary, Keys of values to be converted
        # Converts the values of the keys from dictionary
        # into format specified by sqlite3 iso861
        for key in keys:
            activityDict[key] = activityDict[key].isoformat(
                sep=" ", timespec="milliseconds"
            )

    def dictValToStr(self, activityDict):
        # ARGS: dictionary to convert
        # Converts all values for all keys to string.
        for key in activityDict:
            activityDict[key] = str(activityDict[key])
