import unittest
import os
from Backend.authentication import authenticate_gmail
from Backend.database import init_db, insert_email
from Backend.email_fetching import fetch_emails
import sqlite3

class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Initialize the database
        init_db()

    def test_integration(self):
        # Authenticate Gmail and fetch emails
        service = authenticate_gmail()
        fetch_emails(service, max_results=1)

        # Check if the email is inserted in the database
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result, "Email not inserted into the database")
        self.assertEqual(result[1], "test_sender@example.com", "Sender mismatch")
        self.assertEqual(result[2], "Test Subject", "Subject mismatch")
        self.assertEqual(result[3], "Test body", "Body mismatch")

if __name__ == "__main__":
    unittest.main()
