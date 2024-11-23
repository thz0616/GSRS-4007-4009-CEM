import sqlite3

def create_database():
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    
    # Read the SQL file
    with open('create_database.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    
    # Execute the SQL script
    try:
        cursor.executescript(sql_script)
        print("Database created successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

if __name__ == "__main__":
    create_database() 