import sqlite3
from datetime import datetime

def delete_check_in_records(target_date):
    """
    Delete all records from dailyCheckInStatus for a specific date
    """
    try:
        # Connect to database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # First, get count of records to be deleted
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dailyCheckInStatus 
            WHERE date LIKE ?
        """, (f"{target_date}%",))
        
        count = cursor.fetchone()[0]
        
        # Delete records
        cursor.execute("""
            DELETE FROM dailyCheckInStatus 
            WHERE date LIKE ?
        """, (f"{target_date}%",))
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully deleted {count} record(s) for date {target_date}")
        
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    target_date = "2024-11-22"
    
    # Ask for confirmation
    confirm = input(f"Are you sure you want to delete all check-in records for {target_date}? (y/n): ")
    
    if confirm.lower() == 'y':
        delete_check_in_records(target_date)
    else:
        print("Operation cancelled.") 