import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
import os
import datetime
import tkinter as tk
from tkinter import ttk
import sys

# Initialize CustomTkinter appearance
ctk.set_appearance_mode("Light")  # Changed from "System" to "Light"
ctk.set_default_color_theme("blue")  # Options: "blue" (default), "green", "dark-blue"

# Initialize tenant_info and stall_info
tenant_info = {}
stall_info = {}

# Global variable to store rental application data
rental_application_data = {}

# Connect to the SQLite database
db_path = "properties.db"

# Add this function near the top of the file, after the db_path definition but before the initial connection

def create_db_connection():
    """Create and return a new database connection"""
    try:
        connection = sqlite3.connect(db_path)
        # Enable foreign keys
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
        return None

# Check if the database file exists
if not os.path.exists(db_path):
    messagebox.showerror("Database Error", f"The database file '{db_path}' does not exist.")
    exit()

# Add this function after create_db_connection but before the initial connection code

def ensure_db_connection():
    """Ensure database connection is active, reconnect if necessary"""
    global conn, cursor
    try:
        # Test the connection
        cursor.execute("SELECT 1")
    except (sqlite3.Error, AttributeError):
        # Connection is closed or invalid, create new connection
        conn = create_db_connection()
        if conn:
            cursor = conn.cursor()
        else:
            messagebox.showerror("Database Error", "Failed to reconnect to database")
            return False
    return True

# Create a global connection and cursor
conn = create_db_connection()
if not conn:
    exit()
cursor = conn.cursor()

# We don't need to create the rentals table anymore, as it's already defined in the database

# Define the ToolTip class before using it
class ToolTip:
    def __init__(self, widget, text='widget info'):
        self.waittime = 500  # milliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event=None):
        x = y = 0
        # Calculate position relative to the widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        # Create a toplevel window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # Remove window decorations
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            wraplength=self.wraplength
        )
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None


# Define event handlers before using them
def on_start_date_change(event):
    selected_start_date = start_date_entry.get_date()
    end_date_entry.config(mindate=selected_start_date)
    current_end_date = end_date_entry.get_date()
    if current_end_date < selected_start_date:
        end_date_entry.set_date(selected_start_date)


def on_end_date_change(event):
    selected_end_date = end_date_entry.get_date()
    start_date_entry.config(maxdate=selected_end_date)
    current_start_date = start_date_entry.get_date()
    if current_start_date > selected_end_date:
        start_date_entry.set_date(selected_end_date)


# Initialize the main window
root = ctk.CTk()
root.title("Government Stall Rental System")
root.geometry("1920x1080")
root.attributes("-fullscreen", True)  # Make window fullscreen

# Create a back button frame at the top
back_button_frame = ctk.CTkFrame(root, fg_color="#E8DCD0", height=50)
back_button_frame.grid(row=0, column=0, sticky="ew", columnspan=2)
back_button_frame.grid_propagate(False)

# Add back button
back_button = ctk.CTkButton(
    back_button_frame,
    text="Back",
    font=("Arial", 18, "bold"),
    width=150,
    height=40,
    fg_color="#A29086",  # Gray color
    hover_color="#8B7355",  # Darker gray for hover
    text_color="white",
    command=root.destroy
)
back_button.place(x=20, y=5)  # Position at top left

# Update the container frame grid position to account for back button
container = ctk.CTkFrame(master=root)
container.grid(row=1, column=0, sticky="nsew")  # Changed from row=0 to row=1
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Configure root grid weights
root.grid_rowconfigure(0, weight=0)  # Back button frame
root.grid_rowconfigure(1, weight=1)  # Container frame
root.grid_columnconfigure(0, weight=1)

# Set plain background color
container.configure(fg_color="#E8DCD0")  # Light beige background

# Dictionary to hold all pages
pages = {}

