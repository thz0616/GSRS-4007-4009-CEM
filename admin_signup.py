from customtkinter import *
import tkinter as tk
from admin_entity import insert_admin
from tkinter import messagebox
import sqlite3
from sqlite3 import Error
import re  # For email validation
import os  # For os.system
import subprocess

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.geometry("1920x1080")
root.title("Signup Page")
root.resizable(False, False)
root.attributes("-fullscreen", True)

# Define screen dimensions
screen_width = 1920
screen_height = 1080

# Left and right frame widths
left_frame_width = 800
right_frame_width = 1120  # 1920 - 800 = 1120

# Create left and right frames
left_frame = CTkFrame(root, width=left_frame_width, height=screen_height)
left_frame.place(x=0, y=0)
right_frame = CTkFrame(root, width=right_frame_width, height=screen_height, fg_color="white")
right_frame.place(x=left_frame_width, y=0)


# Function to create a vertical gradient on the canvas
def create_gradient(canvas, width, height, color1, color2):
    limit = height
    (r1, g1, b1) = root.winfo_rgb(color1)
    (r2, g2, b2) = root.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / limit
    g_ratio = float(g2 - g1) / limit
    b_ratio = float(b2 - b1) / limit

    for i in range(limit):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = "#%04x%04x%04x" % (nr, ng, nb)
        canvas.create_line(0, i, width, i, fill=color)


# Create a canvas in the left frame and add the gradient background
gradient_canvas = tk.Canvas(left_frame, width=left_frame_width, height=screen_height, highlightthickness=0)
gradient_canvas.place(x=0, y=0)
create_gradient(gradient_canvas, left_frame_width, screen_height, "#d1c4e9", "#f8bbd0")  # Purple to pink gradient

# Fonts (Adjusted sizes for better visibility)
font_header = ("Arial", 56, "bold")  # Reduced header font
font_subheader = ("Arial", 28)  # Reduced subheader font
font_label = ("Arial", 20)  # Reduced label font
font_input = ("Arial", 20)  # Reduced input font
font_button = ("Arial", 28)  # Reduced button font
font_signup = ("Arial", 24)  # Reduced font for signup label

# Create slides for fields
slides = [CTkFrame(right_frame, width=right_frame_width, height=screen_height, fg_color="white") for _ in range(2)]
current_slide = 0


def show_slide(index):
    global current_slide
    slides[current_slide].place_forget()  # Hide the current slide
    slides[index].place(x=0, y=0)  # Show the new slide
    current_slide = index


# First slide (Username, Phone Number, Full Name, IC Number)
username_label = CTkLabel(slides[0], text="Username", font=font_label, text_color="#666666", fg_color="white")
username_label.place(x=150, y=310)

username_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                          fg_color="white", text_color="#000000")
username_entry.place(x=150, y=350)

phone_label = CTkLabel(slides[0], text="Phone Number", font=font_label, text_color="#666666", fg_color="white")
phone_label.place(x=150, y=420)

phone_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                       fg_color="white", text_color="#000000")
phone_entry.place(x=150, y=460)

fullname_label = CTkLabel(slides[0], text="Fullname", font=font_label, text_color="#666666", fg_color="white")
fullname_label.place(x=150, y=530)

fullname_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                          fg_color="white", text_color="#000000")
fullname_entry.place(x=150, y=570)

ic_label = CTkLabel(slides[0], text="IC Number", font=font_label, text_color="#666666", fg_color="white")
ic_label.place(x=150, y=640)

ic_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                    fg_color="white", text_color="#000000")
ic_entry.place(x=150, y=680)

# Second slide (Email, Password, Confirm Password, Passcode)
email_label = CTkLabel(slides[1], text="Email Address", font=font_label, text_color="#666666", fg_color="white")
email_label.place(x=150, y=310)

email_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                       fg_color="white", text_color="#000000")
email_entry.place(x=150, y=350)

password_label = CTkLabel(slides[1], text="Password", font=font_label, text_color="#666666", fg_color="white")
password_label.place(x=150, y=420)

password_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                          fg_color="white", text_color="#000000", show="*")
password_entry.place(x=150, y=460)

confirm_password_label = CTkLabel(slides[1], text="Confirm Password", font=font_label, text_color="#666666", fg_color="white")
confirm_password_label.place(x=150, y=530)

confirm_password_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                          fg_color="white", text_color="#000000", show="*")
confirm_password_entry.place(x=150, y=570)

passcode_label = CTkLabel(slides[1], text="Passcode", font=font_label, text_color="#666666", fg_color="white")
passcode_label.place(x=150, y=640)

passcode_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                          fg_color="white", text_color="grey")
passcode_entry.place(x=150, y=680)

