import sqlite3
from datetime import datetime
import time

def create_daily_checkin_table():
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        conn = None
        try:
            # Connect to the database with a timeout
            conn = sqlite3.connect('properties.db', timeout=20)
            cursor = conn.cursor()

            # Drop the table if it exists
            cursor.execute('''
            DROP TABLE IF EXISTS dailyCheckInStatus
            ''')

            # Create the DailyCheckInStatus table with integer status
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS dailyCheckInStatus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rentalID INTEGER NOT NULL,
                date DATE NOT NULL,
                checkInStatus INTEGER NOT NULL,
                FOREIGN KEY (rentalID) REFERENCES rental(id),
                UNIQUE(rentalID, date)
            )
            ''')

            conn.commit()
            print("DailyCheckInStatus table created successfully")
            break  # Exit the loop if successful
            
        except sqlite3.Error as e:
            print(f"Attempt {attempt + 1}: Error creating DailyCheckInStatus table: {e}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(1)  # Wait for 1 second before retrying
        
        finally:
            if conn:
                conn.close()

    if attempt == max_attempts:
        print("Failed to create table after maximum attempts")

# Helper functions for common operations
def add_daily_checkin(rental_id, date, status):
    conn = None
    try:
        conn = sqlite3.connect('properties.db', timeout=20)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO dailyCheckInStatus (rentalID, date, checkInStatus)
        VALUES (?, ?, ?)
        ''', (rental_id, date, status))
        
        conn.commit()
        print("Daily check-in status added successfully")
        
    except sqlite3.Error as e:
        print(f"Error adding daily check-in status: {e}")
    
    finally:
        if conn:
            conn.close()

def get_daily_checkin(rental_id, date):
    conn = None
    try:
        conn = sqlite3.connect('properties.db', timeout=20)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM dailyCheckInStatus 
        WHERE rentalID = ? AND date = ?
        ''', (rental_id, date))
        
        return cursor.fetchone()
        
    except sqlite3.Error as e:
        print(f"Error retrieving daily check-in status: {e}")
        return None
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_daily_checkin_table()