# Get tenant_id and stall_id from command line arguments and initialize pages
if len(sys.argv) > 2:
    current_tenant_id = int(sys.argv[1])
    current_stall_id = int(sys.argv[2])
    
    # Connect to database and get tenant and stall information
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get tenant information
    cursor.execute("SELECT fullName, ICNumber FROM tenants WHERE tenantID = ?", (current_tenant_id,))
    tenant_result = cursor.fetchone()
    if tenant_result:
        tenant_info['name'] = tenant_result[0]
        tenant_info['ic_number'] = tenant_result[1]
    
    # Get stall information
    cursor.execute("""
        SELECT addressLine1, addressLine2, postcode, city, state, sqft, price 
        FROM combined_properties 
        WHERE id = ?
    """, (current_stall_id,))
    stall_result = cursor.fetchone()
    if stall_result:
        stall_info['location'] = f"{stall_result[0]}, {stall_result[1]}, {stall_result[2]} {stall_result[3]}, {stall_result[4]}"
        stall_info['stall_size'] = stall_result[5]
        stall_info['rental_fee'] = stall_result[6]
    
    conn.close()

    # Remove Page 1 from pages dictionary
    if "Page1" in pages:
        del pages["Page1"]
    
    # After all pages are created, show Page 2
    root.after(100, lambda: [pages["Page2"].tkraise(), update_page2_info()])


######################
# Function to create a header
######################
def create_header(master, text):
    header_frame = ctk.CTkFrame(master=master, fg_color="transparent")
    header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(20, 10))
    header_frame.grid_columnconfigure(0, weight=1)

    title_label = ctk.CTkLabel(master=header_frame, text=text,
                               font=("Arial", 40, "bold"), text_color="#8B4513")  # Changed to brown
    title_label.grid(row=0, column=0, padx=20, pady=10, sticky='ew')


######################
# Page 1: Tenant & Stall ID Entry
######################
def show_page2():
    global conn, cursor
    
    # Ensure database connection is active
    if not ensure_db_connection():
        return
        
    tenant_id = tenant_id_entry.get()
    stall_id = stall_id_entry.get()

    # Input validation
    if not tenant_id.isdigit() or not stall_id.isdigit():
        status_label.configure(text="Tenant ID and Stall ID must be numeric.", text_color="red")
        return

    tenant_id_int = int(tenant_id)
    stall_id_int = int(stall_id)

    # Verify tenantID exists
    cursor.execute("SELECT * FROM tenants WHERE tenantID = ?", (tenant_id_int,))
    tenant = cursor.fetchone()
    if not tenant:
        status_label.configure(text=f"No tenant found with Tenant ID: {tenant_id_int}", text_color="red")
        return

    # Verify stallID exists
    cursor.execute("SELECT * FROM combined_properties WHERE id = ?", (stall_id_int,))
    stall = cursor.fetchone()
    if not stall:
        status_label.configure(text=f"No stall found with Stall ID: {stall_id_int}", text_color="red")
        return

    # Clear status label
    status_label.configure(text="")

    # Store tenantID and stallID for later use
    global current_tenant_id, current_stall_id, tenant_info, stall_info
    current_tenant_id = tenant_id_int
    current_stall_id = stall_id_int

    # Retrieve tenant and stall information
    tenant_info = {
        'name': tenant[2],        # Assuming fullName is at index 2
        'ic_number': tenant[3]    # Assuming ICNumber is at index 3
    }
    stall_info = {
        'location': f"{stall[4]}, {stall[5]}, {stall[6]} {stall[7]}, {stall[8]}",  # addressLine1, addressLine2, postcode, city, state
        'rental_fee': stall[10],  # price in RM
        'stall_size': stall[9]    # sqft
    }

    # If validations pass, show page2 and update information
    pages["Page2"].tkraise()
    update_page2_info()


# Widgets for Page 1
page1 = ctk.CTkFrame(master=container, fg_color="transparent")
pages["Page1"] = page1

# Use grid to manage the page layout
page1.grid(row=0, column=0, sticky='nsew')
page1.grid_rowconfigure(1, weight=1)
page1.grid_columnconfigure(0, weight=1)

# Create header
create_header(page1, "Government Stall Rental Application")

# Form Frame
form_frame = ctk.CTkFrame(master=page1, fg_color="#FFFFFF", corner_radius=10)
form_frame.grid(row=1, column=0, padx=200, pady=50, sticky='nsew')

form_frame.grid_rowconfigure(0, weight=1)
form_frame.grid_rowconfigure(1, weight=1)
form_frame.grid_columnconfigure(1, weight=1)