# "Next" button on the first slide
next_button = CTkButton(
    slides[0], text="Next", font=font_button, text_color="#000000", fg_color="#d0a9f5", hover_color="#c89ef2",
    corner_radius=20, width=140, height=40, command=lambda: show_slide(1)
)
next_button.place(x=800, y=760)

# "Back" button on the second slide
back_button = CTkButton(
    slides[1], text="Back", font=font_button, text_color="#000000", fg_color="#d0a9f5", hover_color="#c89ef2",
    corner_radius=20, width=140, height=40, command=lambda: show_slide(0)
)
back_button.place(x=800, y=760)

# Position the "Sign up" header and subheader lower
signup_header = CTkLabel(
    right_frame, text="Sign up", font=font_header, text_color="#000000", fg_color="white"
)
signup_header.place(x=150, y=150)  # Moved lower

welcome_label = CTkLabel(
    right_frame,
    text="Please fill in all the columns.",
    font=font_subheader,
    text_color="#808080",
    fg_color="white",
)
welcome_label.place(x=150, y=230)  # Moved lower

# Signup Button (Positioned higher)
def handle_signup():
    if validate_signup_data():
        messagebox.showinfo("Success", "Admin account created successfully!")
        switch_to_login()
    # If validation fails, error message is already shown by validate_signup_data

signup_button = CTkButton(
    right_frame, 
    text="SIGN UP", 
    font=font_button, 
    text_color="#000000", 
    fg_color="#d0a9f5", 
    hover_color="#c89ef2",
    corner_radius=20, 
    width=800, 
    height=70,
    command=handle_signup
)
signup_button.place(x=150, y=830)  # Positioned higher


# "Already have an account? Login" Labels (Positioned higher)
def on_login_click():
    switch_to_login()


new_user_label = CTkLabel(right_frame, text="Already have an account? ", font=font_signup, text_color="#808080",
                          fg_color="white")
new_user_label.place(x=150, y=930)  # Positioned higher

login_label = CTkLabel(right_frame, text="Login", font=(font_signup[0], font_signup[1], "underline"),
                       text_color="#9a68ed", fg_color="white")
login_label.place(x=450, y=930)  # Positioned higher
login_label.bind("<Button-1>", lambda e: on_login_click())
login_label.configure(cursor="hand2")

# Show the first slide initially
show_slide(0)

# Add these new variables and functions after the initial setup
current_page = "signup"  # Track current page (signup or login)
login_frame = None  # Will hold the login frame

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

def get_current_passcode():
    """Get the current passcode from systemInformation table"""
    conn = create_connection()
    
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT passcode 
                FROM systemInformation 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result and result[0]:  # Check if result exists and passcode is not None/empty
                return result[0]
            return None  # Return None if no passcode is set
            
        except Error as e:
            print(f"Error getting passcode: {e}")
            return None  # Return None on error
            
        finally:
            conn.close()
    return None  # Return None if no connection

def validate_signup_data():
    # Store the actual password values before validation
    actual_password = password_entry.get()
    actual_confirm_password = confirm_password_entry.get()
    
    # Get all the entry values
    username = username_entry.get().strip()
    phone = phone_entry.get().strip()
    fullname = fullname_entry.get().strip()
    ic = ic_entry.get().strip()
    email = email_entry.get().strip()
    passcode = passcode_entry.get()

    # Check if any field is empty
    if not all([username, phone, fullname, ic, email, actual_password, actual_confirm_password, passcode]):
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        messagebox.showerror("Error", "All fields are required!")
        return False

    # Validate phone number
    if not is_valid_phone(phone):
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        messagebox.showerror("Error", "Phone number must be 10 or 11 digits!")
        return False

    # Validate email format
    if not is_valid_email(email):
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        messagebox.showerror("Error", "Invalid email address format!")
        return False

    # Check if passwords match
    if actual_password != actual_confirm_password:
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        messagebox.showerror("Error", "Passwords do not match!")
        return False

    # Get current passcode from database and check
    current_passcode = get_current_passcode()
    if passcode != current_passcode:
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        messagebox.showerror("Error", "Invalid passcode! Please contact system administrator.")
        return False

    # Try to insert into database using the actual password
    success = insert_admin(
        username=username,
        phone_number=phone,
        fullname=fullname,
        ic_number=ic,
        email=email,
        password=actual_password  # Use the actual password for database storage
    )

    if not success:
        # Restore the actual password values after validation error
        password_entry.delete(0, 'end')
        password_entry.insert(0, actual_password)
        confirm_password_entry.delete(0, 'end')
        confirm_password_entry.insert(0, actual_confirm_password)
        return False

    return True

