# ⌚ Activity Tracker

This program logs user activity based on the foreground window name. 
Inactivity is also monitored for each program based on input activity. The data is 
uploaded to an sqlite database. 

## Setup


### Requirements

- Windows OS
- Python (tested on 3.7 & 3.9)


### Running the program on startups automatically

#### Windows
This is pretty straightforward: Make a windows shortcut of the main-app (right
click -> send to -> desktop -> create shortcut), then paste that shortcut (which
will be on Desktop) to %appdata%\Microsoft\Windows\Start Menu\Programs\Startup
(This can easily be accessed by pressing the Windows Key + r then entering
"shell:startup"). A file explorer window will show up. Paste the shortcut.

In my case, I had to create a .bat file so that I can run it with pipenv where
ezsheets is installed.

startuprun.bat:

      pipenv run python main-app.pyw

## BUGS

None known yet. Program hasn't been tested extensively.

## File Structure 

```
.
│   .gitignore
│   activity.db
│   CHANGELOG.md
│   main.py
│   Pipfile
│   Pipfile.lock
│   README.md       
│   startuprun.bat
│
├───config
│       config.py
│       keywords.py
│    
│
├───docs
│       structure.md
│
└───src
      tracker.py
      uploader.py
```

## TODO 
- Local dashboard
- Code cleanup 
 - for reliability (this program might run 24/7)
 - Create a configuration file
 - Better portability for windows. Currently, the process name lookup involves
      using a command line tool which I am not sure exists on older platforms. 
- Documentation
- Tests
- Port to Linux
