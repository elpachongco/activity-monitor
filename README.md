# ⌚ Activity Tracker

This program logs user activity based on the foreground window name. 
Inactivity is also monitored for each program based on input activity. 
The data is uploaded to an sqlite database. 

## Setup

### Usage Requirements

- Windows OS
- Python (tested on 3.7 & 3.9) 
- Pipenv. Install: `pip install pipenv`

To get the required project dependencies:
```bat
cd path\to\activity-monitor
pipenv sync 
```
You can now run `main.py`.

### Running the program on startups automatically

Make a windows shortcut of the `startup.bat` (right
click -> send to -> desktop -> create shortcut), then paste that shortcut (which
will be on Desktop) to %appdata%\Microsoft\Windows\Start Menu\Programs\Startup
(This can easily be accessed by pressing the `Windows Key + r` then entering
`shell:startup`). A file explorer window will show up. Paste the shortcut. 
The program will now run every startup.

## File Structure 

```sh
.
│   .gitignore
│   activity.db # Generated SQL db
│   CHANGELOG.md
│   main.py # Main controller
│   Pipfile
│   Pipfile.lock
│   README.md
│   startup.bat
│
├───config
│       config.py
│       keywords.py
│
├───dashboard # Experimental dashboard
│
├───docs
│       doc.md
│
└───src # Files used by main.py 
        tracker.py
        uploader.py

```
## Bugs

Program hasn't been tested extensively.

1. No mechanism against programs or webpages that change window names

## Documentation

See [docs](./docs/). 

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
