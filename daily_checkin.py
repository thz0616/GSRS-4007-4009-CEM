import cv2
import sqlite3
import time
from facerecog2024911_02 import verify_face, detect_and_crop_face

def get_checkin_info(rental_id):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.face_image_path, cp.latitude, cp.longitude, r.tenant_id
            FROM rental r
            JOIN tenants t ON r.tenant_id = t.id
            JOIN combined_properties cp ON r.stall_id = cp.id
            WHERE r.id = ?
        """, (rental_id,))
        result = cursor.fetchone()
        if result:
            print(f"Check-in info found: {result}")
        else:
            print(f"No check-in info found for rental_id: {rental_id}")
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def update_stall_status(stall_id, status):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE combined_properties
            SET status = ?
            WHERE id = ?
        """, (status, stall_id))
        conn.commit()
        print(f"Updated status to {status} for stall_id: {stall_id}")
    except sqlite3.Error as e:
        print(f"Error updating stall status: {e}")
    finally:
        conn.close()

def get_latest_user_location(tenant_id):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT latitude, longitude FROM locations
            WHERE rental_id IN (SELECT id FROM rental WHERE tenant_id = ?)
            ORDER BY timestamp DESC
            LIMIT 1
        """, (tenant_id,))
        result = cursor.fetchone()
        if result:
            print(f"Latest location for tenant_id {tenant_id}: {result}")
        else:
            print(f"No location found for tenant_id: {tenant_id}")
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def checkin(rental_id):
    print(f"Starting check-in process for rental ID: {rental_id}")
    
    # Get check-in info
    checkin_info = get_checkin_info(rental_id)
    if not checkin_info:
        print("Check-in information not found.")
        return False
    
    face_image_path, stall_lat, stall_lon, tenant_id = checkin_info
    
    # Face verification
    print("Performing face verification...")
    cropped_face = detect_and_crop_face('captured_image.jpg')  # Update path if necessary
    if cropped_face is None:
        print("No face detected in the captured image.")
        update_stall_status(rental_id, 4)  # Status 4: Check-in failed
        return False
    
    face_verified = verify_face(cropped_face, face_image_path)
    if not face_verified:
        print("Face verification failed.")
        update_stall_status(rental_id, 4)  # Status 4: Check-in failed
        return False
    
    print("Face verification passed.")
    
    # Location verification
    print("Checking location...")
    user_location = get_latest_user_location(tenant_id)
    if not user_location:
        print("Unable to get current location.")
        update_stall_status(rental_id, 3)  # Status 3: Location verification failed
        return False
    
    user_lat, user_lon = user_location
    lat_diff = abs(user_lat - stall_lat)
    lon_diff = abs(user_lon - stall_lon)
    
    if lat_diff <= 0.001 and lon_diff <= 0.001:
        print("Location verified.")
        update_stall_status(rental_id, 1)  # Status 1: Check-in successful
        return True
    else:
        print("Location verification failed.")
        update_stall_status(rental_id, 2)  # Status 2: Wrong location
        return False

if __name__ == "__main__":
    # Run check-in for rental ID 1
    result = checkin(1)
    if result:
        print("Check-in successful!")
    else:
        print("Check-in failed.")
