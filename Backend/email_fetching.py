from googleapiclient.discovery import build
from Backend.database import insert_email,init_db

def fetch_emails(service, max_results=10):
    """
    Fetch emails from Gmail and store them in the SQLite3 database.
    """
    # Get a list of messages from the user's inbox
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    for message in messages:
        # Get the details of each message
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_id = msg['id']
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        # Extract email metadata
        sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        received_date = msg.get('internalDate', None)

        # Extract email body
        body = None
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body'].get('data', None)
                    break

        # Convert received_date to human-readable format
        if received_date:
            received_date = int(received_date) / 1000  # Convert from ms to seconds
            from datetime import datetime
            received_date = datetime.fromtimestamp(received_date).strftime('%Y-%m-%d %H:%M:%S')

        # Decode email body if available
        if body:
            import base64
            body = base64.urlsafe_b64decode(body).decode('utf-8')

        # Extract labels (folders) the email is in
        label_ids = msg.get('labelIds', [])
        is_read = "UNREAD" not in label_ids


        # Insert email into the database along with labels
        init_db()
        insert_email(email_id, sender, subject, body, received_date, label_ids,is_read)
def fetch_all_labels(service):
    """
    Fetch all labels from the authenticated user's Gmail account.
    """
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    label_names = [label['name'] for label in labels]
    
    return label_names