# Tenant ID
tenant_id_label = ctk.CTkLabel(master=form_frame, text="Tenant ID:",
                               font=("Arial", 32), text_color="#4B0082")
tenant_id_label.grid(row=0, column=0, padx=20, pady=20, sticky='e')
tenant_id_entry = ctk.CTkEntry(master=form_frame, font=("Arial", 28))
tenant_id_entry.grid(row=0, column=1, padx=20, pady=20, sticky='we')
ToolTip(tenant_id_entry, "Enter your unique Tenant ID.")

# Stall ID
stall_id_label = ctk.CTkLabel(master=form_frame, text="Stall ID:",
                              font=("Arial", 32), text_color="#4B0082")
stall_id_label.grid(row=1, column=0, padx=20, pady=20, sticky='e')
stall_id_entry = ctk.CTkEntry(master=form_frame, font=("Arial", 28))
stall_id_entry.grid(row=1, column=1, padx=20, pady=20, sticky='we')
ToolTip(stall_id_entry, "Enter the Stall ID you wish to rent.")

# Status Label
status_label = ctk.CTkLabel(master=page1, text="", font=("Arial", 24))
status_label.grid(row=2, column=0, pady=10)

# Next Button
next_button_page1 = ctk.CTkButton(master=page1, text="Next", command=show_page2,
                                  width=300, height=70, font=("Arial", 32),
                                  fg_color="#9370DB", hover_color="#8A2BE2", corner_radius=20)
next_button_page1.grid(row=3, column=0, pady=40)
ToolTip(next_button_page1, "Proceed to the rental application form.")


######################
# Page 2: Rental Application Form
######################
def on_purpose_option_change(choice):
    if choice == "Other":
        please_specify_label.grid()  # Show the label
        purpose_entry.grid()  # Show the entry field
    else:
        please_specify_label.grid_remove()  # Hide the label
        purpose_entry.grid_remove()  # Hide the entry field
        purpose_entry.delete(0, ctk.END)  # Clear the entry field


def proceed_to_next():
    # Gather all input data
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()

    # Convert dates to strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    stall_purpose = purpose_var.get()
    if stall_purpose == "Other":
        stall_purpose = purpose_entry.get()
        if not stall_purpose.strip():
            status_label_page2.configure(text="Please specify the stall purpose.", text_color="red")
            return
    stall_name = stall_name_entry.get()

    # Get operating times
    start_operating_time = f"{start_hour_var.get():02}:{start_minute_var.get():02}"
    end_operating_time = f"{end_hour_var.get():02}:{end_minute_var.get():02}"

    # Validate times
    try:
        start_op_time_obj = datetime.datetime.strptime(start_operating_time, "%H:%M")
        end_op_time_obj = datetime.datetime.strptime(end_operating_time, "%H:%M")
        if start_op_time_obj >= end_op_time_obj:
            status_label_page2.configure(text="Start operating time must be before end operating time.",
                                         text_color="red")
            return
    except ValueError:
        status_label_page2.configure(text="Invalid operating time entered.", text_color="red")
        return

    # Validate dates
    if start_date > end_date:
        status_label_page2.configure(text="Start Date cannot be after End Date.", text_color="red")
        return

    # Validate stall name
    if not stall_name.strip():
        status_label_page2.configure(text="Please enter the stall name.", text_color="red")
        return

    # Store the data in rental_application_data
    global rental_application_data
    rental_application_data = {
        'tenantID': current_tenant_id,
        'stallID': current_stall_id,
        'startDate': start_date_str,
        'endDate': end_date_str,
        'stallPurpose': stall_purpose,
        'stallName': stall_name,
        'startOperatingTime': start_operating_time,
        'endOperatingTime': end_operating_time
    }

    # Clear status label
    status_label_page2.configure(text="")

    # Proceed to Page 3
    show_page3()


# Widgets for Page 2
page2 = ctk.CTkFrame(master=container, fg_color="transparent")
pages["Page2"] = page2

# Use grid to manage the page layout
page2.grid(row=0, column=0, sticky='nsew')
page2.grid_rowconfigure(1, weight=1)
page2.grid_columnconfigure(0, weight=1)

# Create header
create_header(page2, "Rental Application Form")

