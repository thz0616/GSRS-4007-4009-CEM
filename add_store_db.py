import sqlite3

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("properties.db")
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
    return conn

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

if __name__ == "__main__":
    conn = create_connection()
    if conn is not None:
        create_table(conn)
    conn.close()