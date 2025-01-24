import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request  # Import required for token refresh

# Define Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
print(f"Current Working Directory: {os.getcwd()}")
import os

# Dynamically resolve the correct path for credentials.json
CREDENTIALS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
)

TOKEN_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
)
def authenticate_gmail():
    """
    Authenticate with Gmail API and return a service object.
    Handles token creation, refresh, and reuse.
    """
    creds = None

    # Check if token.pickle exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, generate new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new token to token.pickle
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service object
    return build('gmail', 'v1', credentials=creds)
