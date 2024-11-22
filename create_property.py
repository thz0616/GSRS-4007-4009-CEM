import sqlite3
from datetime import datetime

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables if they don't exist"""
    try:
        cursor = conn.cursor()
        
        # Create locations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            status INTEGER DEFAULT 1
        )
        ''')
        
        # Create properties table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            sqft INTEGER,
            tenancy_period TEXT,
            price REAL,
            description TEXT,
            image_path TEXT,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_property(conn, property_data, location_data):
    """Insert a new property into the database"""
    try:
        cursor = conn.cursor()
        
        # Insert location data
        cursor.execute('''
        INSERT INTO locations (latitude, longitude, status)
        VALUES (?, ?, ?)
        ''', location_data)
        location_id = cursor.lastrowid
        
        # Insert property data
        cursor.execute('''
        INSERT INTO properties (location, sqft, tenancy_period, price, description, image_path, location_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (*property_data, location_id))
        
        conn.commit()
        print("Property added successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def main():
    # Create a database connection
    conn = create_connection()
    
    if conn is not None:
        # Create tables
        create_tables(conn)
        
        # Get property details from user
        location = input("Enter property location: ")
        sqft = int(input("Enter property size in sqft: "))
        tenancy_period = input("Enter tenancy period: ")
        price = float(input("Enter property price: "))
        description = input("Enter property description: ")
        image_path = input("Enter image file path: ")
        
        # Get location details
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))
        status = int(input("Enter status (1-4): "))
        
        # Prepare data tuples
        property_data = (location, sqft, tenancy_period, price, description, image_path)
        location_data = (latitude, longitude, status)
        
        # Insert the new property
        insert_property(conn, property_data, location_data)
        
        # Close the connection
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
