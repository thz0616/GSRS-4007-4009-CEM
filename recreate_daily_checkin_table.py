import sqlite3

def recreate_daily_checkin_table():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Drop the existing table
        cursor.execute('''
        DROP TABLE IF EXISTS dailyCheckInStatus
        ''')

        # Create the table with INTEGER for checkInStatus
        cursor.execute('''
        CREATE TABLE dailyCheckInStatus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rentalID INTEGER NOT NULL,
            date DATE NOT NULL,
            checkInStatus INTEGER NOT NULL,
            FOREIGN KEY (rentalID) REFERENCES rental(id),
            UNIQUE(rentalID, date)
        )
        ''')

        conn.commit()
        print("DailyCheckInStatus table recreated successfully with INTEGER status")
            
    except sqlite3.Error as e:
        print(f"Error recreating DailyCheckInStatus table: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    recreate_daily_checkin_table() 