import unittest
from unittest.mock import MagicMock
from Backend.email_fetching import fetch_emails
from Backend.database import insert_email
import sqlite3 
class TestEmailFetcher(unittest.TestCase):

    def test_fetch_emails(self):
        # Mock the Gmail API service object
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test_id'}]
        }
        mock_service.users().messages().get().execute.return_value = {
            'id': 'test_id',
            'payload': {
                'headers': [{'name': 'From', 'value': 'test_sender@example.com'},
                            {'name': 'Subject', 'value': 'Test Subject'}],
                'parts': [{
                    'mimeType': 'text/plain',
                    'body': {'data': 'VGVzdCBib2R5'}  # base64-encoded 'Test body'
                }]
            },
            'internalDate': '1642358400000'  # Timestamp (2025-01-23 12:00:00)
        }

        # Call the fetch_emails function
        fetch_emails(mock_service)

        # Verify that the email was inserted into the database
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE id='test_id'")
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result, "Email not inserted into the database")
        self.assertEqual(result[1], "test_sender@example.com", "Sender mismatch")
        self.assertEqual(result[2], "Test Subject", "Subject mismatch")
        self.assertEqual(result[3], "Test body", "Body mismatch")

if __name__ == "__main__":
    unittest.main()
