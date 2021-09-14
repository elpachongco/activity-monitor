# ⌚ Activity Tracker

This program logs user activity based on the window name that the user is
currently working on. Inactivity is also monitored for each program based on
input activity. The data is then uploaded to an sqlite database where 

Windows only *for now?*. Makes use of Windows built-in functions.

This program is intended to be as invisible as possible.

### Setup

#### 1. Requirements

- Windows OS
- Python 3.7

#### 3. Configure

- See user configurable variables
  - Set ActivMinTime to your preference or leave it default. Don't set this too
  low, Google API has rate limits
 - censorList
  - ignoreList

#### 4. Ignoring or censoring activity

The .txt file keywordList.txt can be filled with keywords that the program will
recognize as triggers to either censor window names or ignore the activity
completely.

`#ignore` - Keywords under this comment will trigger the activity logger to
ignore the current activity if the keyword is found in the window name.

`#censor` - Same as ignore but for censoring. Instead of the window name,
"\[redacted\]" will be put in place.

- One keyword per line. Items should be separated by a newline (enter).
- Not case sensitive.
- Spaces before and after the keywords are ignored.  
example content:
- Lines starting with the hash symbol (#) are considered comments

      keywordList.txt:

      #ignore
      USDT
      BTC
      USD

      #censor
      only fans
      linus tech tips

I personally ignore trading sites since those sites change window name too
frequently (quote prices as page name). (And censor linus tech tips only fans
page)

#### Running the program on startups automatically

This is pretty straightforward: Make a windows shortcut of the main-app (right
click -> send to -> desktop -> create shortcut), then paste that shortcut (which
will be on Desktop) to %appdata%\Microsoft\Windows\Start Menu\Programs\Startup
(This can easily be accessed by pressing winKey + r then entering
"shell:startup").

In my case, I had to create a .bat file so that I can run it with pipenv where
ezsheets is installed.

   startuprun.bat:

      pipenv run python main-app.pyw

#### Clearing the main-app

Normally, the application keeps track of what row the latest data went in. This
can be overriden by running:  

python main-app.pyw -clear 

This will clear the row data at the start of the program.

#### Something not working?

If the application is not working, it might be caused by one or more of these:

- ezsheets is not installed
- Google credentials files are missing/incomplete
 - python/py inconsistency.
(needs fixing, but for now might want to change "py" to "python" in main_app ->
startProgram function)

### TODO 
- Make it less resource intensive 
      - Introduce delay / sampling time for the activity logger to prevent
      unnecesary looping
 - The windows API used to fetch inactivity / window
      name is too heavy, 
- Replace google sheets with a proper database. Use google sheets only as a backup
      idea: dashboard should fetch local data from local db and data from
      google sheets
 - also make a better db design than the google sheets ver
      - import sqlite3?
- better project file structure
      Every file is mixed up and there's no description of what each file does
      - `docs` directory, `src`, 
- Local dashboard
- Code cleanup 
      - for reliability (this program might run 24/7)
      - No more using a shared variable. 
      - Make it more modular for upgradability and ease of porting to other OS
- Create a configuration file
- Better portability for windows. Currently, the process name lookup involves
using a command line tool which I am not sure exists on older platforms. 

#### BUGS