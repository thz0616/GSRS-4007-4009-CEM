import customtkinter as ctk
import asyncio
import json
import webbrowser
import socket
import qrcode
from PIL import Image, ImageTk
from threading import Thread
from flask import Flask, render_template, send_from_directory, send_file
from flask_sock import Sock
import ssl
from OpenSSL import crypto
import os
import base64
from io import BytesIO
import traceback
import simple_websocket
import time
from tkinter import filedialog, messagebox
import logging
import io
import threading
import argparse
import sqlite3
import cv2
import numpy as np
from deepface import DeepFace
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
sock = Sock(app)

# Global variable to store active websocket connections
active_connections = set()

# Add these global variables after the existing ones
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Add these color definitions at the top after imports
HEADER_COLOR = "#E7D7C7"  # Light beige for header
BACKGROUND_COLOR = "#fffcf7"  # Very light beige for background
BUTTON_COLOR = "#c2b8ae"  # Muted beige for buttons
HOVER_COLOR = "#c89ef2"  # Hover color
TEXT_COLOR = "#654633"  # Brown for text
SECONDARY_TEXT_COLOR = "#8B7355"  # Lighter brown for secondary text

# Add this global variable after other globals
web_check_in_active = False

# Add this function before the App class
def create_self_signed_cert():
    # Generate key
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().CN = "*"  # Allow all hostnames
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    
    # Add Subject Alternative Names (SAN)
    alt_names = [
        b"DNS:*",
        b"DNS:*.local",
        b"DNS:localhost",
        b"IP:127.0.0.1"
    ]
    
    # Try to add the local IP to the certificate
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        alt_names.append(f"IP:{local_ip}".encode())
    except:
        pass
    
    san_extension = crypto.X509Extension(
        b"subjectAltName",
        False,
        b", ".join(alt_names)
    )
    cert.add_extensions([san_extension])
    
    cert.sign(k, 'sha256')
    
    # Save certificate and private key
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

# Add this near the start of the program
def print_network_info():
    print("\n=== Network Information ===")
    try:
        hostname = socket.gethostname()
        print(f"Hostname: {hostname}")
        
        # Get all IP addresses
        print("\nAll IP addresses:")
        addresses = socket.getaddrinfo(hostname, None)
        for addr in addresses:
            if addr[0] == socket.AF_INET:  # IPv4 only
                print(f"- {addr[4][0]}")
        
        print("\nActive network interface:")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            print(f"- {s.getsockname()[0]}")
        finally:
            s.close()
    except Exception as e:
        print(f"Error getting network info: {e}")
    print("=========================\n")