def switch_to_login():
    global current_page, login_frame
    
    # Hide signup components
    right_frame.place_forget()
    
    # Create and show login frame if it doesn't exist
    if not login_frame:
        login_frame = CTkFrame(root, width=right_frame_width, height=screen_height, fg_color="white")
        
        # Login header - moved down slightly
        login_header = CTkLabel(
            login_frame, text="Login", font=font_header, text_color="#000000", fg_color="white"
        )
        login_header.place(x=150, y=180)  # Was 150

        welcome_label = CTkLabel(
            login_frame,
            text="Welcome back! Please login to your account.",
            font=font_subheader,
            text_color="#808080",
            fg_color="white",
        )
        welcome_label.place(x=150, y=280)  # Was 230

        # Username - moved down
        username_label = CTkLabel(login_frame, text="Username", font=font_label, text_color="#666666", fg_color="white")
        username_label.place(x=150, y=380)  # Was 310
 
        username_entry = CTkEntry(login_frame, width=800, height=60, font=font_input, corner_radius=20, 
                                border_color="#CCCCCC", fg_color="white", text_color="#000000")
        username_entry.place(x=150, y=420)  # Was 350

        # Password - moved down and increased spacing
        password_label = CTkLabel(login_frame, text="Password", font=font_label, text_color="#666666", fg_color="white")
        password_label.place(x=150, y=520)  # Was 420

        password_entry = CTkEntry(login_frame, width=800, height=60, font=font_input, corner_radius=20, 
                                border_color="#CCCCCC", fg_color="white", text_color="#000000", show="*")
        password_entry.place(x=150, y=560)  # Was 460

        # Login Button - moved down
        def verify_and_login():
            username = username_entry.get().strip()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password!")
                return
            
            admin_data = verify_admin_login(username, password)
            if admin_data:
                admin_id, admin_username = admin_data
                messagebox.showinfo("Success", "Login successful!")
                
                # Launch dashboard without showing console
                import sys
                import os
                import subprocess
                
                # Get the current directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                dashboard_path = os.path.join(current_dir, "admin_dashboard_2.py")
                
                # Start the dashboard process without console window
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen([sys.executable, dashboard_path, str(admin_id)], 
                                creationflags=CREATE_NO_WINDOW)
                
                # Force quit the program
                root.quit()
                root.destroy()
                sys.exit()
            else:
                messagebox.showerror("Error", "Invalid username or password!")

        login_button = CTkButton(
            login_frame, 
            text="LOGIN", 
            font=font_button, 
            text_color="#000000", 
            fg_color="#d0a9f5", 
            hover_color="#c89ef2",
            corner_radius=20, 
            width=800, 
            height=70,
            command=verify_and_login
        )
        login_button.place(x=150, y=700)  # Was 580

        # "Don't have an account? Sign up" Labels - moved down
        new_user_label = CTkLabel(login_frame, text="Don't have an account? ", 
                                font=font_signup, text_color="#808080", fg_color="white")
        new_user_label.place(x=150, y=830)  # Was 680

        signup_label = CTkLabel(login_frame, text="Sign up", 
                              font=(font_signup[0], font_signup[1], "underline"),
                              text_color="#9a68ed", fg_color="white")
        signup_label.place(x=450, y=830)  # Was 680
        signup_label.bind("<Button-1>", lambda e: switch_to_signup())
        signup_label.configure(cursor="hand2")

    login_frame.place(x=left_frame_width, y=0)
    current_page = "login"

def switch_to_signup():
    global current_page
    if login_frame:
        login_frame.place_forget()
    right_frame.place(x=left_frame_width, y=0)
    current_page = "signup"

# Add these database functions before the GUI code
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
                    messagebox.showerror("Error", "Username already exists!")
                elif "ic_number" in str(e):
                    messagebox.showerror("Error", "IC number already exists!")
                elif "email" in str(e):
                    messagebox.showerror("Error", "Email already exists!")
            return False
            
        except Error as e:
            print(f"Error inserting admin: {e}")
            messagebox.showerror("Error", "Failed to create account!")
            return False
            
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        messagebox.showerror("Error", "Database connection failed!")
        return False

def verify_admin_login(username, password):
    """Verify admin login credentials and return admin data"""
    conn = create_connection()
    
    if conn is not None:
        try:
            sql = "SELECT id, username FROM admin WHERE username = ? AND password = ?"
            cursor = conn.cursor()
            cursor.execute(sql, (username, password))
            admin = cursor.fetchone()
            return admin  # Returns (id, username) tuple or None
            
        except Error as e:
            print(f"Error verifying admin login: {e}")
            return None
            
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return None

# Create admin table when the program starts
create_admin_table()

# Show login page initially instead of signup
def show_initial_login():
    switch_to_login()  # Call the existing switch_to_login function

# Call this function after all GUI elements are created
show_initial_login()

# Start the main loop
root.mainloop()
