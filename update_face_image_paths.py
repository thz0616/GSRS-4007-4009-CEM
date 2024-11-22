import sqlite3

def update_face_image_path(rental_id, image_path):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE tenants
            SET face_image_path = ?
            WHERE rental_id = ?
        """, (image_path, rental_id))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"No tenant found with rental_id: {rental_id}")
        else:
            print(f"Updated face_image_path for rental_id: {rental_id}")
    except sqlite3.Error as e:
        print(f"Error updating face_image_path: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Example: Update face_image_path for rental_id 1
    update_face_image_path(1, 'path/to/tenant1_face.jpg')
    
    # Add more updates as needed
    # update_face_image_path(2, 'path/to/tenant2_face.jpg')
