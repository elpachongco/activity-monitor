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

#Get spreadsheet data
sharedVariable = shelve.open("sharedVariable", "r")
spreadsheetID = sharedVariable["spreadsheetID"]  
spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Create the spreadsheet object
currentdaySheet = sharedVariable['currentdaySheet']
archiveSheet = sharedVariable['archiveSheet']   
calculationSheet = sharedVariable['calculationSheet']
dayNumber = sharedVariable['dayNumber']
sharedVariable.close()

currentdaySheet = spreadsheet[currentdaySheet]
archiveSheet = spreadsheet[archiveSheet]
calculationSheet = spreadsheet[calculationSheet]

# Get necessary data and put them to the archival sheet
class DailyData:   
    # this class accepts two lists:
    # Origin, and Destination.
    # both lists contain 1. sheet object, and 2. The location of the cell in the sheet 

    # Class Variables 
    archiveSheet = ''
    calculationSheet = ''
    rowNumber = '' 

    # OriginCell accepts a list, destinationCell accepts cell location info ['A3']
    def __init__(self, originCell, destinationCell):
        self.originCell = originCell
        self.destinationCell = destinationCell
        
    def archive(self):    # Get the data & write it 
        # sheet object
        originCellSheet = self.calculationSheet
        # cell location  
        originCellLoc = self.originCell

        destinationCellSheet = self.archiveSheet  # Class variable
        destinationCellLoc = self.destinationCell[0] + str(rowNumber)
        
        # title of the sheets
        originSheetTitle = originCellSheet.title 
        destinationSheetTitle = destinationCellSheet.title

        # spreadsheet object
        spreadsheet = originCellSheet.spreadsheet

        # Write. 
        spreadsheet[destinationSheetTitle][destinationCellLoc] = spreadsheet[originSheetTitle][originCellLoc] s

# Data that  will be archived at the End Of Day
inputStartRow = 2  
rowNumber = dayNumber + inputStartRow   # row number for archive sheet

start = time.time()

DailyData.archiveSheet = archiveSheet
DailyData.calculationSheet = calculationSheet
DailyData.rowNumber = rowNumber


# archive function takes care of the row of the destination cell
# But it's okay to put there 
cellLocations = [
                # [Origin, Destination]
                ['A3', 'A2'], # Data validity
                ['A5', 'A3'], # Total Inactivity
                ['A7', 'A4'], # Total Activity
                ['A9', 'A5'], # Unique windows
                ['A13', 'A6'] # Average time spent
                ]

for item in cellLocations:
    archiveItem = DailyData(item[0], item[1])
    archiveItem.archive()

end = time.time()

print(end - start)


# columnsToClear = ['A', 'B','E','F','G']
# # Clean currentday spreadsheet, remove entries then restore row 1
# for index, columnLetter in enumerate(columnsToClear):
#     # Get Column Number
#     columnNumber = ezsh.getColumnNumberOf(columnLetter)

#     # Get first item of that Column
#     # Store it 
#     columnFirstRow = currentdaySheet[columnNumber, 1],
#     # time.sleep(3)
#     # Clear Column
#     currentdaySheet.updateColumn(columnNumber, columnFirstRow)

# print("Daily Data cleared & restored ")

# # exit
# sys.exit()