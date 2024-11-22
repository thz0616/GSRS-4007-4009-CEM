import sqlite3


# Create and connect to the SQLite database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("properties.db")
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
    return conn


# Create a table to store property details
def create_table(conn):
    create_properties_table = """
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        sqft INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image_path TEXT
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_properties_table)
        print("Table created successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


# Insert a new property record into the table
def insert_property(conn, property):
    insert_property_query = """
    INSERT INTO properties (location, sqft, start_date, end_date, price, description, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(insert_property_query, property)
        conn.commit()
        print("Property added successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


# Example usage
if __name__ == "__main__":
    # Create a connection to the database
    conn = create_connection()

    # Create the properties table if it doesn't exist
    if conn is not None:
        create_table(conn)

        # Close the connection after you're done
        conn.close()
