import unittest
import os
import sys
import sqlite3
from pathlib import Path

"""
Things to test:

- Check output of tracker (activity dict), and output of uploader (sqlite entry)
- Check if environment variable "ACTIVITY_DB" exists.

"""

# Change working directory to the parent directory (only for import)
sys.path.insert(0, os.path.abspath(".."))
import main


class TestMain(unittest.TestCase):
    def setUp(self):
        pass

    def testDbPath(self):
        """
        Test if main and uploader have the same path for db
        """
        self.dbPath = main.environ["ACTIVITY_DB"]
        self.sqlConnection = sqlite3.connect("../activity.db")
        self.assertEqual(str(self.dbPath), str(main.uploader.dbPath))

    # def testProcess(self):
    #     """
    #     Tests whether the returned activity dictionary is inputted to the
    #     sqlite database properly.
    #     Needs to have the user change the window.
    #     """

    #     activity = main.tracker.track()

    #     # Get last item from activity.db
    #     dbTail = self.sqlConnection.execute("SELECT * FROM activity_data \
    #     ORDER BY actStart DESC LIMIT 1;")

    #     self.assertEqual(activity["windowName"], dbTail.fetchone()[3])
    #     self.sqlConnection.close()


if __name__ == "__main__":
    unittest.main()
