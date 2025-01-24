import unittest
import sqlite3
from Backend.database import init_db, insert_email

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Initialize the database
        init_db()

    def test_insert_email_with_labels(self):
        # Insert a test email with labels
        test_labels = "Inbox, Important"
        insert_email("test_id", "test_sender@example.com", "Test Subject", "Test body", "2025-01-23 12:00:00", test_labels)

        # Verify if the email was inserted correctly, including labels
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE id='test_id'")
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result, "Email not inserted into the database")
        self.assertEqual(result[1], "test_sender@example.com", "Sender mismatch")
        self.assertEqual(result[2], "Test Subject", "Subject mismatch")
        self.assertEqual(result[3], "Test body", "Body mismatch")
        self.assertEqual(result[4], "2025-01-23 12:00:00", "Received date mismatch")
        self.assertEqual(result[5], "Inbox, Important", "Labels mismatch")  # Verify labels

if __name__ == "__main__":
    unittest.main()
