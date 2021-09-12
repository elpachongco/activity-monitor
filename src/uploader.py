import sqlite3
# This program accepts info about the activity then uploads it to an sqlite3 db
# ----------------------------------------------------------------------------- 
from os import system

class Uploader():

    dbPath = "../example.db"
    minUpload = 1

    def __init__(self):
        pass

    def upload(self, a): 
        #system("cls")
        # print(f"Uploader: {a}")
        print(f"{a['windowName']} | Duration: {a['actEnd'] - a['actStart']} | Inact: {a['inactDuration']}")


