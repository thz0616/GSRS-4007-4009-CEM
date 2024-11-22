from customtkinter import *
import customtkinter as ctk
import tkinter as tk
from tkinter import Frame, Scrollbar
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog
import os
import sqlite3
from mystall20241019 import open_mystall_window
from tenantviewstall20241006 import open_viewstall_window
from User_Payment_Final import open_payment_window
#from give_feedback import open_givefeedback_window
from view_messages import ViewMessagesPage
import tkinter.messagebox as messagebox
import subprocess
import sys
from tenant_support_chatbot import TenantSupportChatbot
from tkinter import ttk
import time
import threading
import re
from tenant_signup_with_face_setup import CombinedApp


class PhotoSlideshow:
    def __init__(self, parent, images, delay):
        self.parent = parent
        # Create rounded corner images
        self.images = []
        for image_path in images:
            # Open and resize the image
            img = Image.open(image_path).resize((1200, 370))
            
            # Create a rounded rectangle mask
            mask = Image.new('L', (1200, 370), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (1200, 370)], radius=30, fill=255)
            
            # Apply the mask to create rounded corners
            output = Image.new('RGBA', (1200, 370), (0, 0, 0, 0))
            output.paste(img, mask=mask)
            
            # Convert to PhotoImage and store
            photo = ImageTk.PhotoImage(output)
            self.images.append(photo)
            
        self.current_image = 0
        self.label = tk.Label(self.parent, image=self.images[self.current_image], bg="#fffcf7")
        self.label.place(x=130, y=40)
        self.delay = delay
        self.update_image()

    def update_image(self):
        self.current_image = (self.current_image + 1) % len(self.images)
        self.label.config(image=self.images[self.current_image])
        self.parent.after(self.delay, self.update_image)


