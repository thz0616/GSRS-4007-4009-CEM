from customtkinter import *
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import sqlite3
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sys
import subprocess
import psutil
import time

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.geometry("1920x1080")
root.title("Payment")
root.resizable(True, True)
root.attributes("-fullscreen", True)

# Connect to the SQLite database
db_path = "properties.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add a global variable for property_id
property_id = None

# Get current date for default values
current_month = datetime.now().month
current_year = datetime.now().year

# Navigation functions for month and year
def get_unpaid_periods():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        WITH RECURSIVE
        months AS (
            SELECT 
                r.rentalID,
                strftime('%Y-%m', r.startDate) as month_year,
                CASE 
                    WHEN date(r.endDate) > date('now') THEN date('now', 'start of month')
                    ELSE date(r.endDate, '-1 month', 'start of month')
                END as end_check_date
            FROM rental r
            WHERE r.rentalID = ? AND r.isApprove = 1
            
            UNION ALL
            
            SELECT 
                m.rentalID,
                strftime('%Y-%m', date(substr(m.month_year, 1, 4) || '-' || 
                        substr(m.month_year, 6, 2) || '-01', '+1 month')),
                m.end_check_date
            FROM months m
            WHERE date(substr(m.month_year, 1, 4) || '-' || 
                  substr(m.month_year, 6, 2) || '-01') < m.end_check_date
        )
        SELECT DISTINCT month_year
        FROM months m
        LEFT JOIN payment_records pr ON 
            pr.rentalID = m.rentalID AND 
            pr.payment_period = m.month_year
        WHERE pr.id IS NULL
        ORDER BY month_year;
        """

        cursor.execute(query, (property_id,))
        unpaid_months = cursor.fetchall()
        
        # Convert YYYY-MM format to MM/YYYY format
        formatted_periods = []
        for (month_year,) in unpaid_months:
            year, month = month_year.split('-')
            formatted_periods.append(f"{month}/{year}")
        
        return formatted_periods

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_next_month():
    unpaid_periods = get_unpaid_periods()
    if not unpaid_periods:
        return
        
    current = period_label.cget("text")
    try:
        current_idx = unpaid_periods.index(current)
        if current_idx < len(unpaid_periods) - 1:
            next_period = unpaid_periods[current_idx + 1]
            period_label.configure(text=next_period)
    except ValueError:
        if unpaid_periods:
            period_label.configure(text=unpaid_periods[0])

def get_previous_month():
    unpaid_periods = get_unpaid_periods()
    if not unpaid_periods:
        return
        
    current = period_label.cget("text")
    try:
        current_idx = unpaid_periods.index(current)
        if current_idx > 0:
            prev_period = unpaid_periods[current_idx - 1]
            period_label.configure(text=prev_period)
    except ValueError:
        if unpaid_periods:
            period_label.configure(text=unpaid_periods[-1])

# Move this function up, after the navigation functions (get_previous_month, get_next_month) 
# and before the show_frame function

def update_period_label():
    unpaid_periods = get_unpaid_periods()
    if unpaid_periods:
        period_label.configure(text=unpaid_periods[0])  # Set to first unpaid period
    else:
        period_label.configure(text="No unpaid periods")
        # Disable navigation buttons if there are no unpaid periods
        left_month_arrow.configure(state="disabled")
        right_month_arrow.configure(state="disabled")
        # Disable confirm payment button
        confirm_payment_button.configure(state="disabled")

# Modify the show_frame function to track the active frame
def show_frame(frame, payment_method=None):
    frame.tkraise()
    global active_payment_method
    if payment_method:
        active_payment_method = payment_method
        print(f"Switched to {active_payment_method} payment method")  # Debugging line


# Function to insert data into the database
def insert_payment_data():
    global property_id
    if not property_id:
        messagebox.showerror("Error", "Please enter a rental ID first")
        return

    # Get selected payment period from label
    selected_period = period_label.cget("text")
    try:
        month, year = selected_period.split('/')
        payment_period = f"{year}-{month}"  # Format: YYYY-MM
        
        # Get current date and time
        current_datetime = datetime.now()
        payment_date = current_datetime.strftime('%Y-%m-%d')
        payment_time = current_datetime.strftime('%H:%M:%S')
        
        if active_payment_method == "Card":
            name = name_entry.get()
            card_number = card_entry.get()
            expiry = expiry_entry.get()
            cvc = cvc_entry.get()

            if not all([name, card_number, expiry, cvc]):
                messagebox.showwarning("Warning", "Please fill in all credit card fields.")
                return

            cursor.execute('''
                INSERT INTO payment_records (rentalID, payment_method, cardholder_name, 
                                          card_number, expire_date, cvc, payment_period,
                                          payment_date, payment_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (property_id, "Card", name, card_number, expiry, cvc, payment_period,
                 payment_date, payment_time))

        elif active_payment_method == "Online Banking":
            if bank_image_path:
                cursor.execute('''
                    INSERT INTO payment_records (rentalID, payment_method, receipt, 
                                              payment_period, payment_date, payment_time) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (property_id, "Online Banking", bank_image_path, payment_period,
                     payment_date, payment_time))
            else:
                messagebox.showwarning("Warning", "Please upload a bank receipt image.")
                return

        elif active_payment_method == "TNG":
            if tng_image_path:
                cursor.execute('''
                    INSERT INTO payment_records (rentalID, payment_method, receipt, 
                                              payment_period, payment_date, payment_time) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (property_id, "TNG", tng_image_path, payment_period,
                     payment_date, payment_time))
            else:
                messagebox.showwarning("Warning", "Please upload a TNG receipt image.")
                return

        conn.commit()
        
        # Get the ID of the last inserted payment record
        payment_id = cursor.lastrowid
        
        # Import and call the receipt page
        from receipt_page import open_receipt_window
        
        # Close the payment window before opening receipt window
        root.withdraw()  # Hide the payment window
        
        # Open receipt window with callback to handle dashboard return
        open_receipt_window(root, property_id, payment_id, return_to_dashboard)
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def return_to_dashboard():
    try:
        # Read user data from temporary file
        if os.path.exists('temp_user_data.txt'):
            with open('temp_user_data.txt', 'r') as f:
                user_data = f.read()
            
            # Clean up the temporary file
            os.remove('temp_user_data.txt')
            
            # Close the payment window
            root.destroy()
            
            # Start the tenant dashboard with user data
            subprocess.Popen([
                sys.executable, 
                'tenant_dashboard.py',
                '--user_data',
                user_data
            ])
        else:
            print("Error: No user data file found")
            root.destroy()
            
    except Exception as e:
        print(f"Error returning to dashboard: {e}")
        root.destroy()

def set_background(app, image_path):
    image = Image.open(image_path)
    resized_image = image.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    canvas = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    canvas.image = bg_image

set_background(root, "Images/payment bakcground.jpg")

# Fonts (Adjusted sizes for better visibility)
font_header = ("Arial", 56, "bold")
font_subheader = ("Arial", 30, "bold")
font_label = ("Arial", 25)
font_input = ("Arial", 20)
font_button = ("Arial", 28)
font_signup = ("Arial", 24)

 # Add the header image to the bank_frame
main_image = Image.open("Images/main.png")
main_image = main_image.resize((1000, 50), Image.LANCZOS) # Resize if needed
main_ctk_image = CTkImage(light_image=main_image, size=(1000, 50))
main_image_label = CTkLabel(root, image=main_ctk_image, text="", fg_color="#fffcf7")
main_image_label.place(x=440, y=60)  # Adjust position as needed
main_image_label.image = main_ctk_image  # Keep a reference to avoid garbage collection

# Main payment frame (this will always stay visible)
payment_frame = CTkFrame(root, fg_color="white", width=1150, height=800, corner_radius=15, border_width=2, border_color="black")
payment_frame.place(x=60, y=200)
payment_header = CTkLabel(payment_frame, text="How would you like to pay?", font=font_subheader, text_color="black")
payment_header.place(x=50, y=60)

# Subframe for the sliding content (this part will change)
content_frame = CTkFrame(payment_frame, fg_color="white", width=1050, height=660)
content_frame.place(x=50, y=100)

# Declare global variables for the image paths
bank_image_path = None
tng_image_path = None


# Image Upload function
def upload_image_bank():
    global bank_image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
    if file_path:
        try:
            img = Image.open(file_path)
            img = img.resize((300, 300), Image.LANCZOS)
            ctk_image = CTkImage(light_image=img, size=(300, 300))
            bank_image_label.configure(image=ctk_image, text="")
            bank_image_label.image = ctk_image  # Prevent garbage collection
            bank_image_path = file_path  # Save the image path globally
        except Exception as e:
            print(f"Error loading image: {e}")


# Image Upload function for Touch n Go
def upload_image_tng():
    global tng_image_path  # Declare as global
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
    if file_path:
        try:
            img = Image.open(file_path)
            img = img.resize((300, 300), Image.LANCZOS)
            ctk_image = CTkImage(light_image=img, size=(300, 300))
            tng_image_label.configure(image=ctk_image, text="")
            tng_image_label.image = ctk_image  # Prevent garbage collection

            # Set the image path to the global variable
            tng_image_path = file_path
            print(f"TNG image uploaded: {tng_image_path}")  # Debugging line to check image path

        except Exception as e:
            print(f"Error loading image: {e}")


# Create subframes inside content_frame for different payment methods
credit_card_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)
bank_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)
touch_n_go_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)

for frame in (credit_card_frame, bank_frame, touch_n_go_frame):
    frame.place(x=0, y=0, relwidth=1, relheight=1)

# Add content to credit card frame
name_label = CTkLabel(credit_card_frame, text="Cardholder's Name *", font=font_label, text_color="black")
name_label.place(x=50, y=300)
name_entry = CTkEntry(credit_card_frame, width=950, height=50, font=font_input, corner_radius=20)
name_entry.place(x=50, y=350)

card_label = CTkLabel(credit_card_frame, text="Card Number *", font=font_label, text_color="black")
card_label.place(x=50, y=430)
card_entry = CTkEntry(credit_card_frame, width=950, height=50, font=font_input, corner_radius=20)
card_entry.place(x=50, y=480)

expiry_label = CTkLabel(credit_card_frame, text="Expire date *", font=font_label, text_color="black")
expiry_label.place(x=50, y=550)
expiry_entry = CTkEntry(credit_card_frame, width=450, height=50, font=font_input, corner_radius=20)
expiry_entry.place(x=50, y=600)

cvc_label = CTkLabel(credit_card_frame, text="CVC *", font=font_label, text_color="black")
cvc_label.place(x=550, y=550)
cvc_entry = CTkEntry(credit_card_frame, width=450, height=50, font=font_input, corner_radius=20)
cvc_entry.place(x=550, y=600)

# Add content to bank frame
upload_bank_image_btn = CTkButton(bank_frame, text="Upload Bank Image", text_color="black", width=200, height=50, fg_color="#c2b8ae", corner_radius=20,command=upload_image_bank)
upload_bank_image_btn.place(x=720, y=600)

# Image display area
bank_image_label = CTkLabel(bank_frame, text="No Image Uploaded", fg_color="lightgray", width=300, height=300)
bank_image_label.place(x=670, y=280)

# Add the bank acc image to the bank_frame
bank_acc_image = Image.open("Images/bank acc image.png")
bank_acc_image = bank_acc_image.resize((400, 400), Image.LANCZOS)  # Resize if needed
bank_acc_ctk_image = CTkImage(light_image=bank_acc_image, size=(400, 400))
bank_acc_image_label = CTkLabel(bank_frame, image=bank_acc_ctk_image, text="")
bank_acc_image_label.place(x=100, y=280)  # Adjust position as needed
bank_acc_image_label.image = bank_acc_ctk_image  # Keep a reference to avoid garbage collection

# Add content to touch n go frame
upload_touch_n_go_image_btn = CTkButton(touch_n_go_frame, text="Upload Touch n Go Image", text_color="black",width=200, height=50, fg_color="#c2b8ae",corner_radius=20, command=upload_image_tng)
upload_touch_n_go_image_btn.place(x=720, y=600)

# Image display area
tng_image_label = CTkLabel(touch_n_go_frame, text="No Image Uploaded", fg_color="lightgray", width=300, height=300)
tng_image_label.place(x=670, y=280)

# Add the tng image to the bank_frame
tng_acc_image = Image.open("Images/tng acc image.png")
tng_acc_image = tng_acc_image.resize((300, 400), Image.LANCZOS)  # Resize if needed
tng_acc_ctk_image = CTkImage(light_image=tng_acc_image, size=(300, 400))
tng_acc_image_label = CTkLabel(touch_n_go_frame, image=tng_acc_ctk_image, text="")
tng_acc_image_label.place(x=100, y=250)  # Adjust position as needed
tng_acc_image_label.image = tng_acc_ctk_image  # Keep a reference to avoid garbage collection

# Show default credit card frame initially
show_frame(credit_card_frame, "Card")

# Create the navigation buttons (placed outside of the payment_frame so they are always visible)
credit_card_image = CTkImage(light_image=Image.open("Images/credit card.png"), size=(300, 200))
bank_image = CTkImage(light_image=Image.open("Images/bank.png"), size=(300, 200))
touch_n_go_image = CTkImage(light_image=Image.open("Images/touch n go.png"), size=(300, 200))

credit_card_button = CTkButton(root, image=credit_card_image, text="", width=300, height=200, fg_color="white", hover_color="grey", command=lambda: show_frame(credit_card_frame, "Card"))
credit_card_button.place(x=120, y=330)

bank_button = CTkButton(root, image=bank_image, text="", width=300, height=200, fg_color="white", hover_color="grey", command=lambda: show_frame(bank_frame, "Online Banking"))
bank_button.place(x=490, y=330)

touch_n_go_button = CTkButton(root, image=touch_n_go_image, text="", width=300, height=200, fg_color="white", hover_color="grey", command=lambda: show_frame(touch_n_go_frame, "TNG"))
touch_n_go_button.place(x=850, y=330)


# Add this near the top of the file, after the database connection
def initialize_with_rental_id(rental_id):
    global property_id
    property_id = rental_id
    
    try:
        # Updated query to get fullName instead of username
        cursor.execute("""
            SELECT r.rentalID, r.stallName, r.stallPurpose, r.startDate, r.endDate, 
                   r.rentalAmount, r.startOperatingTime, r.endOperatingTime,
                   cp.addressLine1, cp.addressLine2, cp.postcode, cp.city, cp.state,
                   t.fullName
            FROM rental r
            JOIN combined_properties cp ON r.combined_properties_id = cp.id
            JOIN tenants t ON r.tenantID = t.tenantID
            WHERE r.rentalID = ?
        """, (rental_id,))
        
        rental_data = cursor.fetchone()
        
        if rental_data:
            (rental_id, stall_name, stall_purpose, start_date, end_date, 
             rental_amount, start_time, end_time, 
             address1, address2, postcode, city, state,
             tenant_name) = rental_data
            
            payment_details_text = f"Rental ID: {rental_id}\n"
            payment_details_text += f"Tenant Name: {tenant_name}\n"  # This will now show fullName
            payment_details_text += f"Stall Name: {stall_name}\n"
            payment_details_text += f"Monthly Rental: RM {rental_amount:.2f}\n\n"
            payment_details_text += f"Property Address:\n{address1}\n"
            if address2:
                payment_details_text += f"{address2}\n"
            payment_details_text += f"{postcode} {city}\n"
            payment_details_text += f"{state}"
            
            root.after(100, lambda: payment_details_label.configure(text=payment_details_text))
            root.after(100, lambda: amount_label.configure(text=f"Amount to Pay: RM {rental_amount:.2f}"))
            root.after(100, update_period_label)
        else:
            root.after(100, lambda: payment_details_label.configure(text="No rental found with this ID"))
            property_id = None
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Update the payment details frame and its contents using grid
payment_details_frame = CTkFrame(root, fg_color="white", width=600, height=800, corner_radius=15, border_width=2, border_color="black")
payment_details_frame.place(x=1240, y=200)
payment_details_frame.grid_propagate(False)  # Prevent frame from shrinking

# Configure grid columns and rows with weights
payment_details_frame.grid_columnconfigure(0, weight=1)
payment_details_frame.grid_columnconfigure(1, weight=1)
payment_details_frame.grid_columnconfigure(2, weight=1)
payment_details_frame.grid_columnconfigure(3, weight=1)
for i in range(10):  # Configure 10 rows with equal weight
    payment_details_frame.grid_rowconfigure(i, weight=1)

# Header (Title)
payment_header = CTkLabel(payment_details_frame, 
                        text="Payment Details", 
                        font=font_subheader, 
                        text_color="black")
payment_header.grid(row=0, column=0, columnspan=4, pady=(20, 10), sticky="w", padx=40)

# Payment details label (Content)
payment_details_label = CTkLabel(payment_details_frame, 
                               text="Loading payment details...", 
                               font=font_label, 
                               text_color="black", 
                               justify="left",
                               wraplength=500)
payment_details_label.grid(row=1, column=0, columnspan=4, pady=(10, 30), sticky="w", padx=40)

# Select Payment Period label
period_select_label = CTkLabel(payment_details_frame,
                             text="Select Payment Period:",
                             font=font_label,
                             text_color="black")
period_select_label.grid(row=2, column=0, columnspan=4, pady=(30, 10), sticky="w", padx=40)

# Navigation buttons frame
nav_frame = CTkFrame(payment_details_frame, fg_color="transparent")
nav_frame.grid(row=3, column=0, columnspan=4, pady=10, padx=40)

# Month navigation buttons
left_month_arrow = CTkButton(nav_frame,
                           text="<",
                           text_color="black",
                           width=40,
                           height=40,
                           font=("Arial", 20),
                           fg_color="#c2b8ae",
                           hover_color="#a89e94",
                           corner_radius=10,
                           command=get_previous_month)
left_month_arrow.grid(row=0, column=0, padx=5)

# Period label
period_label = CTkLabel(nav_frame,
                       text="",  # Will be updated by update_period_label
                       font=("Arial", 24, "bold"),
                       text_color="black",
                       width=120,
                       height=40,
                       fg_color="white",
                       corner_radius=8)
period_label.grid(row=0, column=1, padx=20)

right_month_arrow = CTkButton(nav_frame,
                            text=">",
                            text_color="black",
                            width=40,
                            height=40,
                            font=("Arial", 20),
                            fg_color="#c2b8ae",
                            hover_color="#a89e94",
                            corner_radius=10,
                            command=get_next_month)
right_month_arrow.grid(row=0, column=2, padx=5)

# Amount label
amount_label = CTkLabel(payment_details_frame, 
                       text="Amount to Pay: RM 0.00", 
                       font=font_subheader, 
                       text_color="black")
amount_label.grid(row=4, column=0, columnspan=4, pady=(30, 10), sticky="w", padx=40)

# Confirm payment button
confirm_payment_button = CTkButton(payment_details_frame, 
                                 text="Confirm Payment", 
                                 text_color="black", 
                                 width=200, 
                                 height=50, 
                                 font=font_button, 
                                 fg_color="#c2b8ae", 
                                 hover_color="white", 
                                 corner_radius=20, 
                                 command=insert_payment_data)
confirm_payment_button.grid(row=5, column=0, columnspan=4, pady=(30, 0))

# Add this new function near the top of the file, after the database connection
def initialize_payment_window(parent_window, rental_id):
    global root
    root = parent_window
    
    # Initialize all your UI elements here
    # Move all your UI initialization code from the global scope into this function
    
    # Initialize with the provided rental ID
    initialize_with_rental_id(rental_id)

# Add this function near the other functions
def go_back():
    try:
        # First, try to find and kill any existing tenant_dashboard processes
        import psutil
        
        # Get the Python executable path
        python_executable = sys.executable.lower()
        
        # Find and terminate any existing tenant_dashboard processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1:
                    # Check if this is a Python process running tenant_dashboard.py
                    if (proc.info['cmdline'][0].lower() == python_executable and 
                        'tenant_dashboard.py' in ' '.join(proc.info['cmdline']).lower()):
                        # Kill the process
                        psutil.Process(proc.pid).terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Wait a brief moment to ensure processes are terminated
        time.sleep(0.5)
        
        # Close the payment window
        root.destroy()
        
        # Read user data from temporary file
        if os.path.exists('temp_user_data.txt'):
            with open('temp_user_data.txt', 'r') as f:
                user_data = f.read()
            
            # Clean up the temporary file
            os.remove('temp_user_data.txt')
            
            # Start the tenant dashboard with user data
            subprocess.Popen([
                sys.executable, 
                'tenant_dashboard.py',
                '--user_data',
                user_data
            ])
        else:
            print("Error: No user data file found")
            
    except Exception as e:
        print(f"Error returning to dashboard: {e}")
        # If there's an error, ensure the payment window is closed
        if 'root' in globals():
            root.destroy()

# Add this after setting up the root window and before other UI elements
# Back Button
back_button = CTkButton(
    root,
    text="Back",
    font=("Arial", 18, "bold"),
    text_color="black",
    fg_color="#c2b8ae",
    hover_color="#a89e94",
    corner_radius=10,
    width=100,
    height=40,
    command=go_back
)
back_button.place(x=20, y=20)  # Position in top left corner

# Update the main section
if __name__ == "__main__":
    try:
        # Check for rental ID argument
        if len(sys.argv) > 3 and sys.argv[1] == '--rental_id':
            rental_id = int(sys.argv[2])
            pipe_path = sys.argv[3]
            
            # Initialize with the provided rental ID
            initialize_with_rental_id(rental_id)
            
            # Configure window to be fullscreen and toplevel
            root.attributes("-fullscreen", True)
            root.lift()
            root.focus_force()
            
            def on_window_ready(event):
                root.unbind('<Map>')
                # Signal that the window is ready by deleting the pipe file
                if os.path.exists(pipe_path):
                    try:
                        os.remove(pipe_path)
                    except Exception as e:
                        print(f"Error removing pipe file: {e}")
            
            # Bind the Map event to detect when window is ready
            root.bind('<Map>', on_window_ready)
            
            # Configure window closing to use the same logic as the back button
            root.protocol("WM_DELETE_WINDOW", go_back)
            
            root.mainloop()
        else:
            print("Usage: script.py --rental_id <id> <pipe_path>")
            exit(1)
    except ValueError as e:
        print(f"Error with arguments: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
