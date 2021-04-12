# This python script controls the whole program. 
# Responsible for initiating the programs

import time, os

programRunStart = time.localtime(time.time()).tm_mday # Get current day number/date 

runPrograms = False
newDay = False


previousDay = programRunStart  # get current day as previous day when program starts

with open("runProgram.txt", "w") as runProgram:
    x= runProgram

x.write("False")

while True:  
    dateToday = time.localtime(time.time()).tm_mday

    # If today is the same day as the last recorded day    
    if previousDay == dateToday:
        
        newDay = False 

    # If today is different from the previous recorded day
    elif dateToday > previousDay:
        previousDay = dateToday 
        newDay = True