import sqlite3
from datetime import datetime

def update_payment_records_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Drop the existing table to start fresh
        cursor.execute("DROP TABLE IF EXISTS payment_records")

        # Create the table with the new structure
        cursor.execute('''
        CREATE TABLE payment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rentalID INTEGER,
            payment_method TEXT,
            cardholder_name TEXT,
            card_number TEXT,
            expire_date TEXT,
            cvc TEXT,
            receipt TEXT,
            payment_period TEXT,  -- Format: YYYY-MM
            payment_date DATE,    -- Date when payment was made
            payment_time TIME,    -- Time when payment was made
            FOREIGN KEY (rentalID) REFERENCES rental(rentalID)
        )
        ''')

        # Commit the changes
        conn.commit()
        print("Successfully recreated payment_records table with new structure")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_payment_records_table() 