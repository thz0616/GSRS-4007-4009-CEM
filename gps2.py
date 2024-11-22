from flask import Flask, request, jsonify, send_from_directory
import os
import webbrowser
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
browser_opened = False
location_received = threading.Event()

# Serve the HTML file
@app.route('/')
def serve_html():
    return send_from_directory('', 'index.html')

def create_location_table():
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.json
    logger.info(f"Received location data: {data}")
    rental_id = data.get('rental_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if rental_id is None or latitude is None or longitude is None:
        logger.error("Missing data in location request")
        return jsonify({"status": "fail", "message": "Missing data"}), 400
    
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO locations (rental_id, latitude, longitude)
            VALUES (?, ?, ?)
        """, (rental_id, latitude, longitude))
        conn.commit()
        conn.close()
        logger.info(f"Saved location data: rental_id={rental_id}, lat={latitude}, lon={longitude}")
    except Exception as e:
        logger.error(f"Error saving location data: {str(e)}")
        return jsonify({"status": "fail", "message": "Database error"}), 500
    
    location_received.set()  # Signal that location has been received
    return jsonify({"status": "success"}), 200

def open_browser():
    global browser_opened
    if not browser_opened:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('http://127.0.0.1:5000')
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Browser page loaded successfully")
            
            # Wait for location to be received or timeout after 30 seconds
            if location_received.wait(timeout=30):
                logger.info("Location received successfully")
                # Fetch the latest location from the database
                conn = sqlite3.connect('properties.db')
                cursor = conn.cursor()
                cursor.execute("SELECT rental_id, latitude, longitude FROM locations ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    rental_id, latitude, longitude = result
                    logger.info(f"Latest location: rental_id={rental_id}, latitude={latitude}, longitude={longitude}")
                    print(f"\nLatest location:\nRental ID: {rental_id}\nLatitude: {latitude}\nLongitude: {longitude}\n")
                else:
                    logger.warning("No location data found in the database")
            else:
                logger.warning("Timeout waiting for location")
        except Exception as e:
            logger.error(f"Error in open_browser: {str(e)}")
        finally:
            driver.quit()
        
        browser_opened = True

def run_flask():
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    create_location_table()
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    time.sleep(1)  # Give Flask a moment to start
    
    open_browser()  # Run this in the main thread instead of a separate thread
    
    flask_thread.join()
    
    # Keep the console window open
    input("Press Enter to exit...")
