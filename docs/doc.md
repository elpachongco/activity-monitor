# Documentation

The whole program communicates using `main.py` & the dictionary `activity`.

## main

`main.py` serves as controller for the programs. It imports the scripts in 
`./src` which contain classes.

`activity` is a dictionary (explained below) that is returned by the activity
tracker and accepted by the uploader.

It contains loop that calls the activity tracker. The tracker records the
current foreground window & the amount of time the user is inactive. It returns
when the foreground window changes/changes name.

The return value is the `activity` dictionary which is then passed to the 
uploader. The uploader uploads the data to `activity.db` then returns.

This repeats until the program is exited.

## activity 

`activity` is a dictionary that **must** contain the keys 

    "processName", "windowName", "actStart", "actEnd", "inactDuration"

All the values of the keys are of type String. 

(string) `actStart` and `actEnd` contain the start time and end of each activity.
Both are in iso8601 format `YYYY-MM-DD HH-MM-SS.SSS`. SQLite uses this format
for its date time functions. 

(float) `inactDuration` is the total time in seconds of the user's 
inactivity during the activity. 

(string) `processName` is the name of the process that is running the 
foreground window.

(string) `windowName` is the name of the foreground window.

`activity` is passed to uploader as a dictionary of strings.

## activity.db

`activity.db` is the sqlite3 database file that is used to store all the data
collected by the program. It contains the columns: 

```
'actStart' TEXT, 'actEnd' TEXT, 'inactDuration' REAL, 
'windowName' TEXT, 'processName' TEXT
```

## tracker

`tracker.py` contains the class `Tracker()`. Its job is to call the OS API to

- get the name of the foreground window, 
- get the name of the process that runs the said window, 
- Detect user inactivity getting the last time input was made.

Right now, the best solution is to call the Windows API using the python 
library `ctypes`.  

`Tracker.track()` returns when a new foreground window is detected or when
the current foreground window changes name.


## uploader