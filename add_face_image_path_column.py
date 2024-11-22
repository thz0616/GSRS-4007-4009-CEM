import sqlite3

def add_face_image_path_column():
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE tenants ADD COLUMN face_image_path TEXT")
        conn.commit()
        print("Column 'face_image_path' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'face_image_path' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_face_image_path_column()
