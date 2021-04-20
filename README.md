# 🐍⌚ Python Activity Monitor

## Summary

This python program logs user activity based on the window name that the user is currently working on. Inactivity is also monitored for each program based on input activity. The data is then forwarded to a google sheets worksheet where it can be easily seen and analyzed.

Windows only *for now?*. Makes use of Windows built-in functions.

The goal is to make this program be as invisible as possible.

### Setup

#### 1. Requirements

- Windows OS
- Python 3
- [EZsheets](https://pypi.org/project/EZSheets/) for Python
- Google api stuff (See items below)
- Duplicate google sheets template from mine
- Get sheet link, worksheets

[api key setup](https://console.developers.google.com/apis/library/sheets.googleapis.com/)
[api key setup](https://console.developers.google.com/apis/library/drive.googleapis.com/)

#### 2. Setting up Google Accounts and getting API keys

- Enabling API Access for Google Docs and Google Sheets
- pickle files
- renaming to credentials.json
- Spreadsheet design [credit](https://www.reddit.com/r/UKPersonalFinance/comments/k8pb1q/simple_google_sheets_financial_dashboard/)

#### 3. Configure

- See user configurable variables
  - Set ActivMinTime to your preference or leave it default. Don't set this too low, Google API has rate limits
  - censorList
  - ignoreList

#### 4. Ignoring or censoring activity

The .txt file keywordList.txt can be filled with keywords that the program will recognize as triggers to either censor window names or ignore the activity completely.

`#ignore` - Keywords under this comment will trigger the activity logger to ignore the current activity if the keyword is found in the window name.

`#censor` - Same as ignore but for censoring. Instead of the window name, "\[redacted\]" will be put in place.

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

I personally ignore trading sites since those sites change window name too frequently (quote prices as page name). (And censor linus tech tips only fans page)

#### Running the program on startups automatically

This is pretty straightforward: Make a windows shortcut of the main-app (right click -> send to -> desktop -> create shortcut), then paste that shortcut (which will be on Desktop) to %appdata%\Microsoft\Windows\Start Menu\Programs\Startup (This can easily be accessed by pressing winKey + r then entering "shell:startup").

In my case, I had to create a .bat file so that I can run it with pipenv where ezsheets is installed.

   startuprun.bat:

      pipenv run python main-app.pyw

#### Clearing the main-app

Normally, the application keeps track of what row the latest data went in. This can be overriden by running:  

      python main-app.pyw -clear 

This will clear the row data at the start of the program.

#### Something not working?

If the application is not working, it might be caused by one or more of these:

- ezsheets is not installed
- Google credentials files are missing/incomplete
- python/py inconsistency. (needs fixing, but for now might want to change "py" to "python" in main_app -> startProgram function)

### Todo List

- Use sheets.updateRow() instead  
- Logging system needs fixing
- Just learned that using os.system() to run python programs is horrible...

#### BUGS

- App is using too much CPU! Probably needs to use updateRow() and write to list instead. Importing activity logger as a function or something like that should help as well. UPDATE: It's outrageous! 1/4th of cpu belongs to python now 😭
- App doesn't survive hybernation (probably because of the except statement in main-app). Needs a more elegant way to handle errors.
- when eodARchiver is ran, activityLogger starts 1 row ahead of the intended row. **DONE**. Caused by shelf\[\'windowChangeCount\'\] += 1. Changed to shelf\[\'windowChangeCount\'\] = windowChangeCount 🤦‍♂️  
- EOD archiver and logger stops working after a few runs. Hypothesis: Probably caused by the fact that it's set to compare "previous days" in minutes (minutes for testing purposes). When it records 59, it stops recognizing the 01 minute as new day. **DONE**. now uses != instead of > to compare minutes/days. Who knows what could happen when it's 01-01-2022.

##### Contributing

I've never experienced this but if you somehow saw this repo, tried the program, saw the mess, and now want to contribute, just make sure to enable keywordList.txt in gitignore.
