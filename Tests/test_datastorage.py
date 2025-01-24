import sqlite3
import unittest

class TestDatabase(unittest.TestCase):
    DATABASE_FILE = 'emails.db'

    def test_display_all_data(self):
        """
        Test to fetch and display all data from the database.
        """
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.DATABASE_FILE)
            cursor = conn.cursor()

            # Fetch all data from the emails table
            cursor.execute("SELECT * FROM emails")
            rows = cursor.fetchall()

            # Display the data
            print("\n--- Email Data in Database ---")
            for row in rows:
                print(row)

            # Assert that the database contains data
            self.assertGreater(len(rows), 0, "Database is empty!")
        
        except sqlite3.Error as e:
            self.fail(f"Database error occurred: {e}")
        
        finally:
            # Close the connection
            if conn:
                conn.close()

if __name__ == "__main__":
    unittest.main()