# Form Frame
form_frame_page2 = ctk.CTkFrame(master=page2, fg_color="#F2E6DB", corner_radius=10)  # Lighter beige for form
form_frame_page2.grid(row=1, column=0, padx=200, pady=30, sticky='nsew')

# Configure row weights to give more space
for i in range(10):  # Increased from 9 to 10 to accommodate the new row
    form_frame_page2.grid_rowconfigure(i, weight=1)
form_frame_page2.grid_columnconfigure(1, weight=1)

# Display Tenant Information
tenant_name_label = ctk.CTkLabel(master=form_frame_page2, text="Tenant Name:",
                                 font=("Arial", 28), text_color="#8B4513")  # Saddle brown for labels
tenant_name_label.grid(row=0, column=0, padx=20, pady=20, sticky='e')
tenant_name_value = ctk.CTkLabel(master=form_frame_page2, text="",
                                 font=("Arial", 28))
tenant_name_value.grid(row=0, column=1, padx=20, pady=20, sticky='w')

ic_number_label = ctk.CTkLabel(master=form_frame_page2, text="IC Number:",
                               font=("Arial", 28), text_color="#8B4513")
ic_number_label.grid(row=1, column=0, padx=20, pady=20, sticky='e')
ic_number_value = ctk.CTkLabel(master=form_frame_page2, text="",
                               font=("Arial", 28))
ic_number_value.grid(row=1, column=1, padx=20, pady=20, sticky='w')

# Display Stall Information
stall_location_label = ctk.CTkLabel(master=form_frame_page2, text="Stall Location:",
                                    font=("Arial", 28), text_color="#8B4513")
stall_location_label.grid(row=2, column=0, padx=20, pady=20, sticky='e')
stall_location_value = ctk.CTkLabel(master=form_frame_page2, text="",
                                    font=("Arial", 28), wraplength=1200, justify='left')
stall_location_value.grid(row=2, column=1, padx=20, pady=20, sticky='w')

rental_fee_label = ctk.CTkLabel(master=form_frame_page2, text="Rental Fee:",
                                font=("Arial", 28), text_color="#8B4513")
rental_fee_label.grid(row=3, column=0, padx=20, pady=20, sticky='e')
rental_fee_value = ctk.CTkLabel(master=form_frame_page2, text="",
                                font=("Arial", 28))
rental_fee_value.grid(row=3, column=1, padx=20, pady=20, sticky='w')

stall_size_label = ctk.CTkLabel(master=form_frame_page2, text="Stall Size:",
                                font=("Arial", 28), text_color="#8B4513")
stall_size_label.grid(row=4, column=0, padx=20, pady=20, sticky='e')
stall_size_value = ctk.CTkLabel(master=form_frame_page2, text="",
                                font=("Arial", 28))
stall_size_value.grid(row=4, column=1, padx=20, pady=20, sticky='w')

# Rental Period
rental_period_label = ctk.CTkLabel(master=form_frame_page2, text="Rental Period:",
                                   font=("Arial", 28), text_color="#8B4513")
rental_period_label.grid(row=5, column=0, padx=20, pady=20, sticky='e')

dates_frame = ctk.CTkFrame(master=form_frame_page2, fg_color="#FFFFFF")
dates_frame.grid(row=5, column=1, padx=20, pady=20, sticky='w')

today = datetime.date.today()

# Configure ttk styles for DateEntry to enhance disabled dates
style = ttk.Style()
style.theme_use('clam')  # Use 'clam' theme for better styling options

# Customize the disabled dates appearance
style.configure('TCalendar.Calendar', background='white', foreground='black', borderwidth=2, font=("Arial", 22))
style.map('TCalendar.Calendar',
          background=[('disabled', '#D3D3D3')],
          foreground=[('disabled', '#A9A9A9')])

start_date_entry = DateEntry(master=dates_frame, width=16, background='#9370DB',
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                             mindate=today, font=("Arial", 22), state="readonly")
start_date_entry.pack(side='left', padx=(0, 10))
start_date_entry.bind("<<DateEntrySelected>>", on_start_date_change)
ToolTip(start_date_entry, "Select the start date of the rental period.")

to_label = ctk.CTkLabel(master=dates_frame, text=" to ", font=("Arial", 24), text_color="black")
to_label.pack(side='left')

