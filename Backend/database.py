import sqlite3
import os
DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'emails.db')
)

def init_db():
    """
    Initialize the SQLite3 database with an emails table.
    """
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Deleted existing database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_date TEXT,
            labels TEXT,
            read INTEGER  
        )
    ''')
    conn.commit()
    conn.close()

def insert_email(email_id, sender, subject, body, received_date, labels="",is_read=""):
    """
    Insert an email into the database with its labels.
    """
    if isinstance(labels, list):
        labels = ", ".join(labels)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        

        cursor.execute('''
            INSERT INTO emails (id, sender, subject, body, received_date, labels,read)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email_id, sender, subject, body, received_date, labels,is_read))
        conn.commit()
    except sqlite3.IntegrityError:
        # Ignore duplicate emails
        pass
    conn.close()
