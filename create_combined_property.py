import sqlite3

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_combined_table(conn):
    """Create a combined table if it doesn't exist"""
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            status INTEGER DEFAULT 1,
            location TEXT,
            sqft INTEGER,
            tenancy_period TEXT,
            price REAL,
            description TEXT,
            image_path TEXT
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_combined_property(conn, property_data):
    """Insert a new combined property into the database"""
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO combined_properties (
            latitude, longitude, status, location, sqft, tenancy_period, 
            price, description, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', property_data)
        
        conn.commit()
        print("Property added successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def main():
    conn = create_connection()
    
    if conn is not None:
        create_combined_table(conn)
        
        # Get all property details from user
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))
        status = int(input("Enter status (1-4): "))
        location = input("Enter property location: ")
        sqft = int(input("Enter property size in sqft: "))
        tenancy_period = input("Enter tenancy period: ")
        price = float(input("Enter property price: "))
        description = input("Enter property description: ")
        image_path = input("Enter image file path: ")
        
        # Prepare data tuple
        property_data = (latitude, longitude, status, location, sqft, 
                         tenancy_period, price, description, image_path)
        
        # Insert the new combined property
        insert_combined_property(conn, property_data)
        
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
