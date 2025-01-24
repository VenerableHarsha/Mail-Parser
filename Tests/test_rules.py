import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json
from Backend.rules import (
    load_rules_from_json,
    fetch_emails_from_db,
    update_emails_in_db,
    update_emails_in_service,
    match_condition,
    perform_action
)
class TestEmailRuleProcessor(unittest.TestCase):

    @patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps({
        "rules": [
            {
                "type": "All",
                "conditions": [
                    {"field": "From", "predicate": "Contains", "value": "test@example.com"},
                    {"field": "Subject", "predicate": "Equals", "value": "Test Subject"}
                ],
                "actions": ["Mark as Read"]
            }
        ]
    })))
    def test_load_rules_from_json(self):
        """Test loading rules from the JSON file."""
        rules = load_rules_from_json()
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules["rules"]), 1)
        self.assertEqual(rules["rules"][0]["type"], "All")
        self.assertEqual(rules["rules"][0]["conditions"][0]["field"], "From")
        self.assertEqual(rules["rules"][0]["actions"][0], "Mark as Read")

    def test_match_condition_equals(self):
        """Test matching condition where predicate is Equals."""
        email = {
            "id": 1,
            "From": "test@example.com",
            "Subject": "Test Subject",
            "Message": "Hello",
            "Received Date/Time": "2025-01-25 10:00:00",
            "labels": "",
            "read": False
        }

        condition = {"field": "From", "predicate": "Equals", "value": "test@example.com"}
        result = match_condition(email, condition)
        self.assertTrue(result)

    def test_match_condition_contains(self):
        """Test matching condition where predicate is Contains."""
        email = {
            "id": 1,
            "From": "test@example.com",
            "Subject": "Test Subject",
            "Message": "Hello",
            "Received Date/Time": "2025-01-25 10:00:00",
            "labels": "",
            "read": False
        }

        condition = {"field": "Subject", "predicate": "Contains", "value": "Test"}
        result = match_condition(email, condition)
        self.assertTrue(result)

    def test_perform_action_mark_as_read(self):
        """Test performing 'Mark as Read' action."""
        email = {
            "id": 1,
            "From": "test@example.com",
            "Subject": "Test Subject",
            "Message": "Hello",
            "Received Date/Time": "2025-01-25 10:00:00",
            "labels": "",
            "read": False
        }
        perform_action(email, "Mark as Read")
        self.assertTrue(email["read"])

    def test_perform_action_move_to_folder(self):
        """Test performing 'Move to' folder action."""
        email = {
            "id": 1,
            "From": "test@example.com",
            "Subject": "Test Subject",
            "Message": "Hello",
            "Received Date/Time": "2025-01-25 10:00:00",
            "labels": "",
            "read": False
        }
        perform_action(email, "Move to Important")
        self.assertEqual(email["labels"], "Important")

    @patch('sqlite3.connect')
    def test_fetch_emails_from_db(self, mock_connect):
        """Test fetching emails from the database."""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 'test@example.com', 'Test Subject', 'Hello', '2025-01-25 10:00:00', '', False)
        ]
        emails = fetch_emails_from_db()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0][1], "test@example.com")

    @patch('sqlite3.connect')
    def test_update_emails_in_db(self, mock_connect):
        """Test updating emails in the database."""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        emails = [{"id": 1, "read": True, "labels": "Important"}]
        update_emails_in_db(emails)
        mock_cursor.execute.assert_called_with(
    """
            UPDATE emails 
            SET read = ?, labels = ? 
            WHERE id = ?
        """,
    (True, 'Important', 1)
)


if __name__ == '__main__':
    unittest.main()
