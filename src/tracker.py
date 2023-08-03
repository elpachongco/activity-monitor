import logging
import platform
import time

import psutil
from desktopspy.trackers import getForegroundWindow, isUserActive

logger = logging.getLogger()


class Tracker:
    """Get foreground window, track inactivity. Return when window changes
    ARGS: None
    RETURN: Dictionary with String values, and keys:
        {"processName": , "windowName": "startMS": , "endMS": , "idleMS": ,
        "lengthMS": }
    """

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
        lastIdleRecord = 0.0

        activity["startMS"] = time.time()

        while currentWindow == activity["windowName"]:
            time.sleep(self.WHILEINTERVAL)

            # Detects user Inactivity
            userIsActive = isUserActive(self.os)
            currentWindow, currentPid = getForegroundWindow(self.os)
            if (
                currentPid == ""
            ):  # This means there is no window selected i.e. on reboot
                currentWindow = ""
                activity["windowName"] = ""
                activity["startMS"] = time.time()
                continue

            currentProcess = psutil.Process(currentPid).name()

            # When track() is ran for the first time, windowName, procesName is ""
            # Set current window as windowname, and proceed to next loop cycle.
            if activity["windowName"] == "":
                activity["windowName"] = currentWindow
                activity["processName"] = currentProcess
                continue

            if not userIsActive:
                if not idle:
                    idleStartSeconds += time.time()
                    lastIdleRecord = time.time()
                    idle = True
            else:
                # If user is active and idle == True, user came back from inactivity
                if idle:
                    idleEndSeconds += time.time()
                    lastIdleRecord = time.time()
                    # User is no longer idle. Set idle = False for the next inactivity.
                    idle = False

            if currentWindow != activity["windowName"]:
                if idle:
                    """
                    Handles the missing end time when the user is inactive
                    and a change of window occurs (e.g. when waiting for a
                    webpage to load, the windowName is "New Tab", which
                    changes when the page loads, "new tab" -> "youtube.com")
                    """
                    idleEndSeconds += time.time()
                    lastIdleRecord = time.time()
                    idle = False

                activity["endMS"] = time.time()

                """
                Handle long hours of inactivity. E.g. if a user starts activity @ 2pm,
                startMS is 2pm. If PC sleeps after 5 minutes, then the maximum idleMS is
                5mins. If user returns at 6pm, endMS is 6pm. Length will
                be 4hours - 5mins. This is incorrect;  idle time was not recorded.
                Length should be startMS + idleMS - startMS. endMS should be
                startMS + idleMS.

                This should also consider scenario where there is a long idle time but
                the computer doesn't sleep and the windowName is not changed.
                """
                if activity["endMS"] - activity["startMS"] > 3600.0:
                    if activity["endMS"] - lastIdleRecord < 3600.0:
                        activity["endMS"] = activity["startMS"] + (
                            (idleEndSeconds - idleStartSeconds)
                        )

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
