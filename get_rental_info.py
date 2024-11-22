import sqlite3
import cv2
import os
from deepface import DeepFace
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from flask import Flask, request, jsonify, send_from_directory
import datetime
import sys
import subprocess

LIGHT_PURPLE = "#F0E6FF"
DARK_PURPLE = "#4A3F75"
MUTED_LIGHT_PURPLE = "#D1C2F0"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Shared variables to store GPS data
shared_gps_data = {
    "latitude": None,
    "longitude": None
}

@app.route('/')
def serve_html():
    return send_from_directory('', 'index.html')

@app.route('/location', methods=['POST'])
def receive_location():
    """
    Handle incoming GPS data from the client.
    Expects JSON data with 'latitude' and 'longitude' fields.
    """
    data = request.json
    if data:
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude is not None and longitude is not None:
            shared_gps_data['latitude'] = float(latitude)
            shared_gps_data['longitude'] = float(longitude)
            logger.info(f"Received GPS coordinates: Latitude={latitude}, Longitude={longitude}")
            return jsonify(status="success"), 200
        else:
            logger.error("Invalid data received: Missing 'latitude' or 'longitude'")
            return jsonify(status="fail", message="Missing 'latitude' or 'longitude'"), 400
    else:
        logger.error("No data received in the POST request")
        return jsonify(status="fail", message="No data received"), 400

def run_flask():
    """
    Run the Flask app. Set use_reloader to False to prevent the Flask server from starting twice.
    """
    app.run(port=5000, use_reloader=False)

