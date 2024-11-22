import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_admin_table():
    """Create the admin table if it doesn't exist"""
    conn = create_connection()
    
    if conn is not None:
        try:
            sql_create_admin_table = """
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                phone_number TEXT NOT NULL,
                fullname TEXT NOT NULL,
                ic_number TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor = conn.cursor()
            cursor.execute(sql_create_admin_table)
            conn.commit()
            print("Admin table created successfully")
            
        except Error as e:
            print(f"Error creating admin table: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

def insert_admin(username, phone_number, fullname, ic_number, email, password):
    """Insert a new admin into the admin table"""
    conn = create_connection()
    
    if conn is not None:
        try:
            sql = """
            INSERT INTO admin (username, phone_number, fullname, ic_number, email, password)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor = conn.cursor()
            cursor.execute(sql, (username, phone_number, fullname, ic_number, email, password))
            conn.commit()
            print("Admin inserted successfully")
            return True
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                if "username" in str(e):
                    print("Username already exists")
                elif "ic_number" in str(e):
                    print("IC number already exists")
                elif "email" in str(e):
                    print("Email already exists")
            return False
            
        except Error as e:
            print(f"Error inserting admin: {e}")
            return False
            
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return False

def get_admin_by_username(username):
    """Retrieve admin by username"""
    conn = create_connection()
    
    if conn is not None:
        try:
            sql = "SELECT * FROM admin WHERE username = ?"
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            admin = cursor.fetchone()
            return admin
            
        except Error as e:
            print(f"Error retrieving admin: {e}")
            return None
            
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return None

def verify_admin_login(username, password):
    """Verify admin login credentials"""
    conn = create_connection()
    
    if conn is not None:
        try:
            sql = "SELECT * FROM admin WHERE username = ? AND password = ?"
            cursor = conn.cursor()
            cursor.execute(sql, (username, password))
            admin = cursor.fetchone()
            return admin is not None
            
        except Error as e:
            print(f"Error verifying admin login: {e}")
            return False
            
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return False

# Create the admin table when this module is imported
create_admin_table()

if __name__ == "__main__":
    # Test the functions
    create_admin_table()
    
    # Test inserting an admin
    test_admin = {
        "username": "admin1",
        "phone_number": "0123456789",
        "fullname": "Test Admin",
        "ic_number": "990101012345",
        "email": "admin1@example.com",
        "password": "password123"
    }
    
    success = insert_admin(**test_admin)
    if success:
        print("Test admin inserted successfully")
        
        # Test login verification
        login_success = verify_admin_login("admin1", "password123")
        print(f"Login verification: {'Successful' if login_success else 'Failed'}") 