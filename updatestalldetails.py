import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from customtkinter import CTkImage
import sqlite3
from tkintermapview import TkinterMapView
import sys

# Get stall_id from command line argument
stall_id = None
if len(sys.argv) > 1:
    try:
        stall_id = int(sys.argv[1])
        print(f"Editing stall ID: {stall_id}")
    except ValueError:
        print("Invalid stall ID provided")

def initialize_update_stall_page(stall_id):
    # Initialize customtkinter appearance settings
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Declare global variables
    global global_form_data, global_image_path, image_label, address_entry, address2_entry
    global postcode_entry, city_entry, state_combo, sqft_entry, price_entry, description_entry, error_label
    global back_button

    global_form_data = {}
    global_image_path = None

    # Create the main window
    window = ctk.CTk()
    window.attributes('-fullscreen', True)
    window.title(f"Updating Stall {stall_id}")

    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Set window fullscreen size
    window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Set light purple background
    window.configure(fg_color="#f0e6ff")  # Light purple color

    # Add title label
    title_label = ctk.CTkLabel(
        window, 
        text=f"Updating Stall {stall_id}", 
        font=("Arial", 24, "bold"),
        text_color="#5c2e91"  # Dark purple for contrast
    )
    title_label.place(x=screen_width//2 - 100, y=20)

    def back_to_view_stall():
        window.destroy()  # Only close this window
        window.quit()     # Stop this window's mainloop

    # Move back button to a different position
    back_button = ctk.CTkButton(
        window,
        text="← Back",
        command=back_to_view_stall,
        width=100,
        height=40,
        fg_color="#d0a9f5",
        hover_color="#c89ef2",
        text_color="black",
        font=("Arial", 16, "bold")
    )
    back_button.place(x=screen_width - 150, y=20)  # Moved to top right corner

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

    def update_combined_property(conn, property_data, stall_id):
        """Update an existing property in the database"""
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE combined_properties SET
                latitude = ?,
                longitude = ?,
                status = ?,
                addressLine1 = ?,
                addressLine2 = ?,
                postcode = ?,
                city = ?,
                state = ?,
                sqft = ?,
                price = ?,
                description = ?,
                image_path = ?
            WHERE id = ?
            ''', property_data + (stall_id,))
            
            conn.commit()
            print("Property updated successfully!")
            return True
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False

    def update_property():
        global image_label, address_entry, address2_entry, postcode_entry, city_entry
        global state_combo, sqft_entry, price_entry, description_entry, error_label
        
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
        status = 1  # Status for existing stores

        if not all([addressLine1, postcode, city, state, sqft, price]):
            error_label.configure(text="Please fill in all required fields.", text_color="red")
            return

        try:
            sqft = int(sqft)
            price = float(price)
        except ValueError:
            error_label.configure(text="Sqft must be an integer and price must be a number.", text_color="red")
            return

        # Update data in SQLite database
        conn = create_connection()
        if conn is not None:
            property_data = (latitude, longitude, status, addressLine1, addressLine2, postcode, 
                            city, state, sqft, price, description, image_path)
            if update_combined_property(conn, property_data, stall_id):
                error_label.configure(text="Property updated successfully!", text_color="green")
            else:
                error_label.configure(text="Error updating the property.", text_color="red")
            conn.close()
        else:
            error_label.configure(text="Error connecting to the database.", text_color="red")

    def clear_fields():
        global image_label, address_entry, address2_entry, postcode_entry, city_entry
        global state_combo, sqft_entry, price_entry, description_entry
        
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
        global image_label, error_label
        
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
                error_label.configure(text="Error loading image.", text_color="red")

    def show_map():
        # Save current form data
        global global_form_data, global_image_path
        
        # Clear the existing form data before saving new data
        global_form_data.clear()
        
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

        map_widget = TkinterMapView(window, width=screen_width, height=screen_height-50, corner_radius=0)
        map_widget.place(x=0, y=50)

        # Set initial position
        initial_lat = window.selected_coords[0] if hasattr(window, 'selected_coords') else 4.2105
        initial_long = window.selected_coords[1] if hasattr(window, 'selected_coords') else 101.9758
        map_widget.set_position(initial_lat, initial_long)
        map_widget.set_zoom(15)

        def select_location(coords):
            window.selected_coords = coords
            show_main_page()

        map_widget.add_right_click_menu_command("Select this location", select_location, pass_coords=True)

        # Add a button to return to the main update page (moved up)
        back_to_update_button = ctk.CTkButton(
            window,
            text="Back to Update",
            command=show_main_page,
            width=150,
            height=40,
            fg_color="#d0a9f5",
            hover_color="#c89ef2",
            text_color="black",
            font=("Arial", 16, "bold")
        )
        back_to_update_button.place(x=20, y=5)  # Moved up from y=20 to y=5

    def show_main_page():
        # Clear all widgets
        for widget in window.winfo_children():
            widget.place_forget()
        
        setup_main_page()
        
        # Clear all entry fields before restoring data
        address_entry.delete(0, ctk.END)
        address2_entry.delete(0, ctk.END)
        postcode_entry.delete(0, ctk.END)
        city_entry.delete(0, ctk.END)
        state_combo.set("")
        sqft_entry.delete(0, ctk.END)
        price_entry.delete(0, ctk.END)
        description_entry.delete("1.0", ctk.END)
        
        # Now restore form data if available
        if global_form_data:
            address_entry.insert(0, global_form_data.get('address', ''))
            address2_entry.insert(0, global_form_data.get('address2', ''))
            postcode_entry.insert(0, global_form_data.get('postcode', ''))
            city_entry.insert(0, global_form_data.get('city', ''))
            state_combo.set(global_form_data.get('state', ''))
            sqft_entry.insert(0, global_form_data.get('sqft', ''))
            price_entry.insert(0, global_form_data.get('price', ''))
            description_entry.insert("1.0", global_form_data.get('description', ''))
        
        # Make sure back button stays visible
        back_button.place(x=screen_width - 150, y=20)

    def load_existing_data(stall_id):
        """Load existing property data from database"""
        global image_label, address_entry, address2_entry, postcode_entry, city_entry
        global state_combo, sqft_entry, price_entry, description_entry, error_label

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT latitude, longitude, addressLine1, addressLine2, postcode, 
                           city, state, sqft, price, description, image_path
                    FROM combined_properties 
                    WHERE id = ?
                ''', (stall_id,))
                
                row = cursor.fetchone()
                if row:
                    # Store coordinates
                    window.selected_coords = (row[0], row[1])  # Latitude, Longitude
                    
                    # Fill in the form fields
                    address_entry.insert(0, row[2] or '')
                    address2_entry.insert(0, row[3] or '')
                    postcode_entry.insert(0, row[4] or '')
                    city_entry.insert(0, row[5] or '')
                    state_combo.set(row[6] or '')
                    sqft_entry.insert(0, str(row[7]) if row[7] else '')
                    price_entry.insert(0, str(row[8]) if row[8] else '')
                    description_entry.insert("1.0", row[9] or '')

                    # Load image if exists
                    if row[10]:  # image_path
                        try:
                            img = Image.open(row[10])
                            img = img.resize((500, 500))
                            ctk_image = CTkImage(img, size=(500, 500))
                            image_label.configure(image=ctk_image, text="")
                            image_label.image = ctk_image
                            image_label.image_path = row[10]
                        except Exception as e:
                            print(f"Error loading image: {e}")
                            error_label.configure(text="Error loading existing image.", text_color="red")
                    
                    # Display coordinates in single label
                    coords_label = ctk.CTkLabel(
                        window, 
                        text=f"Selected coordinates: ({row[0]}, {row[1]})", 
                        font=("Arial", 16)
                    )
                    coords_label.place(x=300, y=200)

                conn.close()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                error_label.configure(text="Error loading existing data.", text_color="red")

    def setup_main_page():
        global image_label, address_entry, address2_entry, postcode_entry, city_entry
        global state_combo, sqft_entry, price_entry, description_entry, error_label
        
        # Image display area
        image_label = ctk.CTkLabel(window, text="No Image Uploaded", fg_color="lightgray", width=500, height=500)
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
            window, text="Upload \u2191", command=upload_image,
            width=150, height=50, font=("Arial",20),
            text_color="black", fg_color="#d0a9f5", hover_color="#c89ef2"
        )
        upload_button.place(x=470, y=790)

        choose_map_button = ctk.CTkButton(window, text="Choose from map", command=show_map,
            width=150, height=50, font=("Arial",20),
            text_color="black", fg_color="#d0a9f5", hover_color="#c89ef2")
        choose_map_button.place(x=460, y=850)

        # Input fields
        address_label = ctk.CTkLabel(window, text="Address line 1:", font=("Arial", 20))
        address_label.place(x=1000, y=100)
        address_entry = ctk.CTkEntry(window, width=600, height=45, corner_radius=20)
        address_entry.place(x=1000, y=135)

        address2_label = ctk.CTkLabel(window, text="Address line 2:", font=("Arial", 20))
        address2_label.place(x=1000, y=190)
        address2_entry = ctk.CTkEntry(window, width=600, height=45, corner_radius=20)
        address2_entry.place(x=1000, y=230)

        postcode_label = ctk.CTkLabel(window, text="Postcode:", font=("Arial", 20))
        postcode_label.place(x=1000, y=290)
        postcode_entry = ctk.CTkEntry(window, width=600, height=45, corner_radius=20)
        postcode_entry.place(x=1000, y=335)

        city_label = ctk.CTkLabel(window, text="City:", font=("Arial", 20))
        city_label.place(x=1000, y=400)
        city_entry = ctk.CTkEntry(window, width=300, height=45, corner_radius=20)
        city_entry.place(x=1000, y=430)

        state_label = ctk.CTkLabel(window, text="State:", font=("Arial", 20))
        state_label.place(x=1300, y=400)
        state_options = [
            "Selangor", "Johor Bahru", "Pulau Pinang", "Kedah",
            "Kelantan", "Terengganu", "Sabah", "Sarawak",
            "Malacca", "Pahang", "Perak", "Perlis",
            "Negeri Sembilan"
        ]
        state_combo = ctk.CTkComboBox(window, values=state_options, width=300, height=45, corner_radius=20)
        state_combo.place(x=1320, y=430)

        sqft_label = ctk.CTkLabel(window, text="Sqft:", font=("Arial", 20))
        sqft_label.place(x=1000, y=500)
        sqft_entry = ctk.CTkEntry(window, width=600, height=45, corner_radius=20)
        sqft_entry.place(x=1000, y=535)

        price_label = ctk.CTkLabel(window, text="Price:", font=("Arial",20))
        price_label.place(x=1000, y=600)
        price_entry = ctk.CTkEntry(window, width=600, height=45, corner_radius=20)
        price_entry.place(x=1000, y=635)

        description_label = ctk.CTkLabel(window, text="Description:", font=("Arial", 20))
        description_label.place(x=1000, y=700)
        description_entry = ctk.CTkTextbox(window, height=150, width=600, corner_radius=20)
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

        # Update button (moved up to where delete button was)
        update_button = ctk.CTkButton(
            window,
            text="UPDATE",
            fg_color="#d0a9f5",
            hover_color="#c89ef2",
            text_color="black",
            font=("Arial", 20),
            command=update_property,
            width=600,
            height=50
        )
        update_button.place(x=1000, y=870)  # Moved up to previous delete button position

        # Error label (moved up accordingly)
        error_label = ctk.CTkLabel(window, text="", text_color="red")
        error_label.place(x=1000, y=925)  # Moved up to maintain spacing

        # Display selected coordinates if available
        if hasattr(window, 'selected_coords'):
            coords_label = ctk.CTkLabel(
                window, 
                text=f"Selected coordinates: ({window.selected_coords[0]}, {window.selected_coords[1]})", 
                font=("Arial", 16)
            )
            coords_label.place(x=300, y=200)

        # Add this at the end of setup_main_page
        load_existing_data(stall_id)

        # Make sure the back button stays on top
        back_button.lift()

    # Initialize the main page
    setup_main_page()
    window.mainloop()

# Example usage:
# initialize_update_stall_page(123)
initialize_update_stall_page(stall_id)