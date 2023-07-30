import logging
import sqlite3

# This program accepts info about the activity then uploads it to an sqlite3 db

logger = logging.getLogger()


class Uploader:
    # Min amount of items to upload. If this number hasn't
    # been reached, upload() saves the item into a list
    # (to be implemented).
    minUpload = 1

    def __init__(self, dbPath, tableName):
        # - Connect to the db
        # - Create the table if it doesn't exist
        # Table will have column name same as
        # Dictionary keys

        self.__dbPath = dbPath
        self.tableName = tableName
        self.sqlConnection = sqlite3.connect(self.__dbPath)
        self.sqlCursor = self.sqlConnection.cursor()

    def upload(self, activityDict):
        self.sqlCursor.execute(
            """
            INSERT INTO {tn} VALUES (:startMS, :endMS, :lengthMS, :idleMS, :windowName,
                    :processName)
            """.format(
                tn=self.tableName
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
