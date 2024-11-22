import sqlite3

def delete_rental(rental_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # Delete the rental record with the specified ID
        cursor.execute("DELETE FROM rental WHERE rentalID = ?", (rental_id,))
        
        # Commit the changes
        conn.commit()
        
        # Check if any row was affected
        if cursor.rowcount > 0:
            print(f"Successfully deleted rental record with ID {rental_id}")
        else:
            print(f"No rental record found with ID {rental_id}")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    # Delete rental record with ID 8
    delete_rental(8) 