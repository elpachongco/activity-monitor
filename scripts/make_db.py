import sqlite3
import os
from pathlib import Path

from dotenv import load_dotenv


TABLE_COLUMNS = ["startMS", "endMS", "lengthMS", "idleMS", "windowName", "processName"]
TABLE_NAME = "activity_data"


def createDB(dbPath, tableName):
    """Creates a database if it doesn't exist.

    Columns:
    ["startMS", "endMS", "lengthMS", "idleMS", "windowName", "processName"]
    Types:
    ["INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "TEXT"]
    """
    con = sqlite3.connect(dbPath)
    cur = con.cursor()

    """
    https://www.sqlite.org/lang_createtable.html#rowid
    """

    cur.execute(
        """
	    CREATE TABLE IF NOT EXISTS {tableName}
	    ({start} INTEGER PRIMARY KEY, {end} INTEGER, {length} INTEGER, {idle} INTEGER, {window} TEXT, {process} TEXT)
	    """.format(
            tableName=tableName,
            start=TABLE_COLUMNS[0],
            end=TABLE_COLUMNS[1],
            length=TABLE_COLUMNS[2],
            idle=TABLE_COLUMNS[3],
            window=TABLE_COLUMNS[4],
            process=TABLE_COLUMNS[5],
        )
    )
    con.commit()


def main():
    load_dotenv()
    DB_NAME = os.getenv("DB_NAME")
    DB_PATH = DB_NAME

    if DB_NAME == None or DB_PATH == None:
        raise

    createDB(DB_PATH, TABLE_NAME)


if __name__ == "__main__":
    main()
