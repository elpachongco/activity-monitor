# This program is responsible for handling end of days.
# This includes clearing the daily cells,
# Refilling back the row1 (no clue if there is a better way to do this other than manually)

import time, sys
import ezsheets as ezsh, shelve

#Get spreadsheet data
with shelve.open("sharedVariable") as sharedVariable:
	spreadsheetID = sharedVariable["spreadsheetID"]  
	currentdaySheet = sharedVariable['currentdaySheet']
	archiveSheet = sharedVariable['archiveSheet']   
	calculationSheet = sharedVariable['calculationSheet']
	dayNumber = sharedVariable['dayNumber']

spreadsheet = ezsh.Spreadsheet(spreadsheetID)   # Create the spreadsheet object

currentdaySheet = spreadsheet[currentdaySheet]
archiveSheet = spreadsheet[archiveSheet]
calculationSheet = spreadsheet[calculationSheet]

# Get necessary data and put them to the archival sheet
class DailyData:   
	# These variables are required. 
	# OriginCell accepts a list, destinationCell accepts cell location info ['A3']
	def __init__(self, originCell, destinationCell):
		self.originCell = originCell
		self.destinationCell = destinationCell

	def archive(self):    # Get the data & write it 
		originCellLoc = self.originCell
		destinationCellLoc = self.destinationCell[0] + rowNumber

		# Write. 
		if calculationSheet[originCellLoc][0] != "#":		
			archiveSheet[destinationCellLoc] = calculationSheet[originCellLoc]	# Prevents writing #ERRORS

	def writeDate(self):
		dateLoc = dateColumn + rowNumber
		archiveSheet[dateLoc] = time.time()

dateColumn = 'A'
inputStartRow = 2  # row number to start the input
rowNumber = str(dayNumber + inputStartRow - 1)   # row number for archive sheet

print(f"Saved to row Number: {rowNumber}") 

cellLocations = [
					 # [Origin, Destination]
					 ['A5', 'C2'], # Total Inactivity
					 ['A7', 'D2'], # Total Activity
					 ['A3', 'E2'], # Data validity
					 ['A13', 'F2'],# Average time spent
					 ['A11', 'G2'], # Unique windows
					 ['A17', 'H2'], # Most common window name
					 ['A19', 'I2'], # Most common process name
					 ]

for item in cellLocations:
	archiveItem = DailyData(item[0], item[1])
	archiveItem.archive()
archiveItem.writeDate()

# Clean currentday spreadsheet, remove entries then restore row 1
columnsToClear = ['A', 'B','E','F','G']
for index, columnLetter in enumerate(columnsToClear):
	columnNumber = ezsh.getColumnNumberOf(columnLetter)
	columnFirstRow = currentdaySheet[columnNumber, 1],
	currentdaySheet.updateColumn(columnNumber, columnFirstRow)
