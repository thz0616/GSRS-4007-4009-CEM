from customtkinter import *
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import sys
import re

# Set appearance mode
ctk.set_appearance_mode("Light")

def show_admin_update_profile(root, current_frame, show_dashboard_callback):
    # Hide current frame
    current_frame.pack_forget()
    
    # Create main update frame
    update_frame = CTkFrame(root, fg_color="#E6E6FA")
    update_frame.pack(fill="both", expand=True)
    
    # Back button
    back_btn = CTkButton(
        master=update_frame,
        text="← Back",
        command=lambda: [update_frame.pack_forget(), show_dashboard_callback()],
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)

    # Header
    header_label = CTkLabel(
        update_frame,
        text="Update Profile",
        font=("Arial", 40, "bold"),
        text_color="#4B0082"
    )
    header_label.pack(pady=(20, 40))

    # Define fonts
    font_label = ("Arial", 16)
    font_input = ("Arial", 14)
    font_button = ("Arial", 16)

    # Create a main container frame with padding and center alignment
    container = CTkFrame(update_frame, fg_color="transparent", width=1200)  # Increased from 1000
    container.pack(padx=150, pady=(0, 50), expand=True)
    container.pack_propagate(False)

    # Configure grid columns for centering
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=0)
    container.grid_columnconfigure(2, weight=1)

    # Username
    username_label = CTkLabel(container, text="Username", font=font_label, text_color="#666666")
    username_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
    
    username_entry = CTkEntry(container, width=700, height=45, font=font_input)  # Increased from 600x40
    username_entry.grid(row=1, column=1, pady=(0, 20))  # Increased pady from 15

    # Fullname
    fullname_label = CTkLabel(container, text="Fullname", font=font_label, text_color="#666666")
    fullname_label.grid(row=2, column=1, sticky="w", pady=(0, 5))
    
    fullname_entry = CTkEntry(container, width=700, height=45, font=font_input)
    fullname_entry.grid(row=3, column=1, pady=(0, 20))

    # Phone Number
    phone_label = CTkLabel(container, text="Phone Number", font=font_label, text_color="#666666")
    phone_label.grid(row=4, column=1, sticky="w", pady=(0, 5))
    
    phone_entry = CTkEntry(container, width=700, height=45, font=font_input)
    phone_entry.grid(row=5, column=1, pady=(0, 20))

    # IC Number
    ic_label = CTkLabel(container, text="IC Number", font=font_label, text_color="#666666")
    ic_label.grid(row=6, column=1, sticky="w", pady=(0, 5))
    
    ic_entry = CTkEntry(container, width=700, height=45, font=font_input)
    ic_entry.grid(row=7, column=1, pady=(0, 20))

    # Email
    email_label = CTkLabel(container, text="Email Address", font=font_label, text_color="#666666")
    email_label.grid(row=8, column=1, sticky="w", pady=(0, 5))
    
    email_entry = CTkEntry(container, width=700, height=45, font=font_input)
    email_entry.grid(row=9, column=1, pady=(0, 20))

    # Current Password
    current_password_label = CTkLabel(container, text="Current Password *", font=font_label, text_color="#666666")
    current_password_label.grid(row=10, column=1, sticky="w", pady=(0, 5))
    
    current_password_entry = CTkEntry(
        container, width=700, height=45, font=font_input, 
        show="*", placeholder_text="Enter your current password"
    )
    current_password_entry.grid(row=11, column=1, pady=(0, 20))

    # New Password
    password_label = CTkLabel(container, text="New Password", font=font_label, text_color="#666666")
    password_label.grid(row=12, column=1, sticky="w", pady=(0, 5))
    
    password_entry = CTkEntry(
        container, width=700, height=45, font=font_input,
        show="*", placeholder_text="Enter new password (leave blank if no change)"
    )
    password_entry.grid(row=13, column=1, pady=(0, 20))

    # Confirm Password
    confirm_password_label = CTkLabel(container, text="Confirm New Password", font=font_label, text_color="#666666")
    confirm_password_label.grid(row=14, column=1, sticky="w", pady=(0, 5))
    
    confirm_password_entry = CTkEntry(
        container, width=700, height=45, font=font_input,
        show="*", placeholder_text="Confirm new password"
    )
    confirm_password_entry.grid(row=15, column=1, pady=(0, 20))

    def get_admin_data(admin_id):
        """Retrieve admin data from database"""
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, phone_number, fullname, ic_number, email, password 
                FROM admin 
                WHERE id = ?
            """, (admin_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'username': result[0],
                    'phone': result[1],
                    'fullname': result[2],
                    'ic': result[3],
                    'email': result[4],
                    'password': result[5]
                }
            return None
        except Exception as e:
            print(f"Error getting admin data: {e}")
            return None
        finally:
            if conn:
                conn.close()

    # Add validation functions
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

    def check_duplicate(field, value, admin_id):
        """Check if value already exists for other admins"""
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM admin WHERE {field} = ? AND id != ?", (value, admin_id))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking duplicate {field}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_profile(admin_id):
        if not current_password_entry.get():
            messagebox.showerror("Error", "Please enter your current password!")
            return

        # Get all entry values
        username = username_entry.get().strip()
        phone = phone_entry.get().strip()
        fullname = fullname_entry.get().strip()
        ic = ic_entry.get().strip()
        email = email_entry.get().strip()
        new_password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        # Check for empty fields
        if not all([username, phone, fullname, ic, email]):
            messagebox.showerror("Error", "All fields except new password are required!")
            return

        # Validate phone number format
        if not is_valid_phone(phone):
            messagebox.showerror("Error", "Phone number must be 10 or 11 digits!")
            return

        # Validate email format
        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email address format!")
            return

        # Check for duplicates
        if check_duplicate("username", username, admin_id):
            messagebox.showerror("Error", "Username already exists!")
            return
        if check_duplicate("ic_number", ic, admin_id):
            messagebox.showerror("Error", "IC number already exists!")
            return
        if check_duplicate("email", email, admin_id):
            messagebox.showerror("Error", "Email already exists!")
            return

        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute("SELECT password FROM admin WHERE id = ?", (admin_id,))
            stored_password = cursor.fetchone()[0]
            
            if current_password_entry.get() != stored_password:
                messagebox.showerror("Error", "Current password is incorrect!")
                return

            # Check if new password and confirm password match
            if new_password and new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match!")
                return

            # Update profile
            update_password = new_password if new_password else stored_password
            cursor.execute("""
                UPDATE admin 
                SET username=?, phone_number=?, fullname=?, ic_number=?, email=?, password=?
                WHERE id=?
            """, (
                username,
                phone,
                fullname,
                ic,
                email,
                update_password,
                admin_id
            ))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            
            # Switch back to dashboard after successful update
            update_frame.pack_forget()
            show_dashboard_callback()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()

    # Update Button
    update_button = CTkButton(
        container,
        text="Update Profile",
        command=lambda: update_profile(admin_id),
        width=700,  # Match entry width
        height=50,  # Increased from 45
        font=font_button,
        fg_color="#d0a9f5",
        hover_color="#c89ef2"
    )
    update_button.grid(row=16, column=1, pady=(25, 0))  # Increased top padding

    # Get admin ID from command line arguments
    admin_id = None
    if len(sys.argv) > 1:
        admin_id = sys.argv[1]

    # Get admin data and populate fields
    if admin_id:
        admin_data = get_admin_data(admin_id)
        if admin_data:
            username_entry.insert(0, admin_data['username'])
            fullname_entry.insert(0, admin_data['fullname'])
            phone_entry.insert(0, admin_data['phone'])
            ic_entry.insert(0, admin_data['ic'])
            email_entry.insert(0, admin_data['email'])

if __name__ == "__main__":
    app = CTk()
    app.mainloop()
