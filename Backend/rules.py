import json
import os
from datetime import timedelta, datetime
import sqlite3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import copy
from datetime import datetime, timedelta
RULES_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'rules.json')
)

DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'emails.db')
)

    
def perform_action(email, action):
    email_copy = copy.deepcopy(email) 
    print(action, "is being done")
    if action == "Mark as Read":
        print("performing mark as read")
        email_copy["read"] = True
        print(f"Email {email['id']} marked as read.")
    elif action == "Mark as Unread":
        print("performing mark as unread")
        email_copy["read"] = False
        print(f"Email {email['id']} marked as unread.")
    elif action.startswith("Move to"):
        folder = action.split("Move to ")[1]
        print("perform action",folder)
        if folder=='IMPORTANT':
            folder=folder+", "+"INBOX"
        email_copy["labels"] = folder
        print(f"Email {email['id']} moved to {folder}.")
    if email_copy == email:
        print("No modifications needed. Action would result in no changes.")
        return None 

    print("Email modified. Action will be applied.",email_copy,email)
    return email_copy
def match_condition(email, condition):
    

    field = condition["field"]
    predicate = condition["predicate"]
    value = condition["value"]

    # Ensure field exists in the email dictionary
    if field not in email:
        print(field, "not in", email)
        print("returning false as no field")
        return False

    email_value = email[field]

    # String-based conditions
    if isinstance(email_value, str):
        if predicate == "Contains" and value in email_value:
            return True
        elif predicate == "Does not Contain" and value not in email_value:
            return True
        elif predicate == "Equals" and value == email_value:
            return True
        elif predicate == "Does not Equal" and value != email_value:
            return True

    # Date-based conditions for "Received Date/Time"
    if field == "Received Date/Time":
        try:
            email_date = datetime.strptime(email_value, "%Y-%m-%d %H:%M:%S")
            if predicate in ["Less than", "Greater than"]:
                days = int(value) 
                print(days," is the number of days given")
                compare_date = datetime.now() - timedelta(days=days)
                print(compare_date," is the number of difference days given")
                if predicate == "Less than" and email_date > compare_date:
                    return True
                elif predicate == "Greater than" and email_date < compare_date:
                    return True
            elif predicate in ["Equals", "Does not Equal"]:
                compare_date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                if predicate == "Equals" and email_date == compare_date:
                    return True
                elif predicate == "Does not Equal" and email_date != compare_date:
                    return True
        except ValueError:
            print("Invalid date format in email or condition.")
            return False

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


def get_label_id(service, label_name):
    """Get the ID of a label given its name."""
    try:
        labels_response = service.users().labels().list(userId='me').execute()
        labels = labels_response.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        print(f"Label '{label_name}' not found.")
        return None
    except HttpError as error:
        print(f"Error retrieving labels: {error}")
        return None



def update_emails_in_service(emails, service):


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
        if "TRASH" in email.get("labels", ""):
            try:
                print(f"Moving email {email_id} to Trash...")
                response = service.users().messages().trash(userId='me', id=email_id).execute()
                print(f"Response for moving to Trash: {response}")
            except HttpError as error:
                print(f"Error while moving email {email_id} to Trash: {error}")
            continue  # Skip further label modification for emails moved to Trash
        results = service.users().labels().list(userId='me').execute()
        labels_all = results.get('labels', [])
    
        label_names = [label['name'] for label in labels_all]
        # Handle labels (add/remove user labels, ignore system labels)
        labels_to_add = []
        

        # Split the labels and remove empty labels
        labels = email.get("labels", "").split(", ") if email.get("labels") else []
        print(" here is the split labels:    ++++++++",labels)
        labels_to_remove = [get_label_id(service,l) for l in label_names if l not in labels ]
        # Iterate over the labels and process them
        for label in labels:
            label = label.strip()  
            if label:  
                l_id=get_label_id(service,label)
                print(l_id)
                if l_id:
                    labels_to_add.append(l_id)

        if labels_to_add:
            print(f"Adding labels {labels_to_add} to email {email_id}...")
            try:
                response = service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'addLabelIds': labels_to_add}
                ).execute()
                print(f"Response for adding labels: {response}")
            except HttpError as error:
                print(f"Error while adding labels to email {email_id}: {error}")

        if labels_to_remove:
            print(f"Removing labels {labels_to_remove} from email {email_id}...")
            for label in labels_to_remove:
                try:
                    response = service.users().messages().modify(
                        userId='me',
                        id=email_id,
                        body={'removeLabelIds': [label]}
                    ).execute()
                    print(f"Response for removing label {label}: {response}")
                except HttpError as error:

                    print(f"Error while removing label {label} from email {email_id}: {error}")
                    continue

        print(f"Finished processing email {email_id,email}.\n")



def process_rules(service):
    """Process rules, apply them to the emails, and update both the database and the email service."""
    rules = load_rules_from_json()
    if not rules:
        print("No rules found.")
        return


    emails = fetch_emails_from_db()  
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
    keep=[]
    for rule in rules.get("rules", []):
        rule_type = rule["type"]
        conditions = rule["conditions"]
        actions = rule["actions"]
        for email in emails:
            if "TRASH" in email['labels']:
                print(email)
                continue
            if rule_type == "All":

                if all(match_condition(email, condition) for condition in conditions):
                    
                    print(email['id'],"passed all")
                    for action in actions:

                        e=perform_action(email, action)
                        if e is not None and e not in keep:
                            keep.append(e)

            elif rule_type == "Any":
                
                if any(match_condition(email, condition) for condition in conditions):
                    print(email['id'],"passed any")
                    for action in actions:
                        e=perform_action(email, action)
                        if e is not None and e not in keep:
                            keep.append(e)
                        

    print("emails:::",keep)

    update_emails_in_db(keep)  # Update the emails in the database
    update_emails_in_service(keep,service)  # Apply changes to the main email service (e.g., Gmail API)

    print("Rules applied successfully.")
    return len(keep)
