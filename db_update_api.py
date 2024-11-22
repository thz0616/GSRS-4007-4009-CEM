import sqlite3

def update_database_structure():
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Add new column to systemInformation table
        cursor.execute('''
            ALTER TABLE systemInformation 
            ADD COLUMN api_key TEXT
        ''')

        conn.commit()
        print("Database structure updated successfully!")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists. Skipping modification.")
        else:
            print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_structure() 