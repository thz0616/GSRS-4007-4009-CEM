import sqlite3

def add_isApprove_to_rental():
    # Connect to the database
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()

    try:
        # Check if the isApprove column already exists
        cursor.execute("PRAGMA table_info(rental)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'isApprove' not in columns:
            # Add the isApprove column to the rental table
            cursor.execute("ALTER TABLE rental ADD COLUMN isApprove INTEGER DEFAULT 0")
            
            # Update all existing records to set isApprove to 0
            cursor.execute("UPDATE rental SET isApprove = 0 WHERE isApprove IS NULL")
            
            # Commit the changes
            conn.commit()
            print("Successfully added 'isApprove' column and set existing records to 0.")
        else:
            print("The 'isApprove' column already exists in the rental table.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()

    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    add_isApprove_to_rental()
