import sqlite3

# This program accepts info about the activity then uploads it to an sqlite3 db

class Uploader():

    dbPath = "./activity.db"
    tableName = "activity_data"

    # Min amount of items to upload. If this number hasn't      
    # been reached, upload() saves the item into a list
    # (to be implemented).
    minUpload = 1

    def __init__(self):
        # - Connect to the db
        # - Create the table if it doesn't exist
        # Table will have column name same as 
        # Dictionary keys

        self.sqlConnection = sqlite3.connect(self.dbPath)

        self.sqlConnection.execute("""

            CREATE TABLE IF NOT EXISTS {tn} 
            ({colA}, {colB}, {colC}, {colD}, {colE})

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

        self.sqlConnection.execute("""

            INSERT INTO {tn} VALUES ('{actStart}', '{actEnd}',  {inactDuration},
            '{windowName}', '{processName}')

            """.format(
                tn=self.tableName,

                # Unpacks the dictionary. Makes keys behave like 
                # variables in the format string.
                **activityDict
        ))

        self.sqlConnection.commit()