class App(ctk.CTk):
    def __init__(self, tenant_id=None):
        super().__init__()
        
        # Store tenant_id
        self.tenant_id = tenant_id
        self.face_image_path = None
        
        # Get face image path and stall location if tenant_id is provided
        if self.tenant_id:
            self.get_face_image_path()
            self.get_stall_location()
        
        # Initialize variables
        self.received_image = None
        self.latest_frame = None
        self.show_preview = False
        self.preview_window = None
        self.flask_started = False
        self.back_button = None
        self.latest_location = None
        
        # Get local IP address
        self.ip_address = self.get_local_ip()
        self.url = f"https://{self.ip_address}:8080"
        
        # Print connection information
        print("\n=== Web Check-in Server Information ===")
        print(f"Server IP: {self.ip_address}")
        print(f"Server URL: {self.url}")
        print("=====================================\n")
        
        # Configure main window
        self.title("Web Check-in QR Code")
        self.attributes("-fullscreen", True)
        self.configure(fg_color=BACKGROUND_COLOR)
        
        # Create main container
        self.container = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.container.pack(fill="both", expand=True)
        
        # Create header
        header = ctk.CTkFrame(self.container, height=120, fg_color=HEADER_COLOR)
        header.pack(fill="x", padx=0, pady=(0, 30))
        
        # Back Button
        self.back_button = ctk.CTkButton(
            header,
            text="← Back",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self.confirm_exit,
            corner_radius=15,
            width=100,
            height=40
        )
        self.back_button.pack(side="left", padx=40, pady=30)

        # Create status frame with border and background
        status_frame = ctk.CTkFrame(
            header,
            fg_color="#FFE4E1",  # Light red background
            corner_radius=15,
            border_width=2,
            border_color="#E0D5C9"
        )
        status_frame.pack(side="right", padx=40, pady=20)

        # Status indicator dot
        self.status_dot = ctk.CTkLabel(
            status_frame,
            text="●",  # Dot symbol
            font=ctk.CTkFont(size=24),
            text_color="#FF6B6B",  # Red dot for waiting
            width=30
        )
        self.status_dot.pack(side="left", padx=(15, 5), pady=10)
        
        # Status Label with enhanced styling
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Waiting for device connection...",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#654633"
        )
        self.status_label.pack(side="left", padx=(5, 15), pady=10)
        
        # Create content frame
        content_frame = ctk.CTkFrame(
            self.container,
            fg_color=HEADER_COLOR,
            corner_radius=20,
            border_width=2,
            border_color="#E0D5C9"
        )
        content_frame.pack(expand=True, fill="both", padx=300, pady=(0, 50))
        
        # Create QR Code section
        self.create_qr_code(content_frame)
        
        # Add Preview Button
        preview_button = ctk.CTkButton(
            header,
            text="Show Camera Preview",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self.toggle_preview,
            corner_radius=15,
            width=200,
            height=40
        )
        preview_button.pack(side="right", padx=(0, 40), pady=30)
        
        # Start preview update thread
        self.preview_thread = threading.Thread(target=self.update_preview, daemon=True)
        self.preview_thread.start()
        
        # Start Flask server
        self.start_flask_server()
    
    def get_local_ip(self):
        try:
            # Try getting IP from multiple possible interfaces
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google's DNS
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            # Fallback method to find a non-localhost IP
            try:
                # Get all network interfaces
                for interface in socket.getaddrinfo(socket.gethostname(), None):
                    # Only consider IPv4 addresses
                    if interface[0] == socket.AF_INET:
                        ip = interface[4][0]
                        # Skip localhost and empty addresses
                        if ip and not ip.startswith('127.'):
                            return ip
            except:
                pass
            
            # If all else fails, try one more method
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                if not ip.startswith('127.'):
                    return ip
            except:
                pass
            
            return "localhost"  # Last resort fallback
    
    def start_flask_server(self):
        def run_server():
            try:
                # Remove existing certificates
                if os.path.exists("cert.pem"):
                    os.remove("cert.pem")
                if os.path.exists("key.pem"):
                    os.remove("key.pem")
                
                # Create new certificate
                create_self_signed_cert()
                
                # SSL context with proper configuration
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain('cert.pem', 'key.pem')
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                logger.info("Starting Flask server...")
                app.run(
                    host='0.0.0.0', 
                    port=8080,
                    ssl_context=ssl_context,
                    debug=False,
                    use_reloader=False
                )
                self.flask_started = True
                logger.info("Flask server started successfully")
                
            except Exception as e:
                logger.error(f"Failed to start Flask server: {e}")
                messagebox.showerror("Server Error", 
                    f"Failed to start web server. Please check if port 8080 is available.\nError: {str(e)}")
        
        # Start Flask in a separate thread
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a bit to ensure server starts
        time.sleep(2)
        
        # Verify server is running
        try:
            import requests
            from urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            
            response = requests.get(self.url, verify=False, timeout=5)
            if response.status_code == 200:
                logger.info("Server is accessible")
            else:
                logger.warning(f"Server returned status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Could not verify server: {e}")
    
    def create_qr_code(self, parent_frame):
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color=TEXT_COLOR, back_color="white")
        
        # Convert to PhotoImage with larger size
        qr_image = qr_image.resize((300, 300))
        self.qr_photo = ImageTk.PhotoImage(qr_image)
        
        # Create frame for QR code content with enhanced styling and larger size
        qr_content = ctk.CTkFrame(
            parent_frame, 
            fg_color=BACKGROUND_COLOR,
            corner_radius=20,
            border_width=2,
            border_color="#E0D5C9"
        )
        qr_content.pack(expand=True, pady=50, padx=200)  # Increased horizontal padding
        
        # Main instruction with more padding
        main_instruction = ctk.CTkLabel(
            qr_content,
            text="Scan this QR code with your mobile device",
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=TEXT_COLOR,
            wraplength=600  # Added wraplength to handle text better
        )
        main_instruction.pack(pady=(50, 30), padx=50)  # Increased padding
        
        # Display QR code
        qr_display = ctk.CTkLabel(qr_content, image=self.qr_photo, text="")
        qr_display.pack(pady=30)
        
        # Display URL
        url_label = ctk.CTkLabel(
            qr_content,
            text=self.url,
            font=ctk.CTkFont(family="Helvetica", size=20),
            text_color=SECONDARY_TEXT_COLOR
        )
        url_label.pack(pady=(10, 30))
        
        # Instructions frame with enhanced styling
        instructions_frame = ctk.CTkFrame(
            qr_content, 
            fg_color=BACKGROUND_COLOR,
            corner_radius=15
        )
        instructions_frame.pack(pady=(0, 50), padx=80)  # Increased padding
        
        instructions = [
            "1. Open your phone's camera and scan the QR code",
            "2. Click 'Advanced' and 'Proceed' on the security warning",
            "3. Allow camera access when prompted",
            "4. Allow location access when prompted",
            "5. Take a photo for check-in verification"
        ]
        
        # Create instruction labels with consistent styling
        for instruction in instructions:
            instruction_label = ctk.CTkLabel(
                instructions_frame,
                text=instruction,
                font=ctk.CTkFont(family="Helvetica", size=18),
                text_color=SECONDARY_TEXT_COLOR
            )
            instruction_label.pack(pady=10, padx=30)  # Increased padding
        
        # Add a status container with enhanced styling
        self.check_in_status_frame = ctk.CTkFrame(
            parent_frame,
            fg_color="#FFE4E1",  # Light red background
            corner_radius=15,
            border_width=2,
            border_color="#E0D5C9"
        )
        self.check_in_status_frame.pack(pady=(0, 30), padx=80)

        # Status indicator dot and label
        self.check_in_status_dot = ctk.CTkLabel(
            self.check_in_status_frame,
            text="●",  # Dot symbol
            font=ctk.CTkFont(size=24),
            text_color="#FF6B6B",  # Red dot for waiting
            width=30
        )
        self.check_in_status_dot.pack(side="left", padx=(15, 5), pady=10)
        
        self.check_in_status_label = ctk.CTkLabel(
            self.check_in_status_frame,
            text="Waiting for device connection...",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#654633"
        )
        self.check_in_status_label.pack(side="left", padx=(5, 15), pady=10)
    
    def update_check_in_status(self, is_active=False):
        """Update the check-in status display on QR code page"""
        if is_active:
            self.check_in_status_dot.configure(text_color="#32CD32")  # Green dot
            self.check_in_status_label.configure(
                text="Check-in in Progress...",
                text_color="#006400"  # Dark green text
            )
        else:
            self.check_in_status_dot.configure(text_color="#FF6B6B")  # Red dot
            self.check_in_status_label.configure(
                text="Waiting for device connection...",
                text_color="#654633"
            )
    
    def display_received_image(self, base64_image):
        try:
            print("Starting to process received image...")  # Debug log
            
            # Decode base64 image
            try:
                image_data = base64.b64decode(base64_image.split(',')[1])
                print("Base64 decoded successfully")  # Debug log
            except Exception as e:
                print(f"Base64 decode error: {e}")
                raise
            
            # Open image
            try:
                image = Image.open(BytesIO(image_data))
                print(f"Image opened successfully. Size: {image.size}")  # Debug log
            except Exception as e:
                print(f"Image open error: {e}")
                raise
            
            # Resize image
            try:
                max_size = (380, 380)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"Image resized to: {image.size}")  # Debug log
            except Exception as e:
                print(f"Resize error: {e}")
                raise
            
            # Convert to PhotoImage
            try:
                photo = ImageTk.PhotoImage(image)
                print("Converted to PhotoImage successfully")  # Debug log
            except Exception as e:
                print(f"PhotoImage conversion error: {e}")
                raise
            
            # Update label
            if self.image_label:
                print("Updating image label...")  # Debug log
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
                print("Image label updated successfully")  # Debug log
            else:
                print("Error: image_label is None")
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            if self.image_label:
                self.image_label.configure(text=f"Error displaying image: {str(e)}", image=None)
    
    def display_received_data(self, base64_image, location_data):
        try:
            # Save the image to file
            image_data = base64.b64decode(base64_image.split(',')[1])
            timestamp = int(time.time())
            filename = f'image_{timestamp}.jpg'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Create image URL
            image_url = f'/uploads/{filename}'
            
            # Create message with image URL and location
            message = {
                'action': 'updateImage',
                'imageUrl': image_url
            }
            
            if location_data:
                message['location'] = location_data
            
            # Send to all connected clients
            for ws in active_connections.copy():
                try:
                    ws.send(json.dumps(message))
                except:
                    active_connections.remove(ws)
            
            # Display image in GUI
            self.display_received_image(base64_image)
            
        except Exception as e:
            print(f"Error processing received data: {e}")
            traceback.print_exc()
    
    def confirm_exit(self):
        if web_check_in_active:
            messagebox.showwarning(
                "Check-in in Progress",
                "A device is currently performing check-in.\nPlease complete the check-in process first."
            )
        else:
            self.destroy()
    
    def update_status(self, status_text, is_active=False):
        global web_check_in_active
        web_check_in_active = is_active
        
        if is_active:
            # Active state
            self.status_dot.configure(text_color="#32CD32")  # Green dot
            self.status_label.configure(
                text=status_text,
                text_color="#006400",  # Dark green text
                font=ctk.CTkFont(family="Helvetica", size=20, weight="bold")
            )
            self.back_button.configure(state="disabled")
        else:
            # Waiting state
            self.status_dot.configure(text_color="#FF6B6B")  # Red dot
            self.status_label.configure(
                text=status_text,
                text_color="#654633",  # Original text color
                font=ctk.CTkFont(family="Helvetica", size=20, weight="bold")
            )
            self.back_button.configure(state="normal")
    
    def toggle_preview(self):
        if not self.preview_window:
            self.show_preview = True
            if hasattr(self, 'verification_complete'):
                delattr(self, 'verification_complete')  # Reset verification status
            if hasattr(self, 'face_verification_passed'):
                delattr(self, 'face_verification_passed')  # Reset face verification
            self.create_preview_window()
        else:
            self.show_preview = False
            if self.preview_window:
                self.preview_window.destroy()
                self.preview_window = None
    
    def detect_and_crop_face(self, image):
        try:
            # Convert PIL Image to cv2 format
            opencv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                # Get the first face
                (x, y, w, h) = faces[0]
                
                # Add padding (20%)
                padding = int(w * 0.2)
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(opencv_img.shape[1] - x, w + 2*padding)
                h = min(opencv_img.shape[0] - y, h + 2*padding)
                
                # Crop the face
                face = opencv_img[y:y+h, x:x+w]
                
                # Convert back to PIL Image
                face_pil = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
                return face_pil
            return None
        except Exception as e:
            print(f"Error in face detection: {e}")
            return None
    
    def compare_faces(self, registered_face_img, live_face_img):
        try:
            # Convert PIL images to numpy arrays if needed
            if isinstance(registered_face_img, Image.Image):
                registered_face_img = cv2.cvtColor(np.array(registered_face_img), cv2.COLOR_RGB2BGR)
            if isinstance(live_face_img, Image.Image):
                live_face_img = cv2.cvtColor(np.array(live_face_img), cv2.COLOR_RGB2BGR)
            
            # Verify faces and get similarity
            result = DeepFace.verify(registered_face_img, live_face_img, enforce_detection=False)
            similarity = 1 - result['distance']  # Convert distance to similarity
            return similarity * 100  # Convert to percentage
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return None
    
    def create_preview_window(self):
        try:
            self.preview_window = ctk.CTkToplevel(self)
            self.preview_window.title("Camera Preview")
            self.preview_window.geometry("1200x900")
            
            # Create main frame for preview content
            preview_frame = ctk.CTkFrame(self.preview_window, fg_color=BACKGROUND_COLOR)
            preview_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Add countdown frame at the top but don't start countdown yet
            self.countdown_frame = ctk.CTkFrame(preview_frame, fg_color=HEADER_COLOR, corner_radius=15)
            self.countdown_frame.pack(fill="x", pady=(0, 10))
            
            self.countdown_label = ctk.CTkLabel(
                self.countdown_frame,
                text="Waiting for device connection...",
                font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                text_color=TEXT_COLOR
            )
            self.countdown_label.pack(pady=15)
            
            # Create frame for main images
            images_frame = ctk.CTkFrame(preview_frame, fg_color=BACKGROUND_COLOR)
            images_frame.pack(expand=True, fill="both", pady=10)
            images_frame.grid_columnconfigure(0, weight=1)
            images_frame.grid_columnconfigure(1, weight=1)
            
            # Left side - Registered Face
            face_frame = ctk.CTkFrame(images_frame, fg_color=HEADER_COLOR, corner_radius=15)
            face_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            
            face_title = ctk.CTkLabel(
                face_frame,
                text="Registered Face Image",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR
            )
            face_title.pack(pady=(20, 10))
            
            # Create frame for full and cropped registered face
            reg_faces_frame = ctk.CTkFrame(face_frame, fg_color=HEADER_COLOR)
            reg_faces_frame.pack(fill="both", expand=True, padx=10, pady=10)
            reg_faces_frame.grid_columnconfigure(0, weight=1)
            reg_faces_frame.grid_columnconfigure(1, weight=1)
            
            # Full registered face
            self.full_face_label = ctk.CTkLabel(reg_faces_frame, text="Full Image")
            self.full_face_label.grid(row=0, column=0, padx=5, pady=5)
            
            # Cropped registered face
            self.cropped_face_label = ctk.CTkLabel(reg_faces_frame, text="Cropped Face")
            self.cropped_face_label.grid(row=0, column=1, padx=5, pady=5)
            
            if self.face_image_path and os.path.exists(self.face_image_path):
                try:
                    # Load and display full face image
                    face_image = Image.open(self.face_image_path)
                    face_image.thumbnail((300, 300))
                    face_photo = ImageTk.PhotoImage(face_image)
                    self.full_face_label.configure(image=face_photo)
                    self.full_face_label.image = face_photo
                    
                    # Detect and display cropped face
                    cropped_face = self.detect_and_crop_face(face_image)
                    if cropped_face:
                        cropped_face.thumbnail((200, 200))
                        cropped_photo = ImageTk.PhotoImage(cropped_face)
                        self.cropped_face_label.configure(image=cropped_photo)
                        self.cropped_face_label.image = cropped_photo
                except Exception as e:
                    print(f"Error processing registered face: {e}")
            
            # Right side - Live Camera Feed
            camera_frame = ctk.CTkFrame(images_frame, fg_color=HEADER_COLOR, corner_radius=15)
            camera_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            
            camera_title = ctk.CTkLabel(
                camera_frame,
                text="Live Camera Feed",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR
            )
            camera_title.pack(pady=(20, 10))
            
            # Create frame for full and cropped live feed
            live_faces_frame = ctk.CTkFrame(camera_frame, fg_color=HEADER_COLOR)
            live_faces_frame.pack(fill="both", expand=True, padx=10, pady=10)
            live_faces_frame.grid_columnconfigure(0, weight=1)
            live_faces_frame.grid_columnconfigure(1, weight=1)
            
            # Full live feed
            self.preview_label = ctk.CTkLabel(
                live_faces_frame,
                text="Waiting for camera feed..."
            )
            self.preview_label.grid(row=0, column=0, padx=5, pady=5)
            
            # Cropped live face
            self.live_cropped_label = ctk.CTkLabel(
                live_faces_frame,
                text="Waiting for face detection..."
            )
            self.live_cropped_label.grid(row=0, column=1, padx=5, pady=5)
            
            # Add similarity label between images_frame and location_frame
            self.similarity_frame = ctk.CTkFrame(preview_frame, fg_color=HEADER_COLOR, corner_radius=15)
            self.similarity_frame.pack(fill="x", pady=(10, 0))
            
            self.similarity_label = ctk.CTkLabel(
                self.similarity_frame,
                text="Face Similarity: Waiting for detection...",
                font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
                text_color=TEXT_COLOR
            )
            self.similarity_label.pack(pady=15)
            
            # Location information at bottom
            location_frame = ctk.CTkFrame(preview_frame, fg_color=HEADER_COLOR, corner_radius=15)
            location_frame.pack(fill="x", pady=(10, 0))
            
            self.location_label = ctk.CTkLabel(
                location_frame,
                text="Waiting for location data...",
                font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
                text_color=TEXT_COLOR
            )
            self.location_label.pack(pady=15)
            
            # Add stall location frame
            stall_location_frame = ctk.CTkFrame(preview_frame, fg_color=HEADER_COLOR, corner_radius=15)
            stall_location_frame.pack(fill="x", pady=(10, 0))
            
            stall_location_text = "Stall Location: Unavailable"
            if hasattr(self, 'stall_latitude') and hasattr(self, 'stall_longitude'):
                stall_location_text = f"Stall Location: {self.stall_latitude:.6f}°N, {self.stall_longitude:.6f}°E"

            self.stall_location_label = ctk.CTkLabel(
                stall_location_frame,
                text=stall_location_text,
                font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
                text_color=TEXT_COLOR
            )
            self.stall_location_label.pack(pady=15)
            
            self.preview_window.protocol("WM_DELETE_WINDOW", self.toggle_preview)
            
        except Exception as e:
            error_msg = f"Error creating preview window:\n{str(e)}"
            print(error_msg)
            messagebox.showerror("Preview Window Error", error_msg)
    
    def update_preview(self):
        while True:
            if self.show_preview and self.preview_window and self.latest_frame:
                try:
                    # Convert the latest frame to PIL Image
                    image = Image.open(io.BytesIO(self.latest_frame))
                    
                    # Update full image
                    image.thumbnail((300, 300))
                    photo = ImageTk.PhotoImage(image)
                    self.preview_label.configure(image=photo)
                    self.preview_label.image = photo
                    
                    # Update cropped face
                    cropped_face = self.detect_and_crop_face(image)
                    if cropped_face:
                        cropped_face.thumbnail((200, 200))
                        cropped_photo = ImageTk.PhotoImage(cropped_face)
                        self.live_cropped_label.configure(image=cropped_photo)
                        self.live_cropped_label.image = cropped_photo
                        
                        # Compare faces if we have both registered and live faces
                        if hasattr(self, 'face_image_path') and os.path.exists(self.face_image_path):
                            registered_face = Image.open(self.face_image_path)
                            registered_cropped = self.detect_and_crop_face(registered_face)
                            
                            if registered_cropped is not None:
                                similarity = self.compare_faces(registered_cropped, cropped_face)
                                if similarity is not None:
                                    similarity_text = f"Face Similarity: {similarity:.2f}%"
                                    self.similarity_label.configure(text=similarity_text)
                                else:
                                    self.similarity_label.configure(text="Face Similarity: Unable to compare")
                
                    # Update location if available
                    if hasattr(self, 'latest_location') and self.latest_location:
                        lat = self.latest_location.get('latitude')
                        lon = self.latest_location.get('longitude')
                        if lat is not None and lon is not None:
                            location_text = f"Location: {lat:.6f}°N, {lon:.6f}°E"
                            self.location_label.configure(text=location_text)
                
                except Exception as e:
                    print(f"Error updating preview: {e}")
            time.sleep(0.1)
    
    def get_face_image_path(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Log tenant ID being queried
            print(f"Querying database for tenant ID: {self.tenant_id}")
            messagebox.showinfo("Debug", f"Searching for face image for tenant ID: {self.tenant_id}")
            
            cursor.execute("""
                SELECT FaceImagePath, fullName 
                FROM tenants 
                WHERE tenantID = ?
            """, (self.tenant_id,))
            
            result = cursor.fetchone()
            if result:
                self.face_image_path = result[0]
                tenant_name = result[1]
                print(f"Found face image path: {self.face_image_path} for tenant: {tenant_name}")
                messagebox.showinfo("Success", f"Found face image path for {tenant_name}:\n{self.face_image_path}")
                
                # Verify if file exists
                if not os.path.exists(self.face_image_path):
                    error_msg = f"Face image file not found at path:\n{self.face_image_path}"
                    print(error_msg)
                    messagebox.showerror("File Not Found", error_msg)
                    return
                
                # Try to open the image to verify it's valid
                try:
                    Image.open(self.face_image_path)
                    print("Successfully verified image file")
                except Exception as img_error:
                    error_msg = f"Error opening image file:\n{str(img_error)}"
                    print(error_msg)
                    messagebox.showerror("Image Error", error_msg)
                    
            else:
                error_msg = f"No face image found for tenant ID: {self.tenant_id}"
                print(error_msg)
                messagebox.showerror("Database Error", error_msg)
                
        except sqlite3.Error as e:
            error_msg = f"Database error while fetching face image:\n{str(e)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while fetching face image:\n{str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            conn.close()

    def update_database_status(self, status):
        """Update database with check-in status"""
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Get rental ID for the tenant
            cursor.execute("""
                SELECT rentalID, combined_properties_id 
                FROM rental 
                WHERE tenantID = ? AND isApprove = 1
                ORDER BY rentalID DESC
                LIMIT 1
            """, (self.tenant_id,))
            
            result = cursor.fetchone()
            if result:
                rental_id, combined_properties_id = result
                
                # Update combined_properties status
                cursor.execute("""
                    UPDATE combined_properties 
                    SET status = ? 
                    WHERE id = ?
                """, (status, combined_properties_id))
                
                # Always insert a new daily check-in status record
                current_date = datetime.date.today().strftime('%Y-%m-%d')  # Only date, no time
                
                cursor.execute("""
                    INSERT INTO dailyCheckInStatus (rentalID, date, checkInStatus)
                    VALUES (?, ?, ?)
                """, (rental_id, current_date, status))
                
                # If face verification failed, store the failed verification picture
                if status in [3, 4] and not hasattr(self, 'face_verification_passed'):
                    # Save the current frame as failed verification picture
                    if self.latest_frame:
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Keep timestamp for unique filenames
                        filename = f"failed_verification_{rental_id}_{timestamp}.jpg"
                        filepath = os.path.join("failed_verifications", filename)
                        
                        # Ensure directory exists
                        os.makedirs("failed_verifications", exist_ok=True)
                        
                        # Save the image
                        with open(filepath, 'wb') as f:
                            f.write(self.latest_frame)
                        
                        # Store in verificationFailedTenantPictures with timestamp
                        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("""
                            INSERT INTO verificationFailedTenantPictures 
                            (rentalID, date, imagePath)
                            VALUES (?, ?, ?)
                        """, (rental_id, current_datetime, filepath))
                
                conn.commit()
                print(f"Database updated successfully with status: {status}")
                
            else:
                print("No active rental found for tenant")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def process_frame(self):
        """Process a single frame and update the preview window"""
        if self.show_preview and self.preview_window and self.latest_frame:
            try:
                # Skip processing if verification is already complete
                if hasattr(self, 'verification_complete'):
                    return
                
                # Convert the latest frame to PIL Image
                image = Image.open(io.BytesIO(self.latest_frame))
                
                # Update full image
                image.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(image)
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo
                
                # Track verification status
                location_verified = False
                
                # Update cropped face
                cropped_face = self.detect_and_crop_face(image)
                if cropped_face:
                    cropped_face.thumbnail((200, 200))
                    cropped_photo = ImageTk.PhotoImage(cropped_face)
                    self.live_cropped_label.configure(image=cropped_photo)
                    self.live_cropped_label.image = cropped_photo
                    
                    # Compare faces if we have both registered and live faces
                    if hasattr(self, 'face_image_path') and os.path.exists(self.face_image_path):
                        registered_face = Image.open(self.face_image_path)
                        registered_cropped = self.detect_and_crop_face(registered_face)
                        
                        if registered_cropped is not None:
                            similarity = self.compare_faces(registered_cropped, cropped_face)
                            if similarity is not None:
                                self.latest_face_similarity = similarity  # Store latest similarity
                                similarity_text = f"Face Similarity: {similarity:.2f}%"
                                
                                # Check if face verification passed at any point
                                if similarity > 70:
                                    if not hasattr(self, 'face_verification_passed'):
                                        self.face_verification_passed = True
                                
                                # Add verification status to similarity text
                                if hasattr(self, 'face_verification_passed'):
                                    similarity_text += " (Verification Passed)"
                                
                                self.similarity_label.configure(text=similarity_text)
                            else:
                                self.similarity_label.configure(text="Face Similarity: Unable to compare")
                
                # Update location if available
                if hasattr(self, 'latest_location') and self.latest_location:
                    lat = self.latest_location.get('latitude')
                    lon = self.latest_location.get('longitude')
                    if lat is not None and lon is not None:
                        location_text = f"Current Location: {lat:.6f}°N, {lon:.6f}°E"
                        
                        # Compare with stall location
                        if hasattr(self, 'stall_latitude') and hasattr(self, 'stall_longitude'):
                            if (abs(lat - self.stall_latitude) < 0.001 and 
                                abs(lon - self.stall_longitude) < 0.001):
                                location_text += " (Verification Passed)"
                                location_verified = True
                        
                        self.location_label.configure(text=location_text)
                
                # Check if both verifications have passed (immediate success)
                face_verified = hasattr(self, 'face_verification_passed')
                if face_verified and location_verified:
                    self.verification_complete = True
                    self.update_database_status(1)  # Status 1: Both verifications passed
                    messagebox.showinfo("Check-in Status", 
                        "Check-in Successful!\nBoth face and location verifications passed.")
                    self.end_check_in()
            
            except Exception as e:
                print(f"Error processing frame: {e}")

    # Add this method to the App class to retrieve stall location
    def get_stall_location(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Get the combined_properties_id for the current tenant's rental
            cursor.execute("""
                SELECT combined_properties_id 
                FROM rental 
                WHERE tenantID = ? AND isApprove = 1
            """, (self.tenant_id,))
            
            result = cursor.fetchone()
            if result:
                combined_properties_id = result[0]
                
                # Fetch latitude and longitude for the stall
                cursor.execute("""
                    SELECT latitude, longitude 
                    FROM combined_properties 
                    WHERE id = ?
                """, (combined_properties_id,))
                
                location = cursor.fetchone()
                if location:
                    self.stall_latitude, self.stall_longitude = location
                    print(f"Stall location: Latitude={self.stall_latitude}, Longitude={self.stall_longitude}")
                else:
                    print("No location found for the stall.")
            else:
                print("No approved rental found for the tenant.")
            
        except sqlite3.Error as e:
            print(f"Database error while fetching stall location: {e}")
        finally:
            conn.close()

    # Add this method to the App class
    def start_countdown(self):
        """Start 30 second countdown on QR code page"""
        # Create countdown frame with enhanced styling
        self.countdown_frame = ctk.CTkFrame(
            self.container,
            fg_color=HEADER_COLOR,
            corner_radius=15,
            border_width=2,
            border_color="#E0D5C9"
        )
        self.countdown_frame.pack(fill="x", pady=(0, 20))
        
        self.countdown_label = ctk.CTkLabel(
            self.countdown_frame,
            text="Time Remaining: 30s",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=TEXT_COLOR
        )
        self.countdown_label.pack(pady=15)
        
        self.seconds_left = 30
        self.update_countdown()

    def update_countdown(self):
        """Update countdown timer and check verification status when time's up"""
        if self.seconds_left > 0:
            self.countdown_label.configure(text=f"Time Remaining: {self.seconds_left}s")
            
            # When 1 second remains, request final frame capture
            if self.seconds_left == 1:
                for ws in active_connections.copy():
                    try:
                        ws.send(json.dumps({'action': 'captureLastFrame'}))
                    except:
                        active_connections.remove(ws)
            
            self.seconds_left -= 1
            self.after(1000, self.update_countdown)
        else:
            self.countdown_label.configure(text="Time's Up!")
            self.check_final_status()

    def check_final_status(self):
        """Check final status of both verifications after countdown"""
        if hasattr(self, 'verification_complete'):
            return  # Skip if verification is already complete
        
        face_verified = hasattr(self, 'face_verification_passed')
        location_verified = False
        
        # Check location verification with increased threshold
        if hasattr(self, 'latest_location'):
            lat = self.latest_location.get('latitude')
            lon = self.latest_location.get('longitude')
            if lat is not None and lon is not None:
                if hasattr(self, 'stall_latitude') and hasattr(self, 'stall_longitude'):
                    location_verified = (abs(lat - self.stall_latitude) < 0.002 and 
                                      abs(lon - self.stall_longitude) < 0.002)  # Changed from 0.001 to 0.002
        
        # Determine status and message
        if face_verified and location_verified:
            status = 1  # Check-in Successfully
            message = "Check-in Successfully"
        elif face_verified and not location_verified:
            status = 2  # Only camera verification passed
            message = "Partial Check-in\nOnly face verification passed."
        elif not face_verified and location_verified:
            status = 3  # Only location verification passed
            message = "Partial Check-in\nOnly location verification passed."
        else:
            status = 4  # Both verifications failed
            message = "Check-in Failed\nBoth face and location verifications failed."
        
        # Update database and show message
        self.verification_complete = True
        
        # Insert new record in dailyCheckInStatus
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Get rental ID for the current tenant
            cursor.execute("""
                SELECT rentalID 
                FROM rental 
                WHERE tenantID = ? AND isApprove = 1
                ORDER BY rentalID DESC LIMIT 1
            """, (self.tenant_id,))
            
            result = cursor.fetchone()
            if result:
                rental_id = result[0]
                current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Insert new record for this attempt
                cursor.execute("""
                    INSERT INTO dailyCheckInStatus (rentalID, date, checkInStatus)
                    VALUES (?, ?, ?)
                """, (rental_id, current_datetime, status))
                
                # Also update combined_properties status
                cursor.execute("""
                    UPDATE combined_properties 
                    SET status = ? 
                    WHERE id = (
                        SELECT combined_properties_id 
                        FROM rental 
                        WHERE rentalID = ?
                    )
                """, (status, rental_id))
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
        
        messagebox.showinfo("Check-in Status", message)
        self.end_check_in()

    # Add this method to App class
    def end_check_in(self):
        """End the check-in process and close the window"""
        # Send end message to all connected clients
        for ws in active_connections.copy():
            try:
                ws.send(json.dumps({'action': 'checkInEnded'}))
            except:
                active_connections.remove(ws)
        
        # Close the main window after a short delay
        self.after(1000, self.destroy)

# Flask routes
@app.route('/')
def home():
    try:
        return send_from_directory('.', 'color_control.html')
    except Exception as e:
        logger.error(f"Error serving home page: {e}")
        return "Error loading page", 500

@app.route('/manifest.json')
def manifest():
    try:
        return send_from_directory('.', 'manifest.json')
    except Exception as e:
        logger.error(f"Error serving manifest: {e}")
        return "Error loading manifest", 500

@app.route('/uploads/<filename>')
def serve_image(filename):
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename), mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return "Error loading image", 500

@sock.route('/ws')
def websocket(ws):
    global web_check_in_active
    active_connections.add(ws)
    try:
        if hasattr(gui_app, 'update_status'):
            gui_app.after(0, gui_app.update_status, "Device connected - Camera active", True)
            
            # Update check-in status on QR code page
            if hasattr(gui_app, 'update_check_in_status'):
                gui_app.after(0, lambda: gui_app.update_check_in_status(True))
            
            # Start countdown when device connects
            if hasattr(gui_app, 'start_countdown'):
                gui_app.after(0, gui_app.start_countdown)
        
        while True:
            try:
                message = ws.receive()
                if message is None:
                    break
                
                data = json.loads(message)
                action = data.get('action')
                
                if action == 'sendFrame':
                    # Handle camera frame
                    image_data = base64.b64decode(data['image'].split(',')[1])
                    if hasattr(gui_app, 'latest_frame'):
                        gui_app.latest_frame = image_data
                    
                    # Handle location data that comes with the frame
                    location_data = data.get('location')
                    if location_data and hasattr(gui_app, 'latest_location'):
                        gui_app.latest_location = location_data
                        
                        # Update location label if preview window is open
                        if (hasattr(gui_app, 'location_label') and 
                            hasattr(gui_app, 'preview_window') and 
                            gui_app.preview_window):
                            lat = location_data.get('latitude')
                            lon = location_data.get('longitude')
                            if lat is not None and lon is not None:
                                location_text = f"Location: {lat:.6f}°N, {lon:.6f}°E"
                                gui_app.after(0, lambda: gui_app.location_label.configure(text=location_text))
                    
                    # Process the frame and wait for completion
                    if hasattr(gui_app, 'process_frame'):
                        gui_app.after(0, gui_app.process_frame)
                    
                    # Send confirmation that frame was processed
                    ws.send(json.dumps({'action': 'frameProcessed'}))
                elif action == 'finalFrame':
                    # Handle final frame
                    image_data = base64.b64decode(data['image'].split(',')[1])
                    if hasattr(gui_app, 'latest_frame'):
                        gui_app.latest_frame = image_data
                        
                        # Store the final frame if face verification failed
                        if not hasattr(gui_app, 'face_verification_passed'):
                            try:
                                conn = sqlite3.connect('properties.db')
                                cursor = conn.cursor()
                                
                                # Get rental ID
                                cursor.execute("""
                                    SELECT rentalID 
                                    FROM rental 
                                    WHERE tenantID = ? AND isApprove = 1
                                    ORDER BY rentalID DESC LIMIT 1
                                """, (gui_app.tenant_id,))
                                
                                result = cursor.fetchone()
                                if result:
                                    rental_id = result[0]
                                    
                                    # Save the image
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"failed_verification_{rental_id}_{timestamp}.jpg"
                                    filepath = os.path.join("failed_verifications", filename)
                                    
                                    # Ensure directory exists
                                    os.makedirs("failed_verifications", exist_ok=True)
                                    
                                    # Save the image
                                    with open(filepath, 'wb') as f:
                                        f.write(image_data)
                                    
                                    # Store in database
                                    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    cursor.execute("""
                                        INSERT INTO verificationFailedTenantPictures 
                                        (rentalID, date, imagePath)
                                        VALUES (?, ?, ?)
                                    """, (rental_id, current_date, filepath))
                                    
                                    conn.commit()
                                    print(f"Stored final failed verification image: {filepath}")
                                    
                            except sqlite3.Error as e:
                                print(f"Database error storing final frame: {e}")
                            finally:
                                if 'conn' in locals():
                                    conn.close()
                
            except Exception as e:
                print(f"Error processing message: {e}")
                traceback.print_exc()
                if "Connection closed" in str(e):
                    break
                continue
                
    finally:
        active_connections.remove(ws)
        if hasattr(gui_app, 'update_status'):
            gui_app.after(0, gui_app.update_status, "Waiting for device connection...", False)

if __name__ == "__main__":
    try:
        # Add argument parser
        parser = argparse.ArgumentParser()
        parser.add_argument('--tenant_id', type=int, help='Tenant ID')
        args = parser.parse_args()
        
        # Print network information before starting
        print_network_info()
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            logger.info(f"Created uploads directory: {UPLOAD_FOLDER}")
        
        # Start the GUI with tenant_id
        gui_app = App(tenant_id=args.tenant_id)
        gui_app.mainloop()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}") 