def get_rental_information(rental_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()

    try:
        # Query to get rental information
        query = """
        SELECT 
            r.rentalID,
            t.fullName AS tenant_name,
            cp.longitude,
            cp.latitude,
            t.FaceImagePath
        FROM 
            rental r
            JOIN tenants t ON r.tenantID = t.tenantID
            JOIN combined_properties cp ON r.combined_properties_id = cp.id
        WHERE 
            r.rentalID = ?
        """

        # Execute the query
        cursor.execute(query, (rental_id,))
        result = cursor.fetchone()

        if result:
            rental_id, tenant_name, longitude, latitude, face_image_path = result
            return rental_id, tenant_name, longitude, latitude, face_image_path
        else:
            print(f"No rental information found for ID: {rental_id}")
            return None

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the database connection
        conn.close()

def detect_and_crop_face(image_path):
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Image not found or unable to read: {image_path}")
        return None
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        print("No face detected in:", image_path)
        return None
    (x, y, w, h) = faces[0]
    return image[y:y + h, x:x + w]

def verify_face(reference_face, live_face, threshold=0.3):
    try:
        result = DeepFace.verify(reference_face, live_face, enforce_detection=False)
        distance = result['distance']
        return distance < threshold
    except Exception as e:
        print("Verification error:", e)
        return False

def create_verification_failed_pictures_table():
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verificationFailedTenantPictures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rentalID INTEGER,
        date TEXT,
        imagePath TEXT,
        FOREIGN KEY (rentalID) REFERENCES rental(rentalID)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_failed_verification_picture(rental_id, image_path):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO verificationFailedTenantPictures (rentalID, date, imagePath)
    VALUES (?, ?, ?)
    ''', (rental_id, current_date, image_path))
    
    conn.commit()
    conn.close()

# Call this function when initializing your application
create_verification_failed_pictures_table()

class FaceVerificationApp(ctk.CTk):
    def __init__(self, reference_image_path, stall_longitude, stall_latitude, rental_id):
        super().__init__()

        self.title("Real-Time Face Verification and GPS Location")
        self.attributes('-fullscreen', True)

        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            # Test if we can read from the camera
            ret, _ = self.cap.read()
            if not ret:
                raise Exception("Could not read from webcam")
                
        except Exception as e:
            messagebox.showerror("Camera Error", 
                "Unable to access webcam. Please ensure:\n\n" +
                "1. Your webcam is properly connected\n" +
                "2. No other application is using the webcam\n" +
                "3. You have given camera permissions to this application")
            self.destroy()
            return

        self.reference_face = detect_and_crop_face(reference_image_path)
        self.stall_longitude = float(stall_longitude)
        self.stall_latitude = float(stall_latitude)
        self.rental_id = rental_id

        self.current_longitude = None
        self.current_latitude = None

        self.face_verified = False
        self.gps_verified = False

        self.webcam_label = ctk.CTkLabel(self)
        self.webcam_label.pack(pady=20)

        self.result_label = ctk.CTkLabel(self, text="Verification Status", font=("Arial", 20))
        self.result_label.pack(pady=20)

        self.gps_label = ctk.CTkLabel(self, text="Current GPS Location: Fetching...", font=("Arial", 16))
        self.gps_label.pack(pady=10)

        self.stall_gps_label = ctk.CTkLabel(self, text=f"Stall GPS: {self.stall_latitude}, {self.stall_longitude}", font=("Arial", 16))
        self.stall_gps_label.pack(pady=10)

        # Start GPS thread to periodically fetch GPS data
        self.gps_thread = threading.Thread(target=self.fetch_gps_data)
        self.gps_thread.daemon = True
        self.gps_thread.start()

        self.verification_start_time = time.time()
        self.last_frame = None
        self.status_determined = False  # New flag to track if status has been determined

        self.update_webcam()

        # Schedule the status determination after 20 seconds
        self.after(20000, self.determine_status)

    def update_webcam(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame  # Store the last frame
            face_image = self.detect_face(frame)

            if face_image is not None:
                verified = verify_face(self.reference_face, face_image)

                if verified:
                    self.result_label.configure(text="Face Verification Success", fg_color="green")
                    self.face_verified = True
                    if self.gps_verified and not self.status_determined:
                        self.determine_status()  # Both verifications passed, determine status immediately
                        return  # Exit the method to stop further processing
                else:
                    self.result_label.configure(text="Face Verification Failed", fg_color="red")
            else:
                self.result_label.configure(text="No Face Detected", fg_color="orange")

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)

            self.webcam_label.imgtk = img_tk
            self.webcam_label.configure(image=img_tk)

            # Check if 20 seconds have passed and status hasn't been determined yet
            if time.time() - self.verification_start_time > 20 and not self.status_determined:
                self.determine_status()
                return  # Exit the method to stop further processing

        if not self.status_determined:
            self.after(10, self.update_webcam)

    def detect_face(self, frame):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            return frame[y:y + h, x:x + w]
        return None

    def show_success_message(self):
        messagebox.showinfo("Verification Passed", "Face verification passed successfully!")
        self.cap.release()
        self.destroy()

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

    def fetch_gps_data(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set geolocation permissions
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1
        })

        location_obtained = False
        attempt_count = 0

        while not location_obtained:
            try:
                logger.info(f"Attempt {attempt_count + 1} to fetch GPS location")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get('http://127.0.0.1:5000')

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "status"))
                )
                status_element = driver.find_element(By.ID, "status")
                location_text = status_element.text
                logger.info(f"Status text: {location_text}")

                if "Location sent successfully" in location_text:
                    parts = location_text.split(":")[1].strip().split(",")
                    if len(parts) == 2:
                        self.current_latitude = float(parts[0].strip())
                        self.current_longitude = float(parts[1].strip())

                        self.gps_label.configure(text=f"Current GPS: {self.current_latitude}, {self.current_longitude}")
                        logger.info(f"GPS Location: {self.current_latitude}, {self.current_longitude}")

                        # Compare GPS coordinates
                        self.compare_gps()

                        location_obtained = True
                        print(f"Current Location - Latitude: {self.current_latitude}, Longitude: {self.current_longitude}")
                    else:
                        logger.warning(f"Unexpected format for location text: {location_text}")
                        self.gps_label.configure(text="GPS: Unable to parse location")
                else:
                    logger.warning(f"Could not obtain GPS location. Status text: {location_text}")
                    self.gps_label.configure(text="GPS: Location not available")

            except Exception as e:
                logger.error(f"Error fetching GPS location: {str(e)}")
                self.gps_label.configure(text="GPS: Error fetching location")
            finally:
                driver.quit()

            if not location_obtained:
                logger.info("Waiting 2 seconds before next fetch attempt")
                time.sleep(2)  # Wait for 2 seconds before the next attempt
            
            attempt_count += 1

        logger.info("GPS location obtained successfully. Stopping further attempts.")

    def compare_gps(self):
        if self.current_latitude is not None and self.current_longitude is not None:
            lat_diff = abs(self.current_latitude - self.stall_latitude)
            lon_diff = abs(self.current_longitude - self.stall_longitude)

            if lat_diff <= 0.002 and lon_diff <= 0.002:
                self.gps_verified = True
                logger.info("GPS coordinates are within the acceptable range. Status: pass")
                if self.face_verified and not self.status_determined:
                    self.determine_status()  # Both verifications passed, determine status immediately
            else:
                logger.info("GPS coordinates are outside the acceptable range. Status: fail")

    def determine_status(self):
        if self.status_determined:
            return  # Prevent multiple determinations

        self.status_determined = True  # Set the flag to prevent further determinations

        # Determine check-in status with unified status messages
        if self.face_verified and self.gps_verified:
            status = 1  # Check-in Successfully
            check_in_status = 1  # Store as integer in database
        elif self.face_verified and not self.gps_verified:
            status = 2  # Only camera verification passed
            check_in_status = 2  # Store as integer in database
        elif not self.face_verified and self.gps_verified:
            status = 3  # Only location verification passed
            check_in_status = 3  # Store as integer in database
        else:
            status = 4  # Both verifications failed
            check_in_status = 4  # Store as integer in database

        # Update the status in combined_properties
        update_combined_properties_status(self.rental_id, status)

        # Insert a new daily check-in status record
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include time for each attempt
        conn = None
        try:
            conn = sqlite3.connect('properties.db', timeout=20)
            cursor = conn.cursor()
            
            # Always insert a new record for each attempt
            cursor.execute('''
                INSERT INTO dailyCheckInStatus (rentalID, date, checkInStatus)
                VALUES (?, ?, ?)
            ''', (self.rental_id, current_date, check_in_status))
            
            conn.commit()
            logger.info(f"Inserted new daily check-in status for rental {self.rental_id} on {current_date}: {check_in_status}")
            
        except sqlite3.Error as e:
            logger.error(f"Database error while inserting daily check-in status: {e}")
        finally:
            if conn:
                conn.close()

        # If face verification failed, capture and store the picture
        if not self.face_verified and self.last_frame is not None:
            self.capture_and_store_failed_verification()

        # Display the status with unified status messages
        status_text = {
            1: "Check-in Successfully",
            2: "Partially Check-in\nCamera verification passed",
            3: "Partially Check-in\nLocation verification passed",
            4: "Check-in Failed"
        }.get(status, "Unknown Status")

        messagebox.showinfo("Check-in Status", status_text)

        self.on_closing()  # Close the application after displaying the status

    def capture_and_store_failed_verification(self):
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"failed_verification_{self.rental_id}_{timestamp}.jpg"
        filepath = os.path.join("failed_verifications", filename)

        # Ensure the directory exists
        os.makedirs("failed_verifications", exist_ok=True)

        # Save the image
        cv2.imwrite(filepath, self.last_frame)

        # Store in the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO verificationFailedTenantPictures (rentalID, date, imagePath)
            VALUES (?, ?, ?)
            ''', (self.rental_id, datetime.datetime.now().isoformat(), filepath))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

