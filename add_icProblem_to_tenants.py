import sqlite3

def add_icProblem_to_tenants():
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    try:
        # Add the new column
        cursor.execute('''
        ALTER TABLE tenants
        ADD COLUMN icProblem TEXT
        ''')

        print("Successfully added 'icProblem' column to the tenants table.")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("The 'icProblem' column already exists in the tenants table.")
        else:
            print(f"An error occurred: {e}")

    finally:
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_icProblem_to_tenants()
