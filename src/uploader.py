import sqlite3
import logging

# This program accepts info about the activity then uploads it to an sqlite3 db

logger = logging.getLogger()

class Uploader:
    TABLENAME = "activity_data"

    # Min amount of items to upload. If this number hasn't
    # been reached, upload() saves the item into a list
    # (to be implemented).
    minUpload = 1

    def __init__(self, dbPath):
        # - Connect to the db
        # - Create the table if it doesn't exist
        # Table will have column name same as
        # Dictionary keys

        self.__dbPath = dbPath
        self.sqlConnection = sqlite3.connect(self.__dbPath)
        self.sqlCursor = self.sqlConnection.cursor()

        self.sqlCursor.execute(
            """

            CREATE TABLE IF NOT EXISTS {tn}
            ({colA}, {colB}, {colC}, {colD}, {colE})

            """.format(
                tn=self.TABLENAME,
                colA="actStart TEXT",
                colB="actEnd TEXT",
                colC="inactDuration REAL",
                colD="windowName TEXT",
                colE="processName TEXT",
            )
        )

        self.sqlConnection.commit()

    def upload(self, activityDict):
        self.sqlCursor.execute(
            """

            INSERT INTO {tn} VALUES (:actStart, :actEnd,  :inactDuration,
            :windowName, :processName)

            """.format(
                tn=self.TABLENAME
            ),
            activityDict,
        )

        self.sqlConnection.commit()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.sqlCursor.close()
        if isinstance(exc_value, Exception):
            self.sqlConnection.rollback()
        else:
            self.sqlConnection.commit()
        self.sqlConnection.close()
