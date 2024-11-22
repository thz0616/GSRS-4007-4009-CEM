from customtkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from gmail_otp import generate_otp, send_email
import threading
import time
import cv2
import os
import sqlite3
from tkinter import filedialog
from deepface import DeepFace
from tkinter import messagebox  # Add this import at the top of the file
import re
import bcrypt

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Add these validation functions after the imports
def is_valid_phone(phone):
    """Check if phone number is valid (10 or 11 digits)"""
    # Remove any spaces or dashes
    phone = phone.replace(" ", "").replace("-", "")
    # Check if it contains only digits and is 10 or 11 digits long
    return phone.isdigit() and (len(phone) == 10 or len(phone) == 11)

def is_valid_email(email):
    """Check if email address is in valid format"""
    # Regular expression for email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

class CombinedApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1920x1080")
        self.master.title("Login and Signup")
        self.master.attributes("-fullscreen", True)

        # Connect to the database
        self.conn = sqlite3.connect('properties.db')
        self.cursor = self.conn.cursor()
        
        # Ensure database schema is up to date
        self.ensure_database_schema()

        self.create_login_page()
        self.continue_button = None
        self.current_user = None  # Add this to store current user info

    def ensure_database_schema(self):
        try:
            # Check if profile_image column exists
            self.cursor.execute("PRAGMA table_info(tenants)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Add profile_image column if it doesn't exist
            if 'profile_image' not in columns:
                self.cursor.execute("ALTER TABLE tenants ADD COLUMN profile_image TEXT")
                # Set existing profile_image values to match FaceImagePath
                self.cursor.execute("UPDATE tenants SET profile_image = FaceImagePath WHERE profile_image IS NULL")
                self.conn.commit()
                print("Added profile_image column to tenants table")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", f"Failed to update database schema: {e}")

    def create_login_page(self):
        # Define screen dimensions
        screen_width = 1920
        screen_height = 1080

        # Left and right frame widths
        left_frame_width = 800
        right_frame_width = 1120

        # Create left and right frames
        self.left_frame = CTkFrame(self.master, width=left_frame_width, height=screen_height)
        self.left_frame.place(x=0, y=0)
        self.right_frame = CTkFrame(self.master, width=right_frame_width, height=screen_height, fg_color="white")
        self.right_frame.place(x=left_frame_width, y=0)

        # Set background image for the left frame
        self.set_background_image(self.left_frame, "IMG_2085.jpg", left_frame_width, screen_height)

        # Fonts
        font_header = ("Arial", 72, "bold")
        font_label = ("Arial", 28)
        font_input = ("Arial", 28)
        font_button = ("Arial", 36)

        # "Login" Header
        login_label = CTkLabel(self.right_frame, text="Login", font=font_header, text_color="#000000", fg_color="white")
        login_label.place(x=150, y=150)

        # Username Label and Entry
        username_label = CTkLabel(self.right_frame, text="Username", font=font_label, text_color="#666666", fg_color="white")
        username_label.place(x=150, y=350)
        self.username_entry = CTkEntry(self.right_frame, width=820, height=90, font=font_input, corner_radius=30, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.username_entry.place(x=150, y=400)

        # Password Label and Entry
        password_label = CTkLabel(self.right_frame, text="Password", font=font_label, text_color="#666666", fg_color="white")
        password_label.place(x=150, y=540)
        self.password_entry = CTkEntry(self.right_frame, width=820, height=90, font=font_input, corner_radius=30, border_color="#CCCCCC", fg_color="white", text_color="#000000", show="*")
        self.password_entry.place(x=150, y=590)

        # Login Button
        login_button = CTkButton(self.right_frame, text="LOGIN", font=font_button, text_color="#000000", fg_color="#c2b8ae", hover_color="#c89ef2", corner_radius=30, width=820, height=90, command=self.handle_login)
        login_button.place(x=150, y=750)

        # Sign up Button on the left frame
        sign_up_button = CTkButton(self.left_frame, text="SIGN UP", font=font_button, text_color="white", fg_color="#c2b8ae",
                                   hover_color="#0056b3", width=140, height=60, border_width=2,
                                   border_color="#c2b8ae", command=self.open_signup_page)
        sign_up_button.place(x=350, y=800)

    def set_background_image(self, frame, image_path, width, height):
        try:
            image = Image.open(image_path)
            image = image.resize((width, height), Image.LANCZOS)
            bg_image = ImageTk.PhotoImage(image)

            label = tk.Label(frame, image=bg_image)
            label.image = bg_image
            label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

    def open_signup_page(self):
        # Clear the login page
        for widget in self.master.winfo_children():
            widget.destroy()

        # Create the signup page
        self.create_signup_page()

    def create_signup_page(self):
        # Create left and right frames (swapped positions)
        right_frame_width = 1120
        left_frame_width = 800
        self.right_frame = CTkFrame(self.master, width=right_frame_width, height=1080, fg_color="white")
        self.right_frame.place(x=0, y=0)
        self.left_frame = CTkFrame(self.master, width=left_frame_width, height=1080)
        self.left_frame.place(x=right_frame_width, y=0)

        # Set background image for the left frame
        self.set_background_image(self.left_frame, "IMG_2084.jpg", left_frame_width, 1080)

        # Fonts
        font_header = ("Arial", 72, "bold")
        font_label = ("Arial", 28)
        font_input = ("Arial", 28)
        font_button = ("Arial", 36)

        # Signup header
        self.signup_header = CTkLabel(self.right_frame, text="Create Account", font=("Arial", 72, "bold"), text_color="#000000", fg_color="white")
        self.signup_header.place(x=150, y=50)

        # Slides setup
        self.slides = [CTkFrame(self.right_frame, width=right_frame_width, height=800, fg_color="white") for _ in range(2)]
        self.current_slide = 0

        # Slide 1 (Username, Full Name, Phone Number, IC Number)
        username_label = CTkLabel(self.slides[0], text="Username", font=font_label, text_color="#666666", fg_color="white")
        username_label.place(x=150, y=50)
        self.username_entry = CTkEntry(self.slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.username_entry.place(x=150, y=95)

        fullname_label = CTkLabel(self.slides[0], text="Fullname", font=font_label, text_color="#666666", fg_color="white")
        fullname_label.place(x=150, y=180)
        self.fullname_entry = CTkEntry(self.slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.fullname_entry.place(x=150, y=220)

        phone_label = CTkLabel(self.slides[0], text="Phone Number", font=font_label, text_color="#666666", fg_color="white")
        phone_label.place(x=150, y=300)
        self.phone_entry = CTkEntry(self.slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.phone_entry.place(x=150, y=340)

        ic_label = CTkLabel(self.slides[0], text="IC Number", font=font_label, text_color="#666666", fg_color="white")
        ic_label.place(x=150, y=420)
        self.ic_entry = CTkEntry(self.slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.ic_entry.place(x=150, y=455)

        # Slide 2 (Email, Password, Confirm Password, OTP)
        email_label = CTkLabel(self.slides[1], text="Email Address", font=font_label, text_color="#666666", fg_color="white")
        email_label.place(x=150, y=50)
        self.email_entry = CTkEntry(self.slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
        self.email_entry.place(x=150, y=95)

        password_label = CTkLabel(self.slides[1], text="Password", font=font_label, text_color="#666666", fg_color="white")
        password_label.place(x=150, y=180)
        self.password_entry = CTkEntry(self.slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000", show="*")
        self.password_entry.place(x=150, y=220)

        con_password_label = CTkLabel(self.slides[1], text="Confirm Password", font=font_label, text_color="#666666", fg_color="white")
        con_password_label.place(x=150, y=300)
        self.con_password_entry = CTkEntry(self.slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="grey", show="*")
        self.con_password_entry.place(x=150, y=340)

        otp_label = CTkLabel(self.slides[1], text="OTP", font=font_label, text_color="#666666", fg_color="white")
        otp_label.place(x=150, y=420)
        self.otp_entry = CTkEntry(self.slides[1], width=580, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="grey")
        self.otp_entry.place(x=150, y=455)

        self.otp_button = CTkButton(self.slides[1], text="Request OTP", font=("arial", 28), text_color="#FFFFFF", fg_color="#c2b8ae", hover_color="#4682B4", corner_radius=20, width=200, height=60, command=self.send_otp)
        self.otp_button.place(x=750, y=455)

        self.status_label = CTkLabel(self.slides[1], text="", font=("arial", 20), text_color="#666666", fg_color="white")
        self.status_label.place(x=150, y=525)

        # Replace the separate next and back buttons with a single navigation button
        self.nav_button = CTkButton(self.right_frame, text="Next →", font=font_button, 
                                   text_color="#FFFFFF", fg_color="#c2b8ae", 
                                   hover_color="#4682B4", corner_radius=20, 
                                   width=150, height=50, 
                                   command=lambda: self.handle_navigation())
        self.nav_button.place(x=800, y=800)

        # Signup button
        self.signup_button = CTkButton(self.right_frame, text="SIGN UP", font=font_button, text_color="#000000", fg_color="#c2b8ae", hover_color="#c89ef2", corner_radius=20, width=800, height=70, command=self.verify_and_signup)
        self.signup_button.place(x=150, y=900)

        # Login Button on the left frame
        login_button = CTkButton(self.left_frame, text="LOGIN", font=font_button, text_color="white", fg_color="#c2b8ae", hover_color="#0056b3", width=140, height=60, border_width=2, border_color="#c2b8ae", command=self.create_login_page)
        login_button.place(x=360, y=800)

        # Create (but don't place) the continue button
        self.continue_button = CTkButton(self.right_frame, text="Continue to Face Setup", font=("Arial", 36), 
                                         text_color="#000000", fg_color="#c2b8ae", hover_color="#c89ef2", 
                                         corner_radius=20, width=800, height=70, command=self.start_face_setup)

        self.show_slide(0)

    def show_slide(self, index):
        self.slides[self.current_slide].place_forget()
        self.slides[index].place(x=0, y=200)
        self.current_slide = index
        
        # Update navigation button text based on current slide
        if index == 0:
            self.nav_button.configure(text="Next →", command=lambda: self.handle_navigation())
        else:
            self.nav_button.configure(text="← Back", command=lambda: self.handle_navigation())

    def handle_navigation(self):
        # If on first slide, go to second slide
        if self.current_slide == 0:
            self.show_slide(1)
        # If on second slide, go back to first slide
        else:
            self.show_slide(0)

    def send_otp(self):
        email = self.email_entry.get()
        if email:
            self.generated_otp = generate_otp()
            try:
                send_email(email, self.generated_otp)
                self.status_label.configure(text="OTP sent successfully!", text_color="green")
                cooldown_thread = threading.Thread(target=self.cooldown_timer)
                cooldown_thread.start()
            except Exception as e:
                self.status_label.configure(text=f"Failed to send OTP: {str(e)}", text_color="red")
        else:
            self.status_label.configure(text="Please enter an email address", text_color="red")

    def cooldown_timer(self):
        for i in range(30, 0, -1):
            if not self.master.winfo_exists() or not self.otp_button.winfo_exists():
                return  # Exit the method if the main window or button no longer exists
            self.otp_button.configure(text=f"{i}s", state="disabled", text_color="white", font=("Arial", 24, "bold"))
            self.otp_button.update()
            time.sleep(1)
        if self.master.winfo_exists() and self.otp_button.winfo_exists():
            self.otp_button.configure(text="Request OTP", state="normal", text_color="white", font=("arial", 28))

    def is_username_taken(self, username):
        try:
            self.cursor.execute("SELECT * FROM tenants WHERE username = ?", (username,))
            result = self.cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def validate_entries(self):
        # Check if all fields are filled
        fields = [
            (self.username_entry, "Username"),
            (self.fullname_entry, "Full Name"),
            (self.phone_entry, "Phone Number"),
            (self.ic_entry, "IC Number"),
            (self.email_entry, "Email Address"),
            (self.password_entry, "Password"),
            (self.con_password_entry, "Confirm Password"),
            (self.otp_entry, "OTP")
        ]
        
        for entry, field_name in fields:
            if not entry.get().strip():
                self.status_label.configure(text=f"{field_name} is required", text_color="red")
                return False

        # Check if username is taken
        if self.is_username_taken(self.username_entry.get().strip()):
            self.status_label.configure(text="Username is already taken", text_color="red")
            return False

        # Check if password matches confirm password
        if self.password_entry.get() != self.con_password_entry.get():
            self.status_label.configure(text="Passwords do not match", text_color="red")
            return False

        return True

    def verify_and_signup(self):
        if not self.validate_entries():
            return

        # Get the values
        phone_number = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        # Validate phone number
        if not is_valid_phone(phone_number):
            self.status_label.configure(text="Phone number must be 10 or 11 digits!", text_color="red")
            return

        # Validate email format
        if not is_valid_email(email):
            self.status_label.configure(text="Invalid email address format!", text_color="red")
            return

        entered_otp = self.otp_entry.get()
        if not hasattr(self, 'generated_otp'):
            self.status_label.configure(text="Please request an OTP first", text_color="red")
        elif entered_otp != self.generated_otp:
            self.status_label.configure(text="Incorrect OTP. Please try again.", text_color="red")
        else:
            # All validations passed
            self.status_label.configure(text="Sign up successful! Click 'Continue' to proceed with face setup.", text_color="green")
            
            # Hide the signup button and show the continue button
            self.signup_button.place_forget()
            self.continue_button.place(x=150, y=900)

    def start_face_setup(self):
        # Collect user information
        user_info = {
            'username': self.username_entry.get(),
            'fullName': self.fullname_entry.get(),
            'ICNumber': self.ic_entry.get(),
            'emailAddress': self.email_entry.get(),
            'phoneNumber': self.phone_entry.get(),
            'password': self.password_entry.get()
        }

        # Clear the signup page
        for widget in self.master.winfo_children():
            widget.destroy()

        # Initialize the face setup process with user info
        self.face_setup = FaceSetup(self.master, user_info)

    def __del__(self):
        # Close the database connection when the object is destroyed
        if hasattr(self, 'conn'):
            self.conn.close()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            # First get the stored hashed password for this username
            self.cursor.execute("SELECT * FROM tenants WHERE username = ?", (username,))
            user_data = self.cursor.fetchone()

            if user_data:
                # Get the stored password hash
                stored_password = user_data[6]  # Get the stored password hash
                try:
                    # Compare the entered password with stored hash
                    password_bytes = password.encode('utf-8')
                    # Convert stored_password from string back to bytes
                    stored_password_bytes = stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password
                    
                    if bcrypt.checkpw(password_bytes, stored_password_bytes):
                        self.current_user = {
                            'tenantID': user_data[0],
                            'username': user_data[1],
                            'fullName': user_data[2],
                            'ICNumber': user_data[3],
                            'emailAddress': user_data[4],
                            'phoneNumber': user_data[5],
                            'password': user_data[6],
                            'ICImagePath': user_data[7],
                            'FaceImagePath': user_data[8],
                            'icProblem': user_data[9] if len(user_data) > 9 else '0',
                            'profile_image': user_data[10] if len(user_data) > 10 else None
                        }
                        
                        # Clear the main window
                        for widget in self.master.winfo_children():
                            widget.destroy()
                        
                        # Import and initialize TenantDashboard
                        import sys
                        import importlib.util
                        
                        spec = importlib.util.spec_from_file_location(
                            "tenant_dashboard",
                            "tenant_dashboard.py"
                        )
                        tenant_dashboard_module = importlib.util.module_from_spec(spec)
                        sys.modules["tenant_dashboard"] = tenant_dashboard_module
                        spec.loader.exec_module(tenant_dashboard_module)
                        
                        tenant_dashboard_module.TenantDashboard(self.master, self.current_user)
                    else:
                        messagebox.showerror("Login Failed", "Invalid username or password")
                except ValueError as ve:
                    print(f"Password verification error: {ve}")
                    messagebox.showerror("Login Failed", "Invalid username or password")
                except Exception as e:
                    print(f"Password verification error: {e}")
                    messagebox.showerror("Login Failed", "Invalid username or password")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(f"Debug - Error details: {e}")

    def encrypt_password(self, password):
        """Encrypt a password using bcrypt"""
        # Convert the password to bytes
        password_bytes = password.encode('utf-8')
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        # Return the hashed password as a string
        return hashed_password.decode('utf-8')

class FaceSetup:
    def __init__(self, master, user_info):
        self.master = master
        self.user_info = user_info
        self.images_folder = "user_images"  # Folder to store user images
        self.ensure_images_folder_exists()
        self.captured_image_path = os.path.join(self.images_folder, f"{self.user_info['username']}_face.jpg")
        self.id_card_image_path = ""

        # Connect to the database
        self.conn = sqlite3.connect('properties.db')
        self.cursor = self.conn.cursor()
        
        # Ensure database schema is up to date
        self.ensure_database_schema()

        # Load the face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Initialize the webcam
        self.video_capture = cv2.VideoCapture(0)

        self.create_face_setup_page()

    def create_face_setup_page(self):
        # Clear existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        self.buttonFrame = CTkFrame(self.master, fg_color="black", width=1920, height=30)
        self.buttonFrame.place(x=0, y=0)
        
        closeButton = CTkButton(self.master, text="X", command=self.master.destroy, fg_color="black", hover_color="red", text_color="white", width=50, height=30)
        closeButton.place(x=1870, y=0)

        self.titleFrame = CTkFrame(self.master, width=900, height=100)
        self.titleFrame.place(x=960, y=150, anchor=CENTER)
        titleLabel = CTkLabel(self.titleFrame, text="Take a selfie of yourself", font=('Franklin Gothic Medium', 50, "bold"))
        titleLabel.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.statusFrame = CTkFrame(self.master, width=1000, height=50)
        self.statusFrame.place(x=960, y=1000, anchor=CENTER)

        self.cameraFrame = CTkFrame(self.master, width=800, height=700)
        self.cameraFrame.place(x=235, y=250)
        self.video_label = CTkLabel(self.cameraFrame, text="", width=800, height=700)
        self.video_label.place(x=0, y=0)

        self.instructionFrame = CTkFrame(self.master, width=500, height=600)
        self.instructionFrame.place(x=1185, y=250)
        instructionText = CTkTextbox(self.instructionFrame, width=480, height=600, font=("Franklin Gothic Medium", 20), wrap='word')
        instructionText.insert("1.0",
            "1. Make sure you are in a well-lit area.\n\n"
            "2. Remove any obstructions like hats, sunglasses, etc.\n\n"
            "3. Keep your face centered and look directly at the camera.\n\n"
            "4. Avoid shadows across your face.\n\n"
            "5. Hold still while the picture is taken, and follow on-screen prompts.\n\n"
            "6. These instructions will make it easier to recognize your face.\n\n"
            "7. Make sure you follow the guidelines correctly to avoid errors in the system processing your photo."
        )
        instructionText.configure(state="disabled")
        instructionText.place(x=10, y=100)

        self.captureButton = CTkButton(self.cameraFrame, text="Capture Image", font=('Arial', 20), command=self.capture_image, state=DISABLED)
        self.captureButton.place(x=400, y=650, anchor=CENTER)

        self.statusLabel = CTkLabel(self.statusFrame, text="Please position yourself in front of the camera", font=('Arial', 15))
        self.statusLabel.place(x=500, y=30, anchor=CENTER)

        # Reinitialize the webcam
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.video_capture = cv2.VideoCapture(0)

        # Start updating the webcam feed
        self.update_frame()

    def update_frame(self):
        ret, frame = self.video_capture.read()

        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            faces = self.detect_faces(frame)

            if len(faces) > 0:
                self.captureButton.configure(state=NORMAL)
                self.statusLabel.configure(text="Face detected. Ready to capture.")
            else:
                self.captureButton.configure(state=DISABLED)
                self.statusLabel.configure(text="No face detected. Please position yourself in front of the camera.")

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.video_label.after(10, self.update_frame)

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        return faces

    def ensure_images_folder_exists(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

    def capture_image(self):
        ret, frame = self.video_capture.read()
        if ret:
            cv2.imwrite(self.captured_image_path, frame)
            self.show_image_confirmation()

    def show_image_confirmation(self):
        self.cameraFrame.place_forget()
        self.instructionFrame.place_forget()
        self.titleFrame.place_forget()
        self.statusFrame.place_forget()

        confirm_frame = CTkFrame(self.master, width=1920, height=1050)
        confirm_frame.place(x=0, y=30)

        img = Image.open(self.captured_image_path)
        img = img.resize((640, 480), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        img_label = CTkLabel(confirm_frame, text="", image=img_tk)
        img_label.image = img_tk
        img_label.place(relx=0.5, rely=0.4, anchor=CENTER)

        saveButton = CTkButton(confirm_frame, text="Save", command=lambda: self.save_image(confirm_frame))
        discardButton = CTkButton(confirm_frame, text="Discard", command=lambda: self.discard_image(confirm_frame))

        saveButton.place(relx=0.4, rely=0.7, anchor=CENTER)
        discardButton.place(relx=0.6, rely=0.7, anchor=CENTER)

    def save_image(self, confirm_frame):
        confirm_frame.place_forget()
        self.statusLabel.configure(text=f"Image saved at {self.captured_image_path}")
        self.show_id_card_upload()

    def discard_image(self, confirm_frame):
        confirm_frame.destroy()  # Destroy the confirmation frame
        if os.path.exists(self.captured_image_path):
            os.remove(self.captured_image_path)
        
        # Recreate the face setup page
        self.create_face_setup_page()

    def show_id_card_upload(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        upload_frame = CTkFrame(self.master, width=1920, height=1050)
        upload_frame.place(x=0, y=30)

        idStatusFrame = CTkFrame(self.master, width=1000, height=50)
        idStatusFrame.place(x=960, y=1000, anchor=CENTER)

        instruction_label = CTkLabel(upload_frame, text="Please upload your ID card", font=("Arial", 40, "bold"))
        instruction_label.place(x=960, y=200, anchor=CENTER)

        upload_button = CTkButton(upload_frame, text="Upload ID Card", font=("Arial", 20), command=lambda: self.upload_id_card(upload_frame))
        upload_button.place(x=960, y=300, anchor=CENTER)

        self.idStatusLabel = CTkLabel(idStatusFrame, text="Please upload the picture of I/C", font=('Arial', 15))
        self.idStatusLabel.place(x=500, y=30, anchor=CENTER)

    def upload_id_card(self, frame):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])

        if file_path:
            # Create a new filename for the ID card image
            id_card_filename = f"{self.user_info['username']}_id_card{os.path.splitext(file_path)[1]}"
            self.id_card_image_path = os.path.join(self.images_folder, id_card_filename)
            
            # Copy the selected file to our images folder
            import shutil
            shutil.copy2(file_path, self.id_card_image_path)

            img = Image.open(self.id_card_image_path)
            img = img.resize((500, 315), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            img_label = CTkLabel(frame, text="", image=img_tk)
            img_label.image = img_tk
            img_label.place(x=960, y=500, anchor=CENTER)

            self.idStatusLabel.configure(text=f"ID card uploaded: {self.id_card_image_path}")
            self.compare_faces()

    def compare_faces(self):
        try:
            model_name = "VGG-Face"
            distance_metric = "cosine"
            custom_threshold = 0.70

            result = DeepFace.verify(
                img1_path=self.captured_image_path,
                img2_path=self.id_card_image_path,
                model_name=model_name,
                distance_metric=distance_metric,
                enforce_detection=False,
                threshold=custom_threshold
            )

            self.face_match_successful = result["verified"]
            if self.face_match_successful:
                self.update_database(self.captured_image_path, self.id_card_image_path)
                self.idStatusLabel.configure(text="Face match successful! Data saved to database.")
                self.show_success_message()
            else:
                self.handle_face_mismatch()
        except Exception as e:
            self.handle_comparison_error(str(e))

    def handle_face_mismatch(self):
        response = messagebox.askyesno("Face Mismatch", 
                                       "The captured image doesn't match the ID card. Do you want to continue anyway?")
        if response:
            self.face_match_successful = False
            self.update_database(self.captured_image_path, self.id_card_image_path)
            self.idStatusLabel.configure(text="Data saved to database despite mismatch.")
            self.show_success_message()
        else:
            self.idStatusLabel.configure(text="Face match failed. Please try again.")

    def handle_comparison_error(self, error_message):
        response = messagebox.askyesno("Comparison Error", 
                                       f"An error occurred during face comparison: {error_message}\n\nDo you want to continue anyway?")
        if response:
            self.face_match_successful = False
            self.update_database(self.captured_image_path, self.id_card_image_path)
            self.idStatusLabel.configure(text="Data saved to database despite comparison error.")
            self.show_success_message()
        else:
            self.idStatusLabel.configure(text=f"Error in face comparison. Please try again.")

    def show_success_message(self):
        messagebox.showinfo("Registration Complete", "Your registration is complete. You can now log in to your account.")
        self.conn.close()  # Close the database connection
        
        # Clear the current window
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Create new instance of CombinedApp to show login page
        CombinedApp(self.master)

    def update_database(self, faceImagePath, ICImagepath):
        try:
            # Encrypt the password before storing
            encrypted_password = self.encrypt_password(self.user_info['password'])
            
            # Determine the icProblem value based on face comparison result
            icProblem = "1" if not hasattr(self, 'face_match_successful') or not self.face_match_successful else "0"
            
            self.cursor.execute("""
                INSERT INTO tenants (
                    username, fullName, ICNumber, emailAddress, phoneNumber, 
                    password, ICImagePath, FaceImagePath, icProblem, profile_image
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_info['username'],
                self.user_info['fullName'],
                self.user_info['ICNumber'],
                self.user_info['emailAddress'],
                self.user_info['phoneNumber'],
                encrypted_password,  # Store the encrypted password
                ICImagepath,
                faceImagePath,
                icProblem,
                faceImagePath
            ))
            self.conn.commit()
            print("User information saved successfully.")
        except sqlite3.Error as e:
            print(f"Error updating database: {e}")

    def ensure_database_schema(self):
        try:
            # Check if profile_image column exists
            self.cursor.execute("PRAGMA table_info(tenants)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Add profile_image column if it doesn't exist
            if 'profile_image' not in columns:
                self.cursor.execute("ALTER TABLE tenants ADD COLUMN profile_image TEXT")
                # Set existing profile_image values to match FaceImagePath
                self.cursor.execute("UPDATE tenants SET profile_image = FaceImagePath WHERE profile_image IS NULL")
                self.conn.commit()
                print("Added profile_image column to tenants table")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def encrypt_password(self, password):
        """Encrypt a password using bcrypt"""
        # Convert the password to bytes
        password_bytes = password.encode('utf-8')
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        # Return the hashed password as a string
        return hashed_password.decode('utf-8')

def main():
    root = CTk()
    app = CombinedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