end_date_entry = DateEntry(master=dates_frame, width=16, background='#9370DB',
                           foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                           mindate=today, font=("Arial", 22), state="readonly")
end_date_entry.pack(side='left', padx=(10, 0))
end_date_entry.bind("<<DateEntrySelected>>", on_end_date_change)
ToolTip(end_date_entry, "Select the end date of the rental period.")

# Stall Purpose
purpose_label = ctk.CTkLabel(master=form_frame_page2, text="Stall Purpose:",
                             font=("Arial", 28), text_color="#8B4513")
purpose_label.grid(row=6, column=0, padx=20, pady=20, sticky='e')

purpose_var = ctk.StringVar(value="Food and Beverage")
purpose_options = [
    "Food and Beverage",
    "Clothing and Apparel",
    "Electronics",
    "Handicrafts",
    "Books and Stationery",
    "Health and Beauty",
    "Services (e.g., Repair, Tailoring)",
    "Agricultural Products",
    "Other"
]

# Create the purpose_menu first
purpose_menu = ctk.CTkComboBox(master=form_frame_page2, values=purpose_options, variable=purpose_var,
                               command=on_purpose_option_change, font=("Arial", 20),
                               fg_color="#F2E6DB", dropdown_fg_color="#F2E6DB",
                               text_color="#8B4513", button_color="#C4A484", button_hover_color="#8B4513",
                               width=500, state="readonly")  # Non-editable
purpose_menu.grid(row=6, column=1, padx=20, pady=(20, 10), sticky='we')  # Reduced bottom padding
ToolTip(purpose_menu, "Select the primary purpose of your stall.")

# Please Specify Label (Initially hidden)
please_specify_label = ctk.CTkLabel(master=form_frame_page2, text="Please Specify:",
                                    font=("Arial", 28), text_color="#8B4513")
please_specify_label.grid(row=7, column=0, padx=20, pady=(10, 10), sticky='e')  # Adjusted padding
please_specify_label.grid_remove()

# Stall Purpose - Other Entry (Initially hidden)
purpose_entry = ctk.CTkEntry(master=form_frame_page2, font=("Arial", 22),
                             placeholder_text="Enter your stall purpose", 
                             fg_color="#FFFFFF", border_color="#8B4513")
purpose_entry.grid(row=7, column=1, padx=20, pady=(10, 10), sticky='we')  # Adjusted padding
purpose_entry.grid_remove()

# Stall Name (adjusted padding)
stall_name_label = ctk.CTkLabel(master=form_frame_page2, text="Stall Name:",
                                font=("Arial", 28), text_color="#8B4513")
stall_name_label.grid(row=8, column=0, padx=20, pady=(20, 20), sticky='e')
stall_name_entry = ctk.CTkEntry(master=form_frame_page2, font=("Arial", 26))
stall_name_entry.grid(row=8, column=1, padx=20, pady=20, sticky='we')
ToolTip(stall_name_entry, "Enter the name of your stall.")

# Operating Hours Label
operating_hours_label = ctk.CTkLabel(master=form_frame_page2, text="Operating Hours:",
                                     font=("Arial", 28), text_color="#8B4513")
operating_hours_label.grid(row=9, column=0, padx=20, pady=20, sticky='e')

# Operating Hours Frame
operating_hours_frame = ctk.CTkFrame(master=form_frame_page2, fg_color="#F2E6DB")
operating_hours_frame.grid(row=9, column=1, padx=20, pady=20, sticky='w')

# Start Operating Time
start_time_label = ctk.CTkLabel(master=operating_hours_frame, text="From", font=("Arial", 24))
start_time_label.pack(side='left', padx=(0, 10))

start_hour_var = tk.StringVar(value="09")
start_minute_var = tk.StringVar(value="00")

start_hour_spinbox = ttk.Spinbox(operating_hours_frame, from_=0, to=23, wrap=True, textvariable=start_hour_var, width=3,
                                 font=("Arial", 22), format="%02.0f")
start_hour_spinbox.pack(side='left')
start_hour_spinbox.configure(state='readonly')

start_colon_label = ctk.CTkLabel(master=operating_hours_frame, text=":", font=("Arial", 24))
start_colon_label.pack(side='left')

