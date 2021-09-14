import sqlite3
# from os import system

# This program accepts info about the activity then uploads it to an sqlite3 db

# -- DB DESIGN --
# TABLE: ACTIVITY_DATA
# COLUMNS: Index, Start Time, End Time, Inactivity, 
# Program Name, Window Title, Time Spent


class Uploader():

    dbPath = "./activity.db"
    tableName = "activity_data"

    # Min amount of items to upload. If this number hasn't      
    # been reached, upload() saves the item into a list
    # (class variable)
    minUpload = 1
    uploadCalls = 0
    dataBuf = []

    def __init__(self):
        # When Uploader() is initiated:
        # - Connect to the db
        # - Create the table

        self.sqlConnection = sqlite3.connect(self.dbPath)
        print("""
            CREATE TABLE IF NOT EXISTS {tn} ({colA} {colB} \
                {colC} {colD} {colE} )
            """.format(
            tn=self.tableName,
            colA="actStart TEXT",
            colB="actEnd TEXT",
            colC="inactDuration REAL",
            colD="windowName TEXT",
            colE="processName TEXT",
        ))

        self.sqlConnection.execute("""
            CREATE TABLE IF NOT EXISTS {tn} ({colA}, {colB}, \
                {colC}, {colD}, {colE})
            """.format(
            tn=self.tableName,
            colA="actStart TEXT",
            colB="actEnd TEXT",
            colC="inactDuration REAL",
            colD="windowName TEXT",
            colE="processName TEXT",
        ))

        self.sqlConnection.commit()

    def upload(self, activityDict): 
        self.uploadCalls += 1
        # self.dataBuf.append(activityDict)

        if self.uploadCalls < self.minUpload: return 
        # print("""
        #     INSERT INTO {tn} VALUES ({actStart}, {actEnd},  {inactDuration}, {windowName}, {processName})
        #     """.format(**activityDict,
        #         tn=self.tableName,
        #     ))

        self.sqlConnection.execute("""
            INSERT INTO {tn} VALUES ('{actStart}', '{actEnd}',  {inactDuration}, '{windowName}', '{processName}')
            """.format(**activityDict,
                tn=self.tableName,
            ))

        x = self.sqlConnection.execute("SELECT * from {tn}".format(tn=self.tableName))
        self.sqlConnection.commit()
        self.uploadCalls = 0
        # del self.dataBuf[:]