class TenantDashboard:
    def __init__(self, master, user_data):
        self.master = master
        self.user_data = user_data  # Store the user data passed from login

        # Configure the window
        self.master.geometry("1920x1080")
        self.master.title("Tenant Dashboard")
        self.master.resizable(False, False)
        self.master.attributes("-fullscreen", True)

        # Create main frames - swap positions
        self.right_frame = CTkFrame(self.master, width=1420, height=1080, fg_color="#fffcf7")
        self.right_frame.place(x=0, y=0)  # Changed x from 500 to 0
        
        self.left_frame = CTkFrame(self.master, width=500, height=1080, fg_color="#c2b8ae")
        self.left_frame.place(x=1420, y=0)  # Changed x from 0 to 1420

        # Initialize UI elements
        self.setup_slideshow()
        self.setup_navigation_buttons()
        self.setup_profile_section()
        self.setup_menu_options()

    def setup_slideshow(self):
        # Fetch banner images from database
        image_files = self.fetch_banner_images()
        
        # Activity header
        activity_header = CTkLabel(self.right_frame, text="Activity", 
                                 font=("Goudy Old Style", 56, "bold"), 
                                 text_color="black")
        activity_header.place(x=150, y=450)
        
        # Create slideshow if we have images
        if image_files:
            self.slideshow = PhotoSlideshow(self.right_frame, image_files, 3000)

    def setup_navigation_buttons(self):
        try:
            # Load button images with error handling
            button_images = {}
            image_files = {
                'my_store': "my store.png",
                'view_store': "view store.jpeg",
                'payment': "payment.jpeg",
                'message': "message.jpeg"
            }
            
            for key, file_path in image_files.items():
                if os.path.exists(file_path):
                    button_images[key] = CTkImage(
                        light_image=Image.open(file_path),
                        size=(50, 50)
                    )
                else:
                    print(f"Warning: Image file not found: {file_path}")
                    button_images[key] = None  # Use None if image not found

            # Create navigation buttons with updated text labels
            buttons = [
                ("My Stall", button_images.get('my_store'), "#f6e4e3", lambda: self.open_my_stall(), 540),
                ("View Stall", button_images.get('view_store'), "#f6e4e3", 
                 lambda: self.open_view_stall(), 670),
                ("Payment", button_images.get('payment'), "#f6e4e3", lambda: self.open_payment_window(), 800),
                ("Message and Announcement", button_images.get('message'), "#f6e4e3", lambda: ViewMessagesPage().run(), 930)
            ]

            for text, image, color, command, y_pos in buttons:
                CTkButton(
                    self.right_frame,
                    text=text,
                    image=image if image is not None else None,
                    font=("Arial", 28),
                    text_color="#654633",  # Keep text color consistent
                    fg_color=color,  # Updated to #f6e4e3
                    hover_color="#c89ef2",
                    corner_radius=20,
                    width=1150,
                    height=100,
                    command=command
                ).place(x=130, y=y_pos)

        except Exception as e:
            print(f"Error setting up navigation buttons: {e}")
            # Create buttons without images as fallback
            buttons = [
                ("My Stall", "#E7D7C7", lambda: self.open_my_stall(), 540),
                ("View Stall", "#d4b2a9", open_viewstall_window, 670),
                ("Payment", "#cfc5c3", open_payment_window, 800),
                ("Message and Announcement", "#A29086", lambda: ViewMessagesPage().run(), 930)
            ]

            for text, color, command, y_pos in buttons:
                CTkButton(
                    self.right_frame,
                    text=text,
                    font=("Arial", 28),
                    text_color="#654633" if text != "Message and Announcement" else "#f8e5e5",
                    fg_color=color,
                    hover_color="#c89ef2",
                    corner_radius=20,
                    width=1150,
                    height=100,
                    command=command
                ).place(x=130, y=y_pos)

    def setup_profile_section(self):
        # Display profile image
        self.display_profile_image()

        # Profile label
        profile_label = CTkLabel(
            self.left_frame,
            text="My Profile",
            font=("Goudy Old Style", 28, "underline"),
            text_color="black",
            fg_color="#c2b8ae"
        )
        profile_label.place(x=195, y=400)
        profile_label.bind("<Button-1>", lambda e: self.open_profile_update_window())
        profile_label.configure(cursor="hand2")

    def setup_menu_options(self):
        # Create menu options (Contact, Feedback, Logout)
        options = [
            ("Contact us", self.on_contact_click, 460),
            ("Feedback", self.on_feedback_click, 520),
            ("Logout", self.on_logout_click, 980)
        ]

        for text, command, y_pos in options:
            label = CTkLabel(
                self.left_frame,
                text=text,
                font=("Goudy Old Style", 28, "underline"),
                text_color="black",
                fg_color="#c2b8ae"
            )
            label.place(x=195 if text != "Logout" else 210, y=y_pos)
            label.bind("<Button-1>", lambda e, cmd=command: cmd())
            label.configure(cursor="hand2")

    # ... [Keep all the existing helper methods like create_circular_image,
    #      display_profile_image, fetch_banner_images, etc.]

    def on_contact_click(self):
        # Create a new window for the chatbot
        chat_window = CTkToplevel()
        chat_window.title("Contact Support")
        chat_window.geometry("1920x1080")
        chat_window.attributes("-fullscreen", True)
        
        # Initialize the chatbot with the container as parent and dashboard reference
        chatbot = TenantSupportChatbot(chat_window, self)
        
        # Configure the chat window to close properly
        def on_closing():
            chat_window.destroy()
            self.master.deiconify()
        
        chat_window.protocol("WM_DELETE_WINDOW", on_closing)
        self.master.withdraw()

    def on_feedback_click(self):
        try:
            # Launch the feedback window using subprocess with tenant ID
            process = subprocess.Popen([
                sys.executable, 
                'give_feedback.py',
                '--tenant_id',
                str(self.user_data['tenantID'])
            ])
            
            # Hide the main window
            self.master.withdraw()
            
            # Wait for the feedback window to close
            process.wait()
            
            # Show the main window again
            self.master.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open feedback window: {e}")
            self.master.deiconify()  # Make sure main window is shown if there's an error

    def on_logout_click(self):
        # Import the CombinedApp class
        from tenant_signup_with_face_setup import CombinedApp
        
        # Destroy the current dashboard window
        self.master.destroy()
        
        # Create a new window for login
        new_window = CTk()
        CombinedApp(new_window)
        new_window.mainloop()

    def fetch_banner_images(self):
        db_path = "properties.db"
        default_images = [
            "banner1.jpg",
            "banner2.jpg",
            "banner3.jpg"
        ]
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # First get the latest system_info_id
            cursor.execute("SELECT MAX(id) FROM systemInformation")
            latest_system_id = cursor.fetchone()[0]
            
            if latest_system_id is None:
                print("No system information found")
                conn.close()
                return default_images

            # Fetch all banner images for the latest system_info_id
            cursor.execute("""
                SELECT image_path 
                FROM bannerImages 
                WHERE system_info_id = ? 
                ORDER BY id
            """, (latest_system_id,))
            
            images = [row[0] for row in cursor.fetchall()]
            conn.close()

            # If no images found in database, use default images
            if not images:
                print("No banner images found in database, using defaults")
                return default_images

            # Verify each image path exists
            valid_images = []
            for img_path in images:
                if os.path.exists(img_path):
                    valid_images.append(img_path)
                else:
                    print(f"Warning: Image not found at path: {img_path}")

            # If no valid images found, use defaults
            return valid_images if valid_images else default_images

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return default_images
        except Exception as e:
            print(f"Error fetching banner images: {e}")
            return default_images

    def create_circular_image(self, image_path, size):
        img = Image.open(image_path).resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        circular_img = Image.new("RGBA", (size, size))
        circular_img.paste(img, (0, 0), mask)
        return circular_img

    def display_profile_image(self):
        try:
            # Connect to database to fetch profile_image
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()
            
            # Get tenantID from user_data
            tenant_id = self.user_data.get('tenantID')
            
            # Fetch profile_image for the current tenant
            cursor.execute("SELECT profile_image FROM tenants WHERE tenantID = ?", (tenant_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                image_path = result[0]
                
                # Check if file exists
                if os.path.exists(image_path):
                    try:
                        circular_img = self.create_circular_image(image_path, 230)
                        profile_image_tk = ImageTk.PhotoImage(circular_img)
                        profile_label = tk.Label(self.left_frame, image=profile_image_tk, background="#c2b8ae")
                        profile_label.image = profile_image_tk  # Keep a reference
                        profile_label.place(x=140, y=100)
                    except Exception as e:
                        print(f"Error creating/displaying circular image: {e}")
                else:
                    print(f"Profile image not found at path: {image_path}")
                    # You might want to display a default image here
            else:
                print("No profile image found for tenant")
                
            conn.close()
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error displaying profile image: {e}")

    def open_profile_update_window(self):
        self.master.withdraw()  # Hide the main window
        profile_window = CTkToplevel(fg_color="#f4f1e9")
        profile_window.geometry("1920x1080")
        profile_window.title("Update Profile")
        profile_window.resizable(False, False)
        profile_window.attributes("-fullscreen", True)

        # Database path
        db_path = "properties.db"

        # Get tenant data from user_data instead of querying database
        username = self.user_data.get('username', '')
        fullname = self.user_data.get('fullName', '')
        phone_number = self.user_data.get('phoneNumber', '')
        ic_number = self.user_data.get('ICNumber', '')
        email = self.user_data.get('emailAddress', '')
        profile_image_path = self.user_data.get('profile_image', '')

        # Scrollable frame for form fields
        scrollable_frame = Frame(profile_window)
        scrollable_frame.place(x=0, y=0, relwidth=1, relheight=1)
        scrollbar = Scrollbar(scrollable_frame)
        scrollbar.pack(side="right", fill="y")

        # Get profile image path - first try profile_image, then fallback to FaceImagePath
        profile_image_path = None
        try:
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()
            cursor.execute("SELECT profile_image FROM tenants WHERE tenantID = ?", (self.user_data['tenantID'],))
            result = cursor.fetchone()
            if result and result[0]:
                profile_image_path = result[0]
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

        # Profile image display
        profile_image_label = tk.Label(scrollable_frame, bg="#f4f1e9")  # Match background color
        profile_image_label.place(x=300, y=150)
        
        # Try to display the profile image
        if profile_image_path and os.path.exists(profile_image_path):
            try:
                circular_img = self.create_circular_image(profile_image_path, 200)
                profile_image_tk = ImageTk.PhotoImage(circular_img)
                profile_image_label.config(image=profile_image_tk)
                profile_image_label.image = profile_image_tk  # Keep a reference
            except Exception as e:
                print(f"Error displaying profile image: {e}")
        else:
            print("No valid profile image path found")

        def update_profile_image_in_window(image_path):
            if os.path.exists(image_path):
                try:
                    circular_img = self.create_circular_image(image_path, 200)
                    profile_image_tk = ImageTk.PhotoImage(circular_img)
                    profile_image_label.config(image=profile_image_tk)
                    profile_image_label.image = profile_image_tk  # Keep a reference
                except Exception as e:
                    print(f"Error updating profile image: {e}")

        def change_profile_image():
            new_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if new_image_path:
                update_profile_image_in_window(new_image_path)
                nonlocal profile_image_path
                profile_image_path = new_image_path

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

        def save_profile_updates():
            updated_username = username_entry.get()
            updated_fullname = fullname_entry.get()
            updated_phone_number = phone_entry.get()
            updated_ic_number = ic_entry.get()
            updated_email = email_entry.get()

            # Validate phone number
            if not is_valid_phone(updated_phone_number):
                messagebox.showerror("Error", "Phone number must be 10 or 11 digits!")
                return

            # Validate email format
            if not is_valid_email(updated_email):
                messagebox.showerror("Error", "Invalid email address format!")
                return

            # Get tenantID from user_data
            tenant_id = self.user_data.get('tenantID')

            try:
                # Connect to database and update data
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tenants
                    SET username = ?, fullName = ?, phoneNumber = ?, ICNumber = ?, emailAddress = ?, profile_image = ?
                    WHERE tenantID = ?
                """, (updated_username, updated_fullname, updated_phone_number, updated_ic_number, 
                      updated_email, profile_image_path, tenant_id))
                conn.commit()
                conn.close()

                # Update user_data with new values
                self.user_data.update({
                    'tenantID': tenant_id,
                    'username': updated_username,
                    'fullName': updated_fullname,
                    'phoneNumber': updated_phone_number,
                    'ICNumber': updated_ic_number,
                    'emailAddress': updated_email,
                    'profile_image': profile_image_path
                })

                # Update the display immediately after saving
                self.display_profile_image()
                
                # Show success message box
                messagebox.showinfo("Success", "Profile successfully updated!")
                
                # Schedule return to main window after showing message
                profile_window.destroy()
                self.master.deiconify()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {str(e)}")

        def go_back():
            # Refresh the profile image before showing main window
            self.display_profile_image()
            profile_window.destroy()
            self.master.deiconify()

        # Back button - moved to top left corner
        back_button = CTkButton(master=scrollable_frame, text="Back", 
                              font=("Arial", 24), text_color="black",
                              fg_color="#c2b8ae", hover_color="#c89ef2", 
                              corner_radius=20, width=100, height=50,  # Made wider to fit text
                              command=go_back)
        back_button.place(x=20, y=20)  # Positioned at top left corner

        # Form fields setup (same as before)
        update_header = CTkLabel(master=scrollable_frame, text="Update Profile", 
                               font=("Arial", 56, "bold"), text_color="#000000")
        update_header.place(x=900, y=70)

        # Username field
        username_label = CTkLabel(master=scrollable_frame, text="Username", 
                                font=("Arial", 20), text_color="#666666")
        username_label.place(x=900, y=200)
        username_entry = CTkEntry(master=scrollable_frame, width=800, height=60, 
                                font=("Arial", 20), corner_radius=20,
                                border_color="#CCCCCC", fg_color="white", text_color="#000000")
        username_entry.insert(0, username)
        username_entry.place(x=900, y=240)

        # Fullname field
        fullname_label = CTkLabel(master=scrollable_frame, text="Fullname", 
                                font=("Arial", 20), text_color="#666666")
        fullname_label.place(x=900, y=310)
        fullname_entry = CTkEntry(master=scrollable_frame, width=800, height=60, 
                                font=("Arial", 20), corner_radius=20,
                                border_color="#CCCCCC", fg_color="white", text_color="#000000")
        fullname_entry.insert(0, fullname)
        fullname_entry.place(x=900, y=340)

        # Phone number field
        phone_label = CTkLabel(master=scrollable_frame, text="Phone Number", 
                              font=("Arial", 20), text_color="#666666")
        phone_label.place(x=900, y=420)
        phone_entry = CTkEntry(master=scrollable_frame, width=800, height=60, 
                              font=("Arial", 20), corner_radius=20,
                              border_color="#CCCCCC", fg_color="white", text_color="#000000")
        phone_entry.insert(0, phone_number)
        phone_entry.place(x=900, y=450)

        # IC number field
        ic_label = CTkLabel(master=scrollable_frame, text="IC Number", 
                           font=("Arial", 20), text_color="#666666")
        ic_label.place(x=900, y=520)
        ic_entry = CTkEntry(master=scrollable_frame, width=800, height=60, 
                           font=("Arial", 20), corner_radius=20,
                           border_color="#CCCCCC", fg_color="white", text_color="#000000")
        ic_entry.insert(0, ic_number)
        ic_entry.place(x=900, y=550)

        # Email field
        email_label = CTkLabel(master=scrollable_frame, text="Email Address", 
                              font=("Arial", 20), text_color="#666666")
        email_label.place(x=900, y=620)
        email_entry = CTkEntry(master=scrollable_frame, width=800, height=60, 
                              font=("Arial", 20), corner_radius=20,
                              border_color="#CCCCCC", fg_color="white", text_color="#000000")
        email_entry.insert(0, email)
        email_entry.place(x=900, y=650)

        # Profile image change option
        change_image_label = CTkLabel(scrollable_frame, text="Change Profile Image", 
                                    font=("Arial", 24, "underline"),
                                    text_color="black", fg_color="#f4f1e9")
        change_image_label.place(x=290, y=380)
        change_image_label.bind("<Button-1>", lambda e: change_profile_image())
        change_image_label.configure(cursor="hand2")

        # Save button
        save_button = CTkButton(master=scrollable_frame, text="Save Changes", 
                              font=("Arial", 28), text_color="black",
                              fg_color="#c2b8ae", hover_color="#c89ef2", 
                              corner_radius=20, width=800, height=60,
                              command=save_profile_updates)
        save_button.place(x=900, y=950)

    def open_my_stall(self):
        try:
            # Connect to database
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()
            
            # First check for active rental (isApprove = 1)
            cursor.execute("""
                SELECT rentalID 
                FROM rental 
                WHERE tenantID = ? AND isApprove = 1
                ORDER BY rentalID DESC LIMIT 1
            """, (self.user_data.get('tenantID'),))
            
            active_rental = cursor.fetchone()
            
            if active_rental:
                rental_id = active_rental[0]
                
                # Hide the dashboard immediately
                self.master.withdraw()
                
                # Create loading screen
                loading_screen = LoadingScreen(self.master)
                
                def launch_mystall():
                    try:
                        # Create a pipe for communication
                        import tempfile
                        temp_dir = tempfile.gettempdir()
                        pipe_path = os.path.join(temp_dir, f'mystall_pipe_{rental_id}')
                        
                        if not os.path.exists(pipe_path):
                            with open(pipe_path, 'w') as f:
                                f.write('')
                        
                        # Launch mystall window
                        process = subprocess.Popen(
                            [sys.executable, 'mystall20241019.py', str(rental_id), pipe_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        
                        def check_mystall_ready():
                            try:
                                if not os.path.exists(pipe_path):
                                    loading_screen.destroy()
                                else:
                                    self.master.after(100, check_mystall_ready)
                            except Exception as e:
                                print(f"Error checking mystall status: {e}")
                                loading_screen.destroy()
                                self.master.deiconify()
                                self.master.lift()
                                self.master.focus_force()
                        
                        check_mystall_ready()
                        
                        def check_process():
                            try:
                                # Check if process has ended
                                if process.poll() is not None:
                                    # Clean up pipe file if it exists
                                    if os.path.exists(pipe_path):
                                        os.remove(pipe_path)
                                    
                                    # Show and focus the dashboard window
                                    self.master.after(100, lambda: [
                                        self.master.deiconify(),
                                        self.master.lift(),
                                        self.master.focus_force(),
                                        self.master.attributes('-topmost', True),
                                        self.master.after(100, lambda: self.master.attributes('-topmost', False))
                                    ])
                                else:
                                    # Continue checking
                                    self.master.after(100, check_process)
                            except Exception as e:
                                print(f"Error in check_process: {e}")
                                self.master.deiconify()
                                self.master.lift()
                                self.master.focus_force()
                
                        # Start monitoring the process
                        check_process()
                        
                    except Exception as e:
                        loading_screen.destroy()
                        messagebox.showerror("Error", f"Failed to launch My Stall: {str(e)}")
                        self.master.deiconify()
                        self.master.lift()
                        self.master.focus_force()
                
                # Start the launch process in a separate thread
                threading.Thread(target=launch_mystall, daemon=True).start()
                
            else:
                # Check for pending rental (isApprove = 0 or isApprove = -1)
                cursor.execute("""
                    SELECT isApprove 
                    FROM rental 
                    WHERE tenantID = ? AND (isApprove = 0 OR isApprove = -1)
                    ORDER BY rentalID DESC LIMIT 1
                """, (self.user_data.get('tenantID'),))
                
                pending_rental = cursor.fetchone()
                
                if pending_rental:
                    # Determine the type of pending rental
                    status = "new application" if pending_rental[0] == 0 else "renewal"
                    messagebox.showinfo(
                        "Pending Rental",
                        f"You have a pending {status} that is waiting for admin approval. "
                        "Please wait for the admin to review your application."
                    )
                else:
                    messagebox.showinfo(
                        "No Rental",
                        "You don't have any active or pending rental. "
                        "Please apply for a stall first using the View Stall option."
                    )
            
            conn.close()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.master.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.master.deiconify()

    def open_view_stall(self):
        try:
            # Connect to database
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()
            
            # Check if tenant has any approved or pending rentals
            cursor.execute("""
                SELECT rentalID 
                FROM rental 
                WHERE tenantID = ? AND (isApprove = 1 OR isApprove = 0)
            """, (self.user_data['tenantID'],))
            
            existing_rental = cursor.fetchone()
            conn.close()
            
            if existing_rental:
                messagebox.showwarning(
                    "Cannot Apply", 
                    "You already have an active or pending rental application. You cannot apply for another stall."
                )
            else:
                # Hide the dashboard
                self.master.withdraw()
                
                # Launch the view stall window with tenant ID
                process = subprocess.Popen([
                    sys.executable, 
                    'tenantviewstall20241006.py', 
                    '--tenant_id',
                    str(self.user_data['tenantID'])
                ])
                
                # Monitor the process
                def check_process():
                    if process.poll() is not None:
                        # View stall window closed, show dashboard again
                        self.master.deiconify()
                        self.master.lift()
                        self.master.focus_force()
                    else:
                        # Check again in 100ms
                        self.master.after(100, check_process)
                
                # Start monitoring
                check_process()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.master.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.master.deiconify()

    def open_payment_window(self):
        try:
            # Connect to database
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()
            
            # Get tenant's rental IDs
            cursor.execute("""
                SELECT rentalID 
                FROM rental 
                WHERE tenantID = ? AND isApprove = 1
                ORDER BY rentalID DESC LIMIT 1
            """, (self.user_data.get('tenantID'),))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                rental_id = result[0]
                
                # Hide the dashboard immediately
                self.master.withdraw()
                
                # Create loading screen with payment style
                loading_screen = LoadingScreen(self.master, loading_type="payment")
                
                def launch_payment():
                    try:
                        # Create a pipe for communication
                        import tempfile
                        temp_dir = tempfile.gettempdir()
                        pipe_path = os.path.join(temp_dir, f'payment_pipe_{rental_id}')
                        
                        if not os.path.exists(pipe_path):
                            with open(pipe_path, 'w') as f:
                                f.write('')
                        
                        # Store user data in a temporary file
                        with open('temp_user_data.txt', 'w') as f:
                            f.write(str(self.user_data))
                        
                        # Launch payment window
                        process = subprocess.Popen(
                            [sys.executable, 'User_Payment_Total_Final.py', '--rental_id', str(rental_id), pipe_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        
                        def check_payment_ready():
                            try:
                                # Check if the pipe file has been deleted (indicating payment window is ready)
                                if not os.path.exists(pipe_path):
                                    # Payment window is ready, close loading screen
                                    loading_screen.destroy()
                                else:
                                    # Check again in 100ms
                                    self.master.after(100, check_payment_ready)
                            except Exception as e:
                                print(f"Error checking payment status: {e}")
                                loading_screen.destroy()
                                self.master.deiconify()
                        
                        # Start checking for payment window readiness
                        check_payment_ready()
                        
                        # Monitor payment process
                        def check_process():
                            if process.poll() is not None:
                                # Payment window closed, show dashboard again
                                if os.path.exists(pipe_path):
                                    os.remove(pipe_path)
                                self.master.deiconify()
                                self.master.lift()
                                self.master.focus_force()
                                self.master.attributes('-topmost', True)
                                self.master.attributes('-topmost', False)
                            else:
                                # Check again in 100ms
                                self.master.after(100, check_process)
                        
                        # Start monitoring
                        check_process()
                        
                    except Exception as e:
                        loading_screen.destroy()
                        messagebox.showerror("Error", f"Failed to launch Payment: {str(e)}")
                        self.master.deiconify()
                
                # Launch payment in a separate thread
                threading.Thread(target=launch_payment, daemon=True).start()
                
            else:
                messagebox.showinfo("No Stall", "You don't have any active stall rental.")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


class LoadingScreen:
    def __init__(self, parent, loading_type="default"):
        self.window = CTkToplevel(parent)
        self.window.attributes("-fullscreen", True)
        self.window.title("Loading")
        
        # Configure the window with mystall theme colors
        if loading_type == "payment":
            bg_color = "#fffcf7"  # Very light beige background
            icon_color = "#654633"  # Brown for icon
            text_color = "#654633"  # Brown for text
            loading_text = "Processing Payment Request"
            progress_color = "#c2b8ae"  # Muted beige for progress bar
        else:  # default/mystall
            bg_color = "#fffcf7"  # Very light beige background
            icon_color = "#654633"  # Brown for icon
            text_color = "#654633"  # Brown for text
            loading_text = "Fetching stall information"
            progress_color = "#c2b8ae"  # Muted beige for progress bar
            
        self.window.configure(fg_color=bg_color)
        
        # Center frame for content
        self.center_frame = CTkFrame(self.window, fg_color=bg_color)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        if loading_type == "payment":
            # Payment loading animation (dollar sign spinning)
            self.loading_label = CTkLabel(
                self.center_frame,
                text="💰",  # Dollar bag emoji
                font=("Arial", 72),
                text_color=icon_color
            )
        else:
            # Default loading animation
            self.loading_label = CTkLabel(
                self.center_frame,
                text="🔄",  # Rotating arrow emoji
                font=("Arial", 48),
                text_color=icon_color
            )
        
        self.loading_label.pack(pady=20)
        
        # Loading text
        self.text_label = CTkLabel(
            self.center_frame,
            text=loading_text,
            font=("Arial", 24, "bold"),
            text_color=text_color
        )
        self.text_label.pack(pady=10)
        
        # Progress bar with theme colors
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar",
                      troughcolor=bg_color,
                      background=progress_color,
                      thickness=10)
            
        self.progress = ttk.Progressbar(
            self.center_frame,
            length=300,
            mode='indeterminate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=20)
        self.progress.start(15)
        
        # Start the loading animation
        self.dots = 0
        self.animate_dots()
        
        # Center the window
        self.window.update_idletasks()
        self.window.lift()
        self.window.focus_force()

    def animate_dots(self):
        if hasattr(self, 'text_label'):  # Check if text_label still exists
            dots = "." * (self.dots % 4)
            current_text = self.text_label.cget("text").split('.')[0]  # Get text without dots
            self.text_label.configure(text=f"{current_text}{dots}")
            self.dots += 1
            self.window.after(500, self.animate_dots)

    def destroy(self):
        if hasattr(self, 'progress'):
            self.progress.stop()
        self.window.destroy()


if __name__ == "__main__":
    import ast
    
    # Get user data from command line arguments
    if len(sys.argv) > 2 and sys.argv[1] == '--user_data':
        try:
            # Convert string representation of dict back to dict
            user_data = ast.literal_eval(sys.argv[2])
            
            app = CTk()
            dashboard = TenantDashboard(app, user_data)
            app.mainloop()
        except Exception as e:
            print(f"Error initializing dashboard: {e}")
    else:
        print("No user data provided")