start_minute_spinbox = ttk.Spinbox(operating_hours_frame, from_=0, to=59, wrap=True, textvariable=start_minute_var,
                                   width=3, font=("Arial", 22), format="%02.0f")
start_minute_spinbox.pack(side='left')
start_minute_spinbox.configure(state='readonly')

# End Operating Time
end_time_label = ctk.CTkLabel(master=operating_hours_frame, text=" to ", font=("Arial", 24))
end_time_label.pack(side='left', padx=(20, 10))

end_hour_var = tk.StringVar(value="17")
end_minute_var = tk.StringVar(value="00")

end_hour_spinbox = ttk.Spinbox(operating_hours_frame, from_=0, to=23, wrap=True, textvariable=end_hour_var, width=3,
                               font=("Arial", 22), format="%02.0f")
end_hour_spinbox.pack(side='left')
end_hour_spinbox.configure(state='readonly')

end_colon_label = ctk.CTkLabel(master=operating_hours_frame, text=":", font=("Arial", 24))
end_colon_label.pack(side='left')

end_minute_spinbox = ttk.Spinbox(operating_hours_frame, from_=0, to=59, wrap=True, textvariable=end_minute_var, width=3,
                                 font=("Arial", 22), format="%02.0f")
end_minute_spinbox.pack(side='left')
end_minute_spinbox.configure(state='readonly')

ToolTip(operating_hours_frame, "Select your stall's operating hours.")

# Status Label
status_label_page2 = ctk.CTkLabel(master=page2, text="", font=("Arial", 24))
status_label_page2.grid(row=2, column=0, pady=10)

# Next Button (Changed from Submit to Next)
next_button_page2 = ctk.CTkButton(master=page2, text="Next", command=proceed_to_next,
                                  width=300, height=70, font=("Arial", 32),
                                  fg_color="#C4A484",  # Light brown
                                  hover_color="#8B4513",  # Darker brown on hover
                                  corner_radius=20)
next_button_page2.grid(row=3, column=0, pady=40)
ToolTip(next_button_page2, "Proceed to the rental application agreement.")


# Function to update Page 2 information
def update_page2_info():
    tenant_name_value.configure(text=tenant_info.get('name', 'N/A'))
    ic_number_value.configure(text=tenant_info.get('ic_number', 'N/A'))
    stall_location_value.configure(text=stall_info.get('location', 'N/A'))
    rental_fee_value.configure(text=f"RM{stall_info.get('rental_fee', 0):.2f}")
    stall_size_value.configure(text=f"{stall_info.get('stall_size', 0)} sqft")


######################
# Page 3: Rental Application Agreement
######################
def show_page3():
    global conn, cursor
    
    # Ensure database connection is active
    if not ensure_db_connection():
        return
        
    # Retrieve the agreement text from the database
    try:
        cursor.execute("SELECT rental_agreement FROM systemInformation ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            agreement_text = result[0]
        else:
            agreement_text = "No agreement text found in the database."

        # Replace placeholders with actual data
        agreement_text = agreement_text.replace("##tenantName##", tenant_info.get('name', ''))
        agreement_text = agreement_text.replace("##tenantICNumber##", tenant_info.get('ic_number', ''))
        agreement_text = agreement_text.replace("##stallLocation##", stall_info.get('location', ''))
        agreement_text = agreement_text.replace("##stallSize##", str(stall_info.get('stall_size', '')))
        agreement_text = agreement_text.replace("##stallRentalFee##", f"RM{stall_info.get('rental_fee', 0):.2f}")
        agreement_text = agreement_text.replace("##startDate##", rental_application_data.get('startDate', ''))
        agreement_text = agreement_text.replace("##endDate##", rental_application_data.get('endDate', ''))

        # Display the agreement text
        agreement_textbox.configure(state="normal")
        agreement_textbox.delete("1.0", ctk.END)
        agreement_textbox.insert(ctk.END, agreement_text)
        agreement_textbox.configure(state="disabled", font=("Arial", 16))

        # Clear the checkbox and disable the submit button
        agree_var.set(False)
        submit_button_page3.configure(state="disabled")

        # Clear status label
        status_label_page3.configure(text="")

        # Show Page 3
        pages["Page3"].tkraise()
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while retrieving the agreement: {str(e)}")
        return


def on_agree_checkbox_change():
    submit_button_page3.configure(state="normal" if agree_var.get() else "disabled")


def submit_application():
    global conn, cursor, rental_application_data
    
    # Ensure database connection is active
    if not ensure_db_connection():
        return
        
    # Insert rental data into the rental table
    try:
        cursor.execute("""
        INSERT INTO rental (combined_properties_id, tenantID, startDate, endDate, rentalAmount, stallPurpose, stallName, startOperatingTime, endOperatingTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rental_application_data['stallID'],
            rental_application_data['tenantID'],
            rental_application_data['startDate'],
            rental_application_data['endDate'],
            stall_info['rental_fee'],  # Use the rental fee from stall_info
            rental_application_data['stallPurpose'],
            rental_application_data['stallName'],
            rental_application_data['startOperatingTime'],
            rental_application_data['endOperatingTime']
        ))
        conn.commit()
        
        # Show success message
        messagebox.showinfo("Success", "Rental application submitted successfully!")
        
        # Close the application window
        root.destroy()
        
    except Exception as e:
        status_label_page3.configure(text=f"An error occurred: {e}", text_color="red")


def reset_application():
    # Close the application
    root.destroy()


# Widgets for Page 3
page3 = ctk.CTkFrame(master=container, fg_color="transparent")
pages["Page3"] = page3

# Use grid to manage the page layout
page3.grid(row=0, column=0, sticky='nsew')
page3.grid_rowconfigure(1, weight=1)
page3.grid_columnconfigure(0, weight=1)

# Create header
create_header(page3, "Rental Application Agreement")

# Agreement Frame
agreement_frame = ctk.CTkFrame(master=page3, fg_color="#FFFFFF", corner_radius=10)
agreement_frame.grid(row=1, column=0, padx=200, pady=30, sticky='nsew')

agreement_frame.grid_rowconfigure(0, weight=1)
agreement_frame.grid_columnconfigure(0, weight=1)

# Agreement Textbox
agreement_textbox = ctk.CTkTextbox(master=agreement_frame, width=800, height=500, wrap="word",
                                   fg_color="#FFFFFF", text_color="black", border_color="#D8BFD8",
                                   corner_radius=5, font=("Arial", 16))  # Increased font size from 14 to 16
agreement_textbox.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
agreement_textbox.configure(state="disabled")

# Checkbox for agreement
agree_var = tk.BooleanVar()
agree_checkbox = ctk.CTkCheckBox(master=page3, text="I agree to the terms and conditions",
                                 variable=agree_var, onvalue=True, offvalue=False,
                                 command=on_agree_checkbox_change,
                                 font=("Arial", 16))  # Increased font size
agree_checkbox.grid(row=2, column=0, pady=20)
ToolTip(agree_checkbox, "You must agree to the terms to proceed.")

# Submit Button
submit_button_page3 = ctk.CTkButton(master=page3, text="Submit Application", command=submit_application,
                                    width=300, height=70, font=("Arial", 32),
                                    fg_color="#C4A484",  # Light brown
                                    hover_color="#8B4513",  # Darker brown on hover
                                    corner_radius=20)
submit_button_page3.grid(row=3, column=0, pady=40)
ToolTip(submit_button_page3, "Submit your rental application.")

# Status Label
status_label_page3 = ctk.CTkLabel(master=page3, text="", font=("Arial", 24))
status_label_page3.grid(row=4, column=0, pady=10)


# Function to update Page 2 information
def update_page2_info():
    tenant_name_value.configure(text=tenant_info.get('name', 'N/A'))
    ic_number_value.configure(text=tenant_info.get('ic_number', 'N/A'))
    stall_location_value.configure(text=stall_info.get('location', 'N/A'))
    rental_fee_value.configure(text=f"RM{stall_info.get('rental_fee', 0):.2f}")
    stall_size_value.configure(text=f"{stall_info.get('stall_size', 0)} sqft")


# Start with Page1
pages["Page1"].tkraise()

# Start the main loop
try:
    root.mainloop()
finally:
    # Close the database connection when the application is closed
    if conn:
        conn.close()