def update_combined_properties_status(rental_id, status):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()

    try:
        # First, get the combined_properties_id from the rental table
        cursor.execute("SELECT combined_properties_id FROM rental WHERE rentalID = ?", (rental_id,))
        result = cursor.fetchone()
        
        if result:
            combined_properties_id = result[0]
            
            # Now update the status in the combined_properties table
            cursor.execute("UPDATE combined_properties SET status = ? WHERE id = ?", (status, combined_properties_id))
            conn.commit()
            logger.info(f"Updated status to {status} for combined_properties_id {combined_properties_id}")
        else:
            logger.error(f"No rental found with ID {rental_id}")
    
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()

    finally:
        conn.close()

def main(rental_id=None):
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Give Flask some time to start
    time.sleep(2)

    if rental_id is None:
        rental_id = input("Enter the rental ID: ")
    
    rental_info = get_rental_information(int(rental_id))

    if rental_info:
        # Instead of showing CheckInApp window, directly start verification
        start_verification_process(*rental_info)
    else:
        print("Unable to proceed with check-in due to missing information.")

def start_verification_process(rental_id, tenant_name, longitude, latitude, face_image_path):
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Give Flask some time to start
    time.sleep(2)

    try:
        # Test camera access before creating the app
        test_cap = cv2.VideoCapture(0)
        if not test_cap.isOpened():
            messagebox.showerror("Camera Error", 
                "Unable to access webcam. Please ensure your webcam is connected and not in use by another application.")
            return
        test_cap.release()

        # Create and run the face verification app
        app = FaceVerificationApp(face_image_path, longitude, latitude, rental_id)
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        error_message = str(e)
        if "cap_msmf" in error_message:
            messagebox.showerror("Camera Error", 
                "Unable to access webcam. Please ensure:\n\n" +
                "1. Your webcam is properly connected\n" +
                "2. No other application is using the webcam\n" +
                "3. You have given camera permissions to this application")
        else:
            messagebox.showerror("Error", f"Failed to start verification process: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        rental_id = int(sys.argv[1])
        main(rental_id)
    else:
        main()
