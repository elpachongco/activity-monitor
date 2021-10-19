# Activity Tracker Documentation

This document serves as an overview of the activity tracker system. 
The whole program communicates using `main.py` & the dictionary `activity`.

## main

`main.py` serves as controller for the programs. It imports the scripts in 
`./src` which contain classes.

It contains a loop that calls the activity tracker. The tracker tracks two 
things: the current foreground window & the amount of time the user is
inactive. It returns when the foreground window changes name. this usually
means the user has changed windows. Though sometimes this is not the case -
some websites and applications change their window name from time to time.

The return value is the `activity` dictionary which is then passed to the 
uploader. The uploader uploads the data to `activity.db` then returns.

This repeats until the program is exited.

## activity 

`activity` is a dictionary that **must** contain the keys: 

    "processName", "windowName", "actStart", "actEnd", "inactDuration"

All the values of the keys are of type String. 

(string) `actStart` and `actEnd` contain the start time and end of each
activity.  Both are in iso8601 format `YYYY-MM-DD HH-MM-SS.SSS`. SQLite uses
this format for its date time functions. 

(float) `inactDuration` is the total time in seconds of the user's 
inactivity during the activity. 

(string) `processName` is the name of the process that is running the 
foreground window.

(string) `windowName` is the name of the foreground window.

`activity` is passed to uploader as a dictionary of strings. Any key that 
contains non-string values is converted into strings.

## activity.db

`activity.db` is the sqlite3 database file that is used to store all the data
collected by the program. It contains the columns: 

```
'actStart' TEXT, 'actEnd' TEXT, 'inactDuration' REAL, 
'windowName' TEXT, 'processName' TEXT
```

## tracker

`tracker.py` contains the class `Tracker()`. Its job is to call the OS API to
do the following things:

- get the name of the foreground window, 
- get the name of the process that runs the said window, 
- Detect user inactivity by getting the last time input was made.

Right now, the best solution is to call the Windows API using the python 
library `ctypes`.  

`Tracker.track()` returns when a new foreground window is detected or when
the current foreground window changes name.


## uploader

`uploader.py` handles the uploading of data to the sqlite db. 

Upon initialization, it connects to the database file `activity.db`. If the file 
doesn't exist, sqlite3 creates it. `Uploader()` checks `activity.db` if it 
contains the necessary table and columns. If not, `Uploader()` creates it.

It stays connected as long as `main.py` is running. It uploads and commits 
changes whenever the `Uploader.upload()` called.

## Things to implement

- Configuration system
- Mechanism against programs that change window names too frequently.
