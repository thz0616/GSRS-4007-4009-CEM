import sqlite3
from datetime import datetime


# Function to connect to the database and create a table if it doesn't exist
def create_connection():
    try:
        conn = sqlite3.connect('feedback.db')  # This will create the feedback.db file if it doesn't exist
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


# Function to create feedback table if it doesn't exist
def create_table(conn):
    if conn:
        try:
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL,
                comments TEXT,
                date TEXT NOT NULL
            )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")


# Function to insert a new feedback record
def insert_feedback(name, emoji, comments):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('''
            INSERT INTO feedback (name, emoji, comments, date)
            VALUES (?, ?, ?, ?)
            ''', (name, emoji, comments, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            print("Feedback successfully saved!")
        except sqlite3.Error as e:
            print(f"Error inserting feedback: {e}")
        finally:
            conn.close()


# Function to retrieve all feedback data
def fetch_feedback():
    conn = create_connection()
    feedbacks = []
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM feedback')
            feedbacks = c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching feedback: {e}")
        finally:
            conn.close()
    return feedbacks
