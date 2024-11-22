import sqlite3

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def modify_combined_table(conn):
    """Modify the combined_properties table"""
    try:
        cursor = conn.cursor()
        
        # Check if the old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='combined_properties'")
        if cursor.fetchone():
            # Rename the existing table
            cursor.execute("ALTER TABLE combined_properties RENAME TO old_combined_properties")
        
        # Create the new table with modified structure
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            status INTEGER DEFAULT 1,
            addressLine1 TEXT,
            addressLine2 TEXT,
            postcode TEXT,
            city TEXT,
            state TEXT,
            sqft INTEGER,
            price REAL,
            description TEXT,
            image_path TEXT
        )
        ''')
        
        # Copy data from old table to new table if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='old_combined_properties'")
        if cursor.fetchone():
            cursor.execute('''
            INSERT INTO combined_properties (
                id, latitude, longitude, status, addressLine1, sqft, price, description, image_path
            )
            SELECT id, latitude, longitude, status, location, sqft, price, description, image_path
            FROM old_combined_properties
            ''')
            
            # Drop the old table
            cursor.execute("DROP TABLE old_combined_properties")
        
        conn.commit()
        print("Table structure updated successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred while modifying the table: {e}")

def insert_modified_property(conn, property_data):
    """Insert a new property into the modified table"""
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO combined_properties (
            latitude, longitude, status, addressLine1, addressLine2, postcode, city, state,
            sqft, price, description, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', property_data)
        
        conn.commit()
        print("Property added successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred while inserting the property: {e}")

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def main():
    conn = create_connection()
    
    if conn is not None:
        modify_combined_table(conn)
        
        print("Please enter the property details.")
        
        # Get all property details from user with error handling
        latitude = get_float_input("Enter latitude: ")
        longitude = get_float_input("Enter longitude: ")
        status = get_int_input("Enter status (1-4): ")
        addressLine1 = input("Enter address line 1: ")
        addressLine2 = input("Enter address line 2: ")
        postcode = input("Enter postcode: ")
        city = input("Enter city: ")
        state = input("Enter state: ")
        sqft = get_int_input("Enter property size in sqft: ")
        price = get_float_input("Enter property price: ")
        description = input("Enter property description: ")
        image_path = input("Enter image file path: ")
        
        # Prepare data tuple
        property_data = (latitude, longitude, status, addressLine1, addressLine2, postcode, city, state,
                         sqft, price, description, image_path)
        
        # Insert the new property
        insert_modified_property(conn, property_data)
        
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
