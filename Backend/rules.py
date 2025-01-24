import json
import os
from datetime import timedelta, datetime
import sqlite3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

RULES_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'rules.json')
)

DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'emails.db')
)

def perform_action(email, action):
    if action == "Mark as Read":
        print("performing mark as read")
        email["read"] = True
        print(f"Email {email['id']} marked as read.")
    elif action == "Mark as Unread":
        print("performing mark as unread")
        email["read"] = False
        print(f"Email {email['id']} marked as unread.")
    elif action.startswith("Move to"):
        folder = action.split("Move to ")[1]
        print("perform action",folder)
        email["labels"] = folder
        print(email)
        print(f"Email {email['id']} moved to {folder}.")

def match_condition(email, condition):
    field = condition["field"]
    predicate = condition["predicate"]
    value = condition["value"]

    if field not in email:
        print(field,"not in ",email)
        print("returning false as no field")
        return False

    email_value = email[field]

    if isinstance(email_value, str):
        if predicate == "Contains" and value in email_value:
            return True
        elif predicate == "Does not Contain" and value not in email_value:
            return True
        elif predicate == "Equals" and value == email_value:
            return True
        elif predicate == "Does not Equal" and value != email_value:
            return True

    if field == "received":
        email_date = datetime.strptime(email_value, "%Y-%m-%d %H:%M:%S")
        days = int(value)
        compare_date = datetime.now() - timedelta(days=days)

        if predicate == "Less than" and email_date < compare_date:
            return True
        elif predicate == "Greater than" and email_date > compare_date:
            return True

    return False

def load_rules_from_json():
    """Load rules from the JSON file."""
    if not os.path.exists(RULES_FILE):
        print(f"{RULES_FILE} not found.")
        return None

    with open(RULES_FILE, "r") as file:
        rules_data = json.load(file)

    return rules_data

def fetch_emails_from_db():
    """Fetch emails from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()

    conn.close()
    return emails

def update_emails_in_db(emails):
    """Update emails in the database with the latest status and folder changes."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for email in emails:
        cursor.execute("""
            UPDATE emails 
            SET read = ?, labels = ? 
            WHERE id = ?
        """, (email["read"], email["labels"], email["id"]))

    conn.commit()
    conn.close()

def update_emails_in_service(emails, service):
    """
    Update email status (read/unread, labels) and handle special cases like Trash for Gmail.
    """
    system_labels = {
        "CATEGORY_PERSONAL",
        "CATEGORY_UPDATES",
        "CATEGORY_FORUMS",
        "CATEGORY_PROMOTIONS",
        "CATEGORY_SOCIAL",
    }

    for email in emails:
        email_id = email["id"]
        print(f"Processing email: {email_id} - {email}")

        # Mark as read/unread in Gmail
        if email.get("read", False):  # Default to False if "read" is not specified
            try:
                print(f"Marking email {email_id} as read...")
                response = service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                print(f"Response for marking as read: {response}")
            except HttpError as error:
                print(f"Error while marking email {email_id} as read: {error}")
        else:
            try:
                print(f"Marking email {email_id} as unread...")
                response = service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'addLabelIds': ['UNREAD']}
                ).execute()
                print(f"Response for marking as unread: {response}")
            except HttpError as error:
                print(f"Error while marking email {email_id} as unread: {error}")

        # Special case: Move email to Trash
        if email.get("labels") == "TRASH":
            try:
                print(f"Moving email {email_id} to Trash...")
                response = service.users().messages().trash(userId='me', id=email_id).execute()
                print(f"Response for moving to Trash: {response}")
            except HttpError as error:
                print(f"Error while moving email {email_id} to Trash: {error}")
            continue  # Skip other label modifications for emails moved to Trash

        labels_to_add = []

        # Check if labels exist in the email and handle potential cases like None or empty strings
        labels = email.get("labels", "").split(",") if email.get("labels") else []

        # Iterate over the labels and strip extra spaces
        for label in labels:
            label = label.strip()  # Remove extra spaces around labels
            if label and label not in system_labels:  # Add label only if it's not empty and not a system label
                labels_to_add.append(label)

        # Optionally, log the labels to check what's being processed
        if labels_to_add:
            print(f"Labels to add: {labels_to_add}")
        else:
            print("No labels to add.")


        if labels_to_add:
            print("adding labels")
            try:
                print(f"Adding labels {labels_to_add} to email {email_id}...")
                response = service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'addLabelIds': labels_to_add}
                ).execute()
                print(f"Response for adding labels: {response}")
            except HttpError as error:
                print(f"Error while adding labels to email {email_id}: {error}")

        labels_to_remove = [
            label.strip()
            for label in email.get("labels", "").split(",")
            if label.strip() in system_labels and label.strip() != "TRASH"
        ]

        if labels_to_remove:
            try:
                print(f"Removing labels {labels_to_remove} from email {email_id}...")
                response = service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'removeLabelIds': labels_to_remove}
                ).execute()
                print(f"Response for removing labels: {response}")
            except HttpError as error:
                print(f"Error while removing labels from email {email_id}: {error}")

        print(f"Finished processing email {email_id}.\n")


def process_rules(service):
    """Process rules, apply them to the emails, and update both the database and the email service."""
    # Step 1: Load the rules from the rules.json file
    rules = load_rules_from_json()

    if not rules:
        print("No rules found.")
        return

    # Step 2: Fetch emails from the database
    emails = fetch_emails_from_db()  # Fetch emails stored in your database
    emails = [
    {
        "id": email[0],
        "From": email[1],
        "Subject": email[2],
        "Message": email[3],
        "Received Date/Time": email[4],
        "labels": email[5],
        "read":email[6],
    }
    for email in emails
]

    if not emails:
        print("No emails found in the database.")
        return

    for rule in rules.get("rules", []):
        print(rule)
        rule_type = rule["type"]
        conditions = rule["conditions"]
        actions = rule["actions"]

        for email in emails:
            print(email)
            if rule_type == "All":
                print("hello")
                # Apply 'All' condition: all conditions must be met
                if all(match_condition(email, condition) for condition in conditions):
                    print("match success for all condition")
                    for action in actions:
                        perform_action(email, action)
            elif rule_type == "Any":
                # Apply 'Any' condition: at least one condition must be met
                if any(match_condition(email, condition) for condition in conditions):
                    for action in actions:
                        print("hi")
                        perform_action(email, action)

    # Step 4: After applying the rules, update the emails in the database and service
    update_emails_in_db(emails)  # Update the emails in the database
    update_emails_in_service(emails,service)  # Apply changes to the main email service (e.g., Gmail API)

    print("Rules applied successfully.")
