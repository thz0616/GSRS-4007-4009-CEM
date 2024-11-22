import sqlite3

def update_feedback_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # First, backup the existing data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_backup AS 
            SELECT * FROM feedback
        """)

        # Drop the existing feedback table
        cursor.execute("DROP TABLE IF EXISTS feedback")

        # Create the new feedback table with additional columns
        cursor.execute("""
            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                comment TEXT,
                timestamp TEXT,
                subject TEXT,
                rentalID INTEGER,
                FOREIGN KEY (rentalID) REFERENCES rental(rentalID)
            )
        """)

        # Restore the data from backup, setting new columns to NULL
        cursor.execute("""
            INSERT INTO feedback (id, category, comment, timestamp)
            SELECT id, category, comment, timestamp
            FROM feedback_backup
        """)

        # Drop the backup table
        cursor.execute("DROP TABLE feedback_backup")

        # Commit the changes
        conn.commit()
        print("Successfully updated feedback table schema")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_feedback_table() 