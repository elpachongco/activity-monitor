# 🐍⌚ Python Activity Monitor

### Summary
This python program logs user activity based on the window name that the user is currently working on. Inactivity is also monitored for each program based on input activity. The data is then forwarded to a google sheets worksheet where it can be easily seen and analyzed.

Windows only *for now*. Makes use of Windows built-in functions.
### Setup

##### 1. Requirements
- Windows OS
- Python 3
- [EZsheets](https://pypi.org/project/EZSheets/) for Python
- Google api stuff (See items below) 
- Duplicate google sheets template from mine
- Get sheet link, worksheets

##### 2. Setting up Google 
- Enabling API Access for Google Docs and Google Sheets
- pickle files
- renaming to credentials.json
- Spreadsheet design [credit]
- 
##### 3. Configure
- See user configurable variables
    - Set ActivMinTime to your preference or leave it default. Don't set this too low, Google API has rate limits
    - censorList
    - ignoreList

##### 4. censorList.txt & ignoreList.txt
The .txt files censorList.txt & ignoreList.txt can be filled with keywords that that the program will recognize as triggers to either censor window names or ignore the activity completely.

censorList - Sites that will be censored. Instead of the window name, "[redacted]" will be put in place.
ignoreList - Sites that will not be written to the spreadsheet.

- One keyword per line. Items should be separated by a newline (enter). 
- Not case sensitive.
- Spaces are ignored.  
example content for each file:  

        censorList.txt:  
        Search
        Mail
       
        ignoreList.txt:
        USDT
        BTC
        USD
        ●

I personally ignore trading sites since those sites change window name too frequently (quote prices as page name).
I also ignore the character "●" for VSCODE. - This needs UTF-16 encoding.


##### Google api read/write limit