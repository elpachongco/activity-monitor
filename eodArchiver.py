# This program is responsible for handling end of days.
# This includes
# Clearing the daily cells
# Refilling back the row1 (no clue if there is a better way to do this other than manually)
# Then saving it to a cell in the archival worksheet

import time
import ezsheets as ezsh
import sys
import shelve

print("End of Day Archiver - Active")

# Get spreadsheet data
sharedVariable = shelve.open("sharedVariable", "r")
spreadsheetID = sharedVariable["spreadsheetID"]  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Create the spreadsheet object
currentdaySheet = sharedVariable['currentdaySheet']
archiveSheet = sharedVariable['archiveSheet']   
# calculationSheet = sharedVariable['calculationSheet']
sharedVariable.close()

# columns to clear are the same rows that will be 
columnsToClear = ['A', 'B','E','F','G']

rowContents = []
# Get contents of row 1 for columns that will be cleared
for item in columnsToClear:
    columnNumber = ezsh.getColumnNumberOf(item)
    rowContents.append(spreadsheet[currentdaySheet][columnNumber, 1])
    
# Get necessary data and put them to the archival sheet 
dictOfArchivalData = {"Total InactivityT": 0, "Total ActivityT": 0, "Date": 0, "Average Time spent": 0, "Data Validity": 0,}

# Clear the listed columns 
print("clearing columns")
time.sleep(5)

# Restore row 1 headers
for index, item in enumerate(columnsToClear):
    columnNumber = ezsh.getColumnNumberOf(item)
    spreadsheet[currentdaySheet][columnNumber, 1] = rowContents[index]

# exit
sys.exit()