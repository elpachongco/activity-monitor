# 🐍⌚ Python Activity Monitor

### Summary
This python program logs user activity based on the window name that the user is currently working on. Inactivity is also monitored for each program based on input activity. The data is then forwarded to a google sheets worksheet where it can be easily seen and analyzed.

Windows only *for now?*. Makes use of Windows built-in functions.

The goal is to make this program be as invisible as possible.
### Setup

##### 1. Requirements
- Windows OS
- Python 3
- [EZsheets](https://pypi.org/project/EZSheets/) for Python
- Google api stuff (See items below) 
- Duplicate google sheets template from mine
- Get sheet link, worksheets

##### 2. Setting up Google API 
- Enabling API Access for Google Docs and Google Sheets
- pickle files
- renaming to credentials.json
- Spreadsheet design [credit]https://www.reddit.com/r/UKPersonalFinance/comments/k8pb1q/simple_google_sheets_financial_dashboard/
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

# -clear


##### Google api read/write limit

### Todo List 
- Use sheets.updateRow() instead  
- Logging system needs fixing
- Headless mode? .pyw? - Not sensible?
- Setting application to run at startup (might include making a .bat file), ; 2. Pasting it in %appdata%\Microsoft\Windows\Start Menu\Programs\Startup or %programdata%\Microsoft\Windows\Start Menu\Programs\Startup for all users.

##### DONE:  
- If day number = 0, clean. I implemented a -clear argument when running the app to set day number = 0
- Make the program survive shutdowns (impossible. but it should at least continue where it left off) **DONE**. 
- End of day data saving   
- Either continue last session or reset
- Initialization - when the script is ran, save all the current spreadsheet data then  clear it to make way for new data  
- Should ignoreList be in just one file? (Ignore list & censor list merged to one file)  
- Put all variables in one file (somewhat, shared variables now in Shelf sharedVariables)
- Make the program headless .pyw, logging... (In progress - logging DONE, headless mode not sensible atm  )
- add blacklist feature that will not list activities if a word is included in the window name  (DONE)
    ex. is Binance where the window name changes every second. This may cause the program to reach googles api limits
        another ex is when I'm watching the tech tip 🙀  
- Workaround for sites that change their page name e.g. messaging sites where   notifications change window name, trading where price is displayed every sec (Done? put those types of window into the ignore list)
- Handle Blacklisting and censoring in a file instead of in-program -DONE  
- Better google sheets dashboard. might use google data studio. (Is this a todo?)  
- ignorelist and censorlist in one file  (DONE)
- numbers on names of py files should be removed (Done, this affected importing)

##### BUGS:
- when eodARchiver is ran, activityLogger starts 1 row ahead of the intended row. **DONE**. Caused by shelf\[\'windowChangeCount\'\] += 1. Changed to shelf\[\'windowChangeCount\'\] = windowChangeCount 🤦‍♂️  
- EOD archiver and logger stops working after a few runs. Hypothesis: Probably caused by the fact that it's set to compare "previous days" in minutes. when it records 59, it stops recognizing the 01 minute as new day. **DONE**. now uses != instead of > to compare minutes/days. Who knows what could happen when it's 01-01-2022