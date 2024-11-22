import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return None

def modify_system_info_table():
    """Add passcode column to systemInformation table"""
    conn = create_connection()
    
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Check if passcode column exists
            cursor.execute("PRAGMA table_info(systemInformation)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'passcode' not in column_names:
                # Add passcode column with default value '0000'
                cursor.execute('''
                    ALTER TABLE systemInformation
                    ADD COLUMN passcode TEXT DEFAULT '0000'
                ''')
                print("Successfully added passcode column to systemInformation table")
            else:
                print("Passcode column already exists")
                
            conn.commit()
            
        except Error as e:
            print(f"Error modifying table: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    modify_system_info_table() 