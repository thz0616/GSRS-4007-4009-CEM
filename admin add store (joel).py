import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from customtkinter import CTkImage
import sqlite3
from tkintermapview import TkinterMapView

# Initialize customtkinter appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Add these global variables at the top of your script, after the imports
global_form_data = {}
global_image_path = None

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_combined_table(conn):
    """Create a combined table if it doesn't exist"""
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            status INTEGER DEFAULT 1,
            addressLine1 TEXT,
            addressLine2 TEXT,
            postcode TEXT,
            city TEXT,
            state TEXT,
            sqft INTEGER,
            price REAL,
            description TEXT,
            image_path TEXT
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_combined_property(conn, property_data):
    """Insert a new combined property into the database"""
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO combined_properties (
            latitude, longitude, status, addressLine1, addressLine2, postcode, city, state,
            sqft, price, description, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', property_data)
        
        conn.commit()
        print("Property added successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def add_property():
    addressLine1 = address_entry.get()
    addressLine2 = address2_entry.get()
    postcode = postcode_entry.get()
    city = city_entry.get()
    state = state_combo.get()
    sqft = sqft_entry.get()
    price = price_entry.get()
    description = description_entry.get("1.0", ctk.END).strip()
    image_path = image_label.image_path if hasattr(image_label, 'image_path') else ""
    latitude = window.selected_coords[0] if hasattr(window, 'selected_coords') else 0.0
    longitude = window.selected_coords[1] if hasattr(window, 'selected_coords') else 0.0
    status = 0  # Default status for new stores

    if not all([addressLine1, postcode, city, state, sqft, price]):
        error_label.configure(text="Please fill in all required fields.")
        return

    try:
        sqft = int(sqft)
        price = float(price)
    except ValueError:
        error_label.configure(text="Sqft must be an integer and price must be a number.")
        return

    # Insert data into SQLite database
    conn = create_connection()
    if conn is not None:
        create_combined_table(conn)
        property_data = (latitude, longitude, status, addressLine1, addressLine2, postcode, city, state,
                         sqft, price, description, image_path)
        insert_combined_property(conn, property_data)
        conn.close()

        # Clear fields after inserting data
        clear_fields()
        error_label.configure(text="Property added successfully!")
    else:
        error_label.configure(text="Error connecting to the database.")

def clear_fields():
    address_entry.delete(0, ctk.END)
    address2_entry.delete(0, ctk.END)
    postcode_entry.delete(0, ctk.END)
    city_entry.delete(0, ctk.END)
    state_combo.set("")
    sqft_entry.delete(0, ctk.END)
    price_entry.delete(0, ctk.END)
    description_entry.delete("1.0", ctk.END)
    image_label.configure(image="", text="No Image Uploaded")
    if hasattr(image_label, 'image_path'):
        del image_label.image_path
    if hasattr(window, 'selected_coords'):
        del window.selected_coords

def upload_image():
    global image_label
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
    )
    if file_path:
        try:
            img = Image.open(file_path)
            img = img.resize((500, 500))  # Resize if needed

            # Convert to CTkImage
            ctk_image = CTkImage(img, size=(500, 500))  # Specify the size for the CTkImage

            # Use CTkImage for image_label
            image_label.configure(image=ctk_image, text="")
            image_label.image = ctk_image  # Keep a reference to avoid garbage collection
            image_label.image_path = file_path  # Save the image path
        except Exception as e:
            print(f"Error loading image: {e}")
            error_label.configure(text="Error loading image.")

def show_map():
    global global_form_data, global_image_path
    
    # Save current form data
    global_form_data = {
        'address': address_entry.get(),
        'address2': address2_entry.get(),
        'postcode': postcode_entry.get(),
        'city': city_entry.get(),
        'state': state_combo.get(),
        'sqft': sqft_entry.get(),
        'price': price_entry.get(),
        'description': description_entry.get("1.0", ctk.END).strip()
    }
    global_image_path = image_label.image_path if hasattr(image_label, 'image_path') else None

    # Hide all current widgets
    for widget in window.winfo_children():
        widget.place_forget()
    
    global map_widget
    map_widget = TkinterMapView(window, width=screen_width, height=screen_height-50, corner_radius=0)
    map_widget.place(x=0, y=50)

    # Set the starting position for the map (centered on Malaysia)
    map_widget.set_position(4.2105, 101.9758)  # Centered on Malaysia
    map_widget.set_zoom(6)  # Zoom level for better focus on Malaysia

    def select_location(coords):
        window.selected_coords = coords
        show_main_page()

    # Add right-click menu command to select location
    map_widget.add_right_click_menu_command("Select this location", select_location, pass_coords=True)

    # Add a Back button
    back_button = ctk.CTkButton(window, text="Back", command=show_main_page, width=100, height=40)
    back_button.place(x=10, y=10)

def show_main_page():
    # Hide all current widgets
    for widget in window.winfo_children():
        widget.place_forget()
    
    setup_main_page()

def back_to_manage_stall():
    window.destroy()  # Close the current window
    
def setup_main_page():
    global bg_label, image_label, upload_button, choose_map_button, address_entry, address2_entry, postcode_entry, city_entry, state_combo, sqft_entry, price_entry, description_entry, add_button, error_label

    # Create a main container frame with light purple background
    main_container = ctk.CTkFrame(window, fg_color="#F0E6FF")
    main_container.place(x=0, y=0, relwidth=1, relheight=1)

    # Add back button at the top left corner
    back_button = ctk.CTkButton(
        main_container,
        text="← Back",
        command=back_to_manage_stall,
        width=100,
        height=40,
        fg_color="#9370DB",  # Purple color to match the theme
        hover_color="#7B68EE",
        font=("Arial", 16, "bold")
    )
    back_button.place(x=20, y=30)

    # Image display area (adjust y position to accommodate back button)
    image_label = ctk.CTkLabel(main_container, text="No Image Uploaded", fg_color="lightgray", width=500, height=500)
    image_label.place(x=300, y=250)

    # Restore image if previously uploaded
    if global_image_path:
        try:
            img = Image.open(global_image_path)
            img = img.resize((500, 500))
            ctk_image = CTkImage(img, size=(500, 500))
            image_label.configure(image=ctk_image, text="")
            image_label.image = ctk_image
            image_label.image_path = global_image_path
        except Exception as e:
            print(f"Error loading image: {e}")

    # Upload button with custom size
    upload_button = ctk.CTkButton(
        main_container, text="Upload \u2191", command=upload_image,
        width=150, height=50, font=("Arial",20),
        text_color="black", fg_color="#d0a9f5", hover_color="#c89ef2"
    )
    upload_button.place(x=470, y=790)

    choose_map_button = ctk.CTkButton(main_container, text="Choose from map", command=show_map,
        width=150, height=50, font=("Arial",20),
        text_color="black", fg_color="#d0a9f5", hover_color="#c89ef2")
    choose_map_button.place(x=460, y=850)

    # Input fields
    address_label = ctk.CTkLabel(main_container, text="Address line 1:", font=("Arial", 20))
    address_label.place(x=1000, y=100)
    address_entry = ctk.CTkEntry(main_container, width=600, height=45, corner_radius=20)
    address_entry.place(x=1000, y=135)

    address2_label = ctk.CTkLabel(main_container, text="Address line 2:", font=("Arial", 20))
    address2_label.place(x=1000, y=190)
    address2_entry = ctk.CTkEntry(main_container, width=600, height=45, corner_radius=20)
    address2_entry.place(x=1000, y=230)

    postcode_label = ctk.CTkLabel(main_container, text="Postcode:", font=("Arial", 20))
    postcode_label.place(x=1000, y=290)
    postcode_entry = ctk.CTkEntry(main_container, width=600, height=45, corner_radius=20)
    postcode_entry.place(x=1000, y=335)

    city_label = ctk.CTkLabel(main_container, text="City:", font=("Arial", 20))
    city_label.place(x=1000, y=400)
    city_entry = ctk.CTkEntry(main_container, width=300, height=45, corner_radius=20)
    city_entry.place(x=1000, y=430)

    state_label = ctk.CTkLabel(main_container, text="State:", font=("Arial", 20))
    state_label.place(x=1300, y=400)
    state_options = [
        "Selangor", "Johor Bahru", "Pulau Pinang", "Kedah",
        "Kelantan", "Terengganu", "Sabah", "Sarawak",
        "Malacca", "Pahang", "Perak", "Perlis",
        "Negeri Sembilan"
    ]
    state_combo = ctk.CTkComboBox(main_container, values=state_options, width=300, height=45, corner_radius=20)
    state_combo.place(x=1320, y=430)

    sqft_label = ctk.CTkLabel(main_container, text="Sqft:", font=("Arial", 20))
    sqft_label.place(x=1000, y=500)
    sqft_entry = ctk.CTkEntry(main_container, width=600, height=45, corner_radius=20)
    sqft_entry.place(x=1000, y=535)

    price_label = ctk.CTkLabel(main_container, text="Price:", font=("Arial",20))
    price_label.place(x=1000, y=600)
    price_entry = ctk.CTkEntry(main_container, width=600, height=45, corner_radius=20)
    price_entry.place(x=1000, y=635)

    description_label = ctk.CTkLabel(main_container, text="Description:", font=("Arial", 20))
    description_label.place(x=1000, y=700)
    description_entry = ctk.CTkTextbox(main_container, height=150, width=600, corner_radius=20)
    description_entry.place(x=1000, y=750)

    # Restore form data if available
    if global_form_data:
        address_entry.insert(0, global_form_data.get('address', ''))
        address2_entry.insert(0, global_form_data.get('address2', ''))
        postcode_entry.insert(0, global_form_data.get('postcode', ''))
        city_entry.insert(0, global_form_data.get('city', ''))
        state_combo.set(global_form_data.get('state', ''))
        sqft_entry.insert(0, global_form_data.get('sqft', ''))
        price_entry.insert(0, global_form_data.get('price', ''))
        description_entry.insert("1.0", global_form_data.get('description', ''))

    # Add button
    add_button = ctk.CTkButton(
        main_container, text="ADD", fg_color="#d0a9f5", hover_color="#c89ef2",
        text_color="black", font=("Arial", 20), command=add_property,
        width=600, height=50
    )
    add_button.place(x=1000, y=935)

    # Error label
    error_label = ctk.CTkLabel(main_container, text="", text_color="red")
    error_label.place(x=1000, y=990)

    # Display selected coordinates if available
    if hasattr(window, 'selected_coords'):
        coords_label = ctk.CTkLabel(main_container, text=f"Selected coordinates: {window.selected_coords}", font=("Arial", 16))
        coords_label.place(x=300, y=200)

# Create the main window using customtkinter
window = ctk.CTk()
window.title("Property Listing")

# Set window fullscreen size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width}x{screen_height}+0+0")

# Set the window background color
window.configure(fg_color="#F0E6FF")  # Light purple background color

# Set window to fullscreen
window.attributes('-fullscreen', True)

# Add an escape key binding to exit fullscreen
def exit_fullscreen(event=None):
    window.attributes('-fullscreen', False)
    window.geometry(f"{screen_width}x{screen_height}+0+0")  # Return to maximized state

window.bind('<Escape>', exit_fullscreen)  # Allow escape key to exit fullscreen

setup_main_page()

window.mainloop()
