import customtkinter as ctk
import tkinter as tk
import sqlite3
from PIL import Image, ImageTk
from functools import partial
import subprocess
import sys
from tkinter import messagebox
import os

# Initialize customtkinter appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Define custom colors
PRIMARY_COLOR = "#B39DDB"          # Light Purple
SECONDARY_COLOR = "#E1BEE7"        # Lighter Purple
BUTTON_COLOR = "#9575CD"           # Medium Purple for Buttons
BUTTON_HOVER_COLOR = "#7E57C2"     # Darker Purple for Button Hover
SELECTED_BUTTON_COLOR = "#FFC107"  # Amber color for selected filter buttons
UNSELECTED_BUTTON_COLOR = "#9575CD"  # Medium purple (same as BUTTON_COLOR)
TEXT_COLOR = "#333333"             # Dark Gray for Text

# Global variables
global perform_search, image_refs, size_filter_option, price_filter_option, stall_count
perform_search = None
image_refs = []
size_filter_option = None
price_filter_selected_button = None
price_filter_option = None
size_filter_selected_button = None
stall_count = 0

# Add these functions after the color definitions

def get_size_range():
    """Get min and max size from database"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(sqft), MAX(sqft) FROM combined_properties")
        min_size, max_size = cursor.fetchone()
        conn.close()
        
        # Ensure we have valid numeric values
        min_size = float(min_size) if min_size is not None else 0
        max_size = float(max_size) if max_size is not None else 1000
        
        # If min and max are the same, create a small range
        if min_size == max_size:
            min_size = max(0, min_size - 10)
            max_size = max_size + 10
            
        return min_size, max_size
    except sqlite3.Error:
        return 0, 1000

def get_price_range():
    """Get min and max price from database"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(price), MAX(price) FROM combined_properties")
        min_price, max_price = cursor.fetchone()
        conn.close()
        
        # Ensure we have valid numeric values
        min_price = float(min_price) if min_price is not None else 0
        max_price = float(max_price) if max_price is not None else 1000
        
        # If min and max are the same, create a small range
        if min_price == max_price:
            min_price = max(0, min_price - 10)
            max_price = max_price + 10
            
        return min_price, max_price
    except sqlite3.Error:
        return 0, 1000

def edit_details(stall_id):
    """Launch the stall details editor"""
    try:
        subprocess.Popen([sys.executable, 'updatestalldetails.py', str(stall_id)])
    except Exception as e:
        messagebox.showerror("Error", f"Error launching stall editor: {e}")

def delete_stall(stall_id):
    """Delete a stall from the database"""
    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this stall? This action cannot be undone.",
        icon='warning'
    )
    
    if confirm:
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM combined_properties WHERE id = ?", (stall_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stall deleted successfully!")
            perform_search()  # Refresh the stall list
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred while deleting: {e}")

# Get initial size and price ranges
min_size, max_size = get_size_range()
min_price, max_price = get_price_range()

# Add this function after the imports and before show_admin_manage_stall
def open_add_stall():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the add store script
        add_store_path = os.path.join(current_dir, "admin add store (joel).py")
        
        # Create transition window
        transition = ctk.CTkToplevel()
        transition.title("Opening Add Stall")
        transition.attributes('-fullscreen', True)
        transition.configure(fg_color="#F0E6FF")
        
        # Create main container
        main_container = ctk.CTkFrame(transition, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.4, anchor="center")
        
        # Add store icon
        icon_label = ctk.CTkLabel(
            main_container,
            text="🏪",  # Store emoji
            font=ctk.CTkFont(size=80),
            text_color="#4A3F75"
        )
        icon_label.pack(pady=(0, 30))
        
        # Content frame
        content_frame = ctk.CTkFrame(
            main_container,
            fg_color="#E6D8FF",
            corner_radius=20,
            width=500,
            height=200
        )
        content_frame.pack(padx=40, pady=20)
        content_frame.pack_propagate(False)
        
        # Text frame
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        loading_label = ctk.CTkLabel(
            text_frame,
            text="Opening Add Stall Window",
            font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),
            text_color="#4A3F75"
        )
        loading_label.pack(pady=(0, 15))
        
        # Launch the add store script with fullscreen argument
        subprocess.Popen([sys.executable, add_store_path, "--fullscreen"])
        
        # Close transition window after a delay
        transition.after(2000, transition.destroy)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error opening Add Stall window: {e}")

def show_admin_manage_stall(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for stall management
    stall_frame = ctk.CTkFrame(root, fg_color="#F0E6FF")  # Light purple background
    stall_frame.pack(fill="both", expand=True)
    
    # Initialize StringVar variables
    global size_filter_option, price_filter_option
    size_filter_option = tk.StringVar(value="all")
    price_filter_option = tk.StringVar(value="all")
    
    def back_to_home():
        # Hide stall frame and call the dashboard callback
        stall_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=stall_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)

    # Create Header
    header_frame = ctk.CTkFrame(stall_frame, height=100, fg_color=PRIMARY_COLOR)
    header_frame.pack(fill="x")

    # Create a container for the header content
    header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
    header_content.pack(fill="x", padx=20)

    # Title on the left
    header_label = ctk.CTkLabel(
        header_content,
        text="Manage Stall",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color="white"
    )
    header_label.pack(side="left", pady=30)

    # Check Stall Status button on the right
    def open_stall_status():
        try:
            # Create transition window
            transition = ctk.CTkToplevel(root)
            transition.title("Loading Map")
            transition.attributes('-fullscreen', True)
            transition.configure(fg_color="#F0E6FF")  # Light purple background
            
            # Create main container with some padding from top
            main_container = ctk.CTkFrame(transition, fg_color="transparent")
            main_container.place(relx=0.5, rely=0.4, anchor="center")
            
            # Add a decorative icon or symbol (map icon using text)
            icon_label = ctk.CTkLabel(
                main_container,
                text="🗺️",  # Map emoji
                font=ctk.CTkFont(size=80),
                text_color="#4A3F75"
            )
            icon_label.pack(pady=(0, 30))
            
            # Create a frame for the loading content with a light background
            content_frame = ctk.CTkFrame(
                main_container, 
                fg_color="#E6D8FF",  # Slightly darker than background
                corner_radius=20,
                width=500,
                height=200
            )
            content_frame.pack(padx=40, pady=20)
            content_frame.pack_propagate(False)  # Maintain fixed size
            
            # Inner frame for text content
            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Loading message with enhanced styling
            loading_label = ctk.CTkLabel(
                text_frame,
                text="Initializing Map View",
                font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),
                text_color="#4A3F75"
            )
            loading_label.pack(pady=(0, 15))
            
            # Progress message with dots animation
            progress_label = ctk.CTkLabel(
                text_frame,
                text="Please wait.",
                font=ctk.CTkFont(family="Helvetica", size=24),
                text_color="#6B5B95"  # Slightly lighter purple for secondary text
            )
            progress_label.pack()
            
            # Add a subtle message at the bottom
            info_label = ctk.CTkLabel(
                main_container,
                text="This may take a few moments...",
                font=ctk.CTkFont(family="Helvetica", size=16),
                text_color="#8B7BB5"  # Even lighter purple for tertiary text
            )
            info_label.pack(pady=(20, 0))
            
            # Hide main window immediately
            root.withdraw()
            
            # Start the map process immediately without waiting
            map_process = subprocess.Popen([sys.executable, 'show_stalls_on_map.py'])
            
            def check_map_window():
                try:
                    # Check if the map window exists by looking for a window with the title "Stalls Map"
                    import win32gui
                    def callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "Stalls Map" in title:
                                windows.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(callback, windows)
                    
                    if windows:  # If map window is found
                        transition.destroy()  # Close the transition window
                    else:
                        if map_process.poll() is None:  # If map process is still running
                            transition.after(100, check_map_window)  # Check again after 100ms
                        else:
                            # Map process ended without creating window
                            transition.destroy()
                            root.deiconify()
                except Exception as e:
                    print(f"Error checking map window: {e}")
                    transition.after(100, check_map_window)
            
            def update_dots(dot_count=0):
                dots = "." * (dot_count % 4)  # Will cycle through 0-3 dots
                progress_label.configure(text=f"Please wait{dots}")
                transition.after(500, update_dots, dot_count + 1)  # Update every 500ms
            
            # Start both the dots animation and window checking
            update_dots()
            check_map_window()
            
            # Wait for map process to complete before showing main window
            def check_process_end():
                if map_process.poll() is not None:  # Process has ended
                    root.deiconify()
                else:
                    root.after(100, check_process_end)
            
            check_process_end()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error managing stall status windows: {e}")
            root.deiconify()  # Ensure the main window is shown even if there's an error

    check_status_btn = ctk.CTkButton(
        header_content,
        text="Check Stall Status",
        command=open_stall_status,
        width=150,
        height=40,
        fg_color="#4CAF50",  # Green color to distinguish it
        hover_color="#45a049",  # Darker green for hover
        font=ctk.CTkFont(size=16, weight="bold")
    )
    check_status_btn.pack(side="right", pady=30)

    # Add Stall Button
    add_stall_btn = ctk.CTkButton(
        header_content,
        text="Add Stall",
        command=open_add_stall,
        width=150,
        height=40,
        fg_color="#4CAF50",  # Green color
        hover_color="#45a049",  # Darker green for hover
        font=ctk.CTkFont(size=16, weight="bold")
    )
    add_stall_btn.pack(side="right", pady=30, padx=(0, 10))  # Added padding between buttons

    # Create Main Frame
    main_frame = ctk.CTkFrame(stall_frame)
    main_frame.pack(fill="both", expand=True)

    # [Rest of your existing code, but replace 'app' with 'stall_frame']
    # Create Search Bar Frame
    search_frame = ctk.CTkFrame(main_frame, fg_color=SECONDARY_COLOR, corner_radius=10)
    search_frame.pack(fill="x", padx=20, pady=10)

    # Search Entry
    search_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="Search by Address, Postcode, City, or State...",
        font=ctk.CTkFont(size=18),
        height=50
    )
    search_entry.pack(side="left", padx=(20, 10), pady=10, fill="x", expand=True)

    # Search Button
    search_button = ctk.CTkButton(
        search_frame,
        text="Search",
        font=ctk.CTkFont(size=18, weight="bold"),
        width=150,
        height=50,
        fg_color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
        command=lambda: perform_search()
    )
    search_button.pack(side="left", padx=(10, 20), pady=10)

    # Variables for filters
    size_filter_option = tk.StringVar(value="all")
    price_filter_option = tk.StringVar(value="all")
    size_filter_selected_button = None
    price_filter_selected_button = None

    # State filter variables
    state_options = [
        "Selangor", "Johor Bahru", "Pulau Pinang", "Kedah",
        "Kelantan", "Terengganu", "Sabah", "Sarawak",
        "Malacca", "Pahang", "Perak", "Perlis",
        "Negeri Sembilan", "Other"
    ]
    state_vars = {state: False for state in state_options}
    state_buttons = {}

    # Functions to handle filter button clicks
    def size_filter_button_click(value, button):
        global size_filter_option, size_filter_selected_button
        # Update the variable
        size_filter_option.set(value)
        # Update the appearance of the previously selected button
        if size_filter_selected_button is not None:
            size_filter_selected_button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        # Update the appearance of the newly selected button
        button.configure(fg_color=SELECTED_BUTTON_COLOR, text_color="black")
        # Update the reference
        size_filter_selected_button = button
        # Show or hide custom controls
        if value == "custom":
            size_custom_controls_frame.grid()
        else:
            size_custom_controls_frame.grid_remove()
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    def price_filter_button_click(value, button):
        global price_filter_option, price_filter_selected_button
        # Update the variable
        price_filter_option.set(value)
        # Update the appearance of the previously selected button
        if price_filter_selected_button is not None:
            price_filter_selected_button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        # Update the appearance of the newly selected button
        button.configure(fg_color=SELECTED_BUTTON_COLOR, text_color="black")
        # Update the reference
        price_filter_selected_button = button
        # Show or hide custom controls
        if value == "custom":
            price_custom_controls_frame.grid()
        else:
            price_custom_controls_frame.grid_remove()
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    def state_filter_button_click(state, button):
        # Toggle the selection state
        if state_vars[state]:
            state_vars[state] = False
            button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        else:
            state_vars[state] = True
            button.configure(fg_color=SELECTED_BUTTON_COLOR, text_color="black")
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    # To keep a reference to images to prevent garbage collection
    image_refs = []

    # Debounce timers
    size_entry_timer = None
    price_entry_timer = None

    # Function to perform search and filter
    def perform_search_internal():
        query = search_entry.get().strip()
        # Use global variables for filters
        global size_filter_option, price_filter_option, search_result_label
        # Clear the current stall list
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        # Fetch and display stalls based on the search query and filters
        num_stalls = fetch_and_display_stalls(query, size_filter_option.get(), price_filter_option.get())
        # Update the search result label
        if num_stalls == 1:
            stall_text = "stall"
        else:
            stall_text = "stalls"
        if query:
            search_result_label.configure(text=f"{num_stalls} {stall_text} found for '{query}'")
        else:
            search_result_label.configure(text=f"All stalls: {num_stalls} {stall_text} found")
        # Update filter tags
        update_filter_tags()

    # Assign the internal function to the global variable
    global perform_search
    perform_search = perform_search_internal

    # Function to fetch and display stalls
    def fetch_and_display_stalls(search_query="", size_filter="all", price_filter="all"):
        global stall_count
        
        # Connect to the SQLite database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Modified query to include rental status information
        query = """
            SELECT cp.*, 
                CASE 
                    WHEN r.isApprove = 1 THEN 'Rented'
                    WHEN r.isApprove = 0 THEN 'Under Application'
                    ELSE 'Available'
                END as rental_status
            FROM combined_properties cp
            LEFT JOIN rental r ON cp.id = r.combined_properties_id 
            WHERE 1=1
        """
        params = []

        # Search query: Search by addressLine1, addressLine2, postcode, city, or state
        if search_query:
            query += """
                AND (
                    cp.city LIKE ?
                    OR cp.state LIKE ?
                    OR cp.addressLine1 LIKE ?
                    OR cp.addressLine2 LIKE ?
                    OR cp.postcode LIKE ?
                )
            """
            like_query = '%' + search_query + '%'
            params.extend([like_query] * 5)

        # Size filter
        if size_filter != "all":
            if size_filter == "below_300":
                query += " AND sqft < ?"
                params.append(300)
            elif size_filter == "300_600":
                query += " AND sqft BETWEEN ? AND ?"
                params.extend([300, 600])
            elif size_filter == "above_600":
                query += " AND sqft > ?"
                params.append(600)
            elif size_filter == "custom":
                try:
                    lower = float(size_custom_entry_min.get())
                    upper = float(size_custom_entry_max.get())
                    query += " AND sqft BETWEEN ? AND ?"
                    params.extend([lower, upper])
                except ValueError:
                    print("Invalid custom size values")
                    return 0

        # Price filter
        if price_filter != "all":
            if price_filter == "below_250":
                query += " AND price < ?"
                params.append(250)
            elif price_filter == "250_500":
                query += " AND price BETWEEN ? AND ?"
                params.extend([250, 500])
            elif price_filter == "above_500":
                query += " AND price > ?"
                params.append(500)
            elif price_filter == "custom":
                try:
                    lower = float(price_custom_entry_min.get())
                    upper = float(price_custom_entry_max.get())
                    query += " AND price BETWEEN ? AND ?"
                    params.extend([lower, upper])
                except ValueError:
                    print("Invalid custom price values")
                    return 0

        # State filter
        selected_states = [state for state, selected in state_vars.items() if selected]
        if selected_states:
            placeholders = ','.join('?' for _ in selected_states)
            query += f" AND state IN ({placeholders})"
            params.extend(selected_states)

        # Add status filter to the query
        selected_statuses = [status for status, selected in status_vars.items() if selected]
        if selected_statuses:
            status_conditions = []
            for status in selected_statuses:
                if status == "Available":
                    status_conditions.append("r.isApprove IS NULL")
                elif status == "Under Application":
                    status_conditions.append("r.isApprove = 0")
                elif status == "Rented":
                    status_conditions.append("r.isApprove = 1")
            query += f" AND ({' OR '.join(status_conditions)})"

        cursor.execute(query, params)
        stalls = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Clear image references
        global image_refs
        image_refs.clear()

        # Update the stall count
        stall_count = len(stalls)

        # If no stalls found, display a message
        if not stalls:
            no_result_label = ctk.CTkLabel(
                scrollable_frame,
                text="No stalls found matching your search and filter criteria.",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="gray"
            )
            no_result_label.pack(pady=20)
            # Update search result label with 0 stalls
            search_result_label.configure(text="All stalls: 0 stalls found")
            return 0

        # Iterate over each stall and display its details
        for stall in stalls:
            # Create a dictionary to store stall details
            stall_details = {
                'stall_id': stall[0],
                'city': '',
                'sqft': 0,
                'state': '',
                'price': 0,
                'description': '',
                'image_path': '',
                'addressLine1': '',
                'addressLine2': '',
                'postcode': '',
                'rental_status': stall[-1]  # The last column from our modified query
            }

            # Dynamically populate the stall_details dictionary
            for i, column in enumerate(cursor.description):
                column_name = column[0]
                if column_name in stall_details:
                    stall_details[column_name] = stall[i]

            # Create a frame for each stall with enhanced styling
            stall_frame = ctk.CTkFrame(
                scrollable_frame,
                corner_radius=10,
                fg_color="white",
                border_width=2,
                border_color=PRIMARY_COLOR
            )
            stall_frame.pack(pady=15, padx=20, fill="x")

            # Create a horizontal layout within the stall_frame
            stall_inner_frame = ctk.CTkFrame(stall_frame, fg_color="transparent")
            stall_inner_frame.pack(fill="x", padx=20, pady=20)

            # Load and display the stall image with scaling
            try:
                image = Image.open(stall_details['image_path'])
                new_size = (int(250 * 1.25), int(180 * 1.25))  # Increased by 1.25x
                image = image.resize(new_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = ctk.CTkLabel(stall_inner_frame, image=photo, text="")
                image_label.image = photo  # Keep a reference
                image_label.pack(side="left", padx=10)
                image_refs.append(photo)  # Keep a reference to prevent garbage collection
            except Exception as e:
                print(f"Error loading image for stall ID {stall_details['stall_id']}: {e}")
                # Display a placeholder if image fails to load
                placeholder = ctk.CTkLabel(
                    stall_inner_frame,
                    text="No Image Available",
                    width=int(250 * 1.25),
                    height=int(180 * 1.25),
                    fg_color="gray",
                    text_color="white",
                    justify="center",
                    corner_radius=10,
                    font=ctk.CTkFont(size=20, weight="bold")
                )
                placeholder.pack(side="left", padx=10)

            # Create a frame for the details to allow individual label spacing
            details_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
            details_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)

            # Title and Status Frame (horizontal container)
            title_status_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            title_status_frame.pack(fill="x", anchor="w")

            # Title: addressLine1 - addressLine2
            title_text = f"{stall_details['addressLine1']} - {stall_details['addressLine2']}"
            title_label = ctk.CTkLabel(
                title_status_frame,
                text=title_text,
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=TEXT_COLOR,
                justify="left",
                anchor="w",
                wraplength=800
            )
            title_label.pack(side="left", pady=(0, 5))

            # Add subtitle (postcode, city, state)
            subtitle_text = f"{stall_details['postcode']} {stall_details['city']}, {stall_details['state']}"
            subtitle_label = ctk.CTkLabel(
                details_frame,
                text=subtitle_text,
                font=ctk.CTkFont(size=24),  # Increased from 18 to 24
                text_color="#666666",  # Slightly lighter gray for subtitle
                justify="left",
                anchor="w"
            )
            subtitle_label.pack(anchor="w", pady=(0, 10))

            # Add description with word wrap
            description_label = ctk.CTkLabel(
                details_frame,
                text=stall_details['description'],
                font=ctk.CTkFont(size=16),
                text_color=TEXT_COLOR,
                justify="left",
                anchor="w",
                wraplength=600  # Adjust this value based on your layout
            )
            description_label.pack(anchor="w", pady=(0, 10))

            # Create a frame for the size, price, and button, aligned to bottom right
            action_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=10, pady=10, anchor="se")

            # Add empty space to push content to the bottom
            spacer_label = ctk.CTkLabel(action_frame, text="")
            spacer_label.pack(expand=True)

            # Size, Price, and Button Frame
            spb_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
            spb_frame.pack(anchor="center")

            # Status indicator (moved here)
            status_color = {
                "Available": "#4CAF50",     # Green
                "Under Application": "#FFA726",  # Orange
                "Rented": "#EF5350"         # Red
            }

            status_frame = ctk.CTkFrame(
                spb_frame,
                fg_color=status_color.get(stall_details['rental_status'], PRIMARY_COLOR),
                corner_radius=5,
                width=150,  # Increased width to match other buttons
                height=40   # Increased height to match other elements
            )
            status_frame.pack(anchor="center", pady=(0, 10))

            status_label = ctk.CTkLabel(
                status_frame,
                text=stall_details['rental_status'],
                font=ctk.CTkFont(size=16, weight="bold"),  # Increased font size
                text_color="white"
            )
            status_label.pack(padx=10, pady=5)

            # Size Label
            size_label = ctk.CTkLabel(
                spb_frame,
                text=f"{stall_details['sqft']} sqft",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=PRIMARY_COLOR
            )
            size_label.pack(anchor="center", pady=(0, 5))

            # Price Label
            price_label = ctk.CTkLabel(
                spb_frame,
                text=f"RM {stall_details['price']:.2f}",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=PRIMARY_COLOR
            )
            price_label.pack(anchor="center", pady=(0, 5))

            # Buttons Frame for Edit and Delete
            buttons_frame = ctk.CTkFrame(spb_frame, fg_color="transparent")
            buttons_frame.pack(anchor="center", pady=(0, 5))

            # Edit Details Button
            edit_details_button = ctk.CTkButton(
                buttons_frame,
                text="Edit Details",
                width=150,
                height=40,
                fg_color=BUTTON_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                font=ctk.CTkFont(size=18, weight="bold"),
                command=lambda id=stall_details['stall_id']: edit_details(id),
                state="normal" if stall_details['rental_status'] == "Available" else "disabled"
            )
            edit_details_button.pack(pady=(0, 5))

            # Delete Button
            delete_button = ctk.CTkButton(
                buttons_frame,
                text="Delete",
                width=150,
                height=40,
                fg_color="#ff6b6b",
                hover_color="#ff5252",
                font=ctk.CTkFont(size=18, weight="bold"),
                command=lambda id=stall_details['stall_id']: delete_stall(id),
                state="normal" if stall_details['rental_status'] == "Available" else "disabled"
            )
            delete_button.pack()

        # Update search result label with actual count
        stall_text = "stall" if stall_count == 1 else "stalls"
        if search_query:
            search_result_label.configure(text=f"{stall_count} {stall_text} found for '{search_query}'")
        else:
            search_result_label.configure(text=f"All stalls: {stall_count} {stall_text} found")

        return stall_count

    # Create a frame for the content below the search bar
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True)

    # Configure grid for content_frame
    content_frame.columnconfigure(0, weight=0)   # Fixed width for filter frame
    content_frame.columnconfigure(1, weight=1)   # Remaining space for results frame
    content_frame.rowconfigure(0, weight=1)

    # Create the filter frame container with fixed width
    filter_frame_container = ctk.CTkFrame(content_frame, fg_color=SECONDARY_COLOR, corner_radius=10, width=250)
    filter_frame_container.grid(row=0, column=0, padx=20, pady=10, sticky="ns")
    filter_frame_container.grid_propagate(False)  # Prevent frame from resizing based on content

    # Create the results frame
    results_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    results_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Ensure frames expand properly
    results_frame.rowconfigure(0, weight=0)  # search_result_frame
    results_frame.rowconfigure(1, weight=0)  # filter_tags_frame
    results_frame.rowconfigure(2, weight=1)  # scrollable_frame
    results_frame.columnconfigure(0, weight=1)

    # Create a scrollable frame inside filter_frame_container
    filter_frame = ctk.CTkScrollableFrame(
        filter_frame_container,
        fg_color="transparent",
        scrollbar_button_color="gray"
    )
    filter_frame.pack(fill="both", expand=True)

    # Configure filter_frame grid
    filter_frame.columnconfigure(0, weight=1)

    # Center-aligning function
    def center_widget(widget):
        widget.grid(sticky="ew")

    # Size Filter
    size_label = ctk.CTkLabel(filter_frame, text="Size Filter", font=ctk.CTkFont(size=18, weight="bold"))
    size_label.grid(row=0, column=0, padx=20, pady=(20, 10))
    center_widget(size_label)

    size_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
    size_filter_container.grid(row=1, column=0, padx=20)
    center_widget(size_filter_container)

    size_filter_container.columnconfigure(0, weight=1)

    size_options = [
        ("All", "all"),
        ("Below 300 sqft", "below_300"),
        ("300 to 600 sqft", "300_600"),
        ("Above 600 sqft", "above_600"),
        ("Custom", "custom")
    ]

    size_filter_option.set("all")
    size_filter_selected_button = None

    size_buttons_frame = ctk.CTkFrame(size_filter_container, fg_color="transparent")
    size_buttons_frame.grid(row=0, column=0)
    center_widget(size_buttons_frame)

    size_buttons_frame.columnconfigure(0, weight=1)

    for idx, (text, value) in enumerate(size_options):
        button = ctk.CTkButton(
            size_buttons_frame,
            text=text,
            font=ctk.CTkFont(size=16),
            fg_color=UNSELECTED_BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=180,  # Adjusted width to fit within filter frame
            height=40,
            text_color="white"
        )
        button.configure(command=partial(size_filter_button_click, value, button))
        button.grid(row=idx, column=0, pady=5)
        center_widget(button)

    size_custom_controls_frame = ctk.CTkFrame(size_filter_container, fg_color="transparent")
    size_custom_controls_frame.grid(row=1, column=0, pady=10)
    center_widget(size_custom_controls_frame)
    size_custom_controls_frame.grid_remove()  # Initially hidden

    # Size Custom Controls
    # Custom Range Slider without OOP
    def create_range_slider(master, from_, to, width, command):
        canvas = tk.Canvas(master, width=width, height=30, bg=SECONDARY_COLOR, highlightthickness=0)
        canvas.pack(anchor="center")

        # Track Line
        canvas.create_line(10, 15, width - 10, 15, fill="#AFAFAF", width=4)

        # Range Line
        range_line = canvas.create_line(10, 15, width - 10, 15, fill="#FFC107", width=4)

        # Handles
        lower_pos = [10]
        upper_pos = [width - 10]
        active_handle = [None]

        lower_handle = canvas.create_oval(0, 5, 20, 25, fill="#FFC107", outline="")
        upper_handle = canvas.create_oval(width - 20, 5, width, 25, fill="#FFC107", outline="")

        def activate_lower(event):
            active_handle[0] = "lower"

        def activate_upper(event):
            active_handle[0] = "upper"

        def deactivate_handle(event):
            active_handle[0] = None
            if command:
                command(get())

        def move_handle(event):
            x = event.x
            if x < 10:
                x = 10
            if x > width - 10:
                x = width - 10

            if active_handle[0] == "lower":
                if x > upper_pos[0]:
                    x = upper_pos[0]
                lower_pos[0] = x
                canvas.coords(lower_handle, x - 10, 5, x + 10, 25)
                canvas.coords(range_line, lower_pos[0], 15, upper_pos[0], 15)
                canvas.update()
                if command:
                    command(get())
            elif active_handle[0] == "upper":
                if x < lower_pos[0]:
                    x = lower_pos[0]
                upper_pos[0] = x
                canvas.coords(upper_handle, x - 10, 5, x + 10, 25)
                canvas.coords(range_line, lower_pos[0], 15, upper_pos[0], 15)
                canvas.update()
                if command:
                    command(get())

        def get():
            lower_value = from_ + (lower_pos[0] - 10) / (width - 20) * (to - from_)
            upper_value = from_ + (upper_pos[0] - 10) / (width - 20) * (to - from_)
            return (round(lower_value), round(upper_value))

        def set_values(lower, upper):
            lower_pos[0] = 10 + (lower - from_) / (to - from_) * (width - 20)
            upper_pos[0] = 10 + (upper - from_) / (to - from_) * (width - 20)
            canvas.coords(lower_handle, lower_pos[0] - 10, 5, lower_pos[0] + 10, 25)
            canvas.coords(upper_handle, upper_pos[0] - 10, 5, upper_pos[0] + 10, 25)
            canvas.coords(range_line, lower_pos[0], 15, upper_pos[0], 15)
            canvas.update()

        canvas.tag_bind(lower_handle, "<Button-1>", activate_lower)
        canvas.tag_bind(upper_handle, "<Button-1>", activate_upper)
        canvas.bind("<B1-Motion>", move_handle)
        canvas.bind("<ButtonRelease-1>", deactivate_handle)

        return {"canvas": canvas, "get": get, "set": set_values}

    def size_slider_callback(value):
        lower, upper = value
        size_custom_entry_min.delete(0, tk.END)
        size_custom_entry_min.insert(0, int(lower))
        size_custom_entry_max.delete(0, tk.END)
        size_custom_entry_max.insert(0, int(upper))
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    size_slider = create_range_slider(size_custom_controls_frame, from_=min_size, to=max_size, width=160, command=size_slider_callback)
    size_slider["set"](min_size, max_size)

    # Entry Boxes
    size_custom_entry_frame = ctk.CTkFrame(size_custom_controls_frame, fg_color="transparent")
    size_custom_entry_frame.pack(pady=10)
    size_custom_entry_frame.pack(anchor="center")  # Center the entry frame

    size_custom_entry_min = ctk.CTkEntry(size_custom_entry_frame, width=60, font=ctk.CTkFont(size=16))
    size_custom_entry_min.pack(side="left", padx=5)
    size_custom_entry_min.insert(0, int(min_size))

    size_to_label = ctk.CTkLabel(size_custom_entry_frame, text=" to ", font=ctk.CTkFont(size=16))
    size_to_label.pack(side="left")

    size_custom_entry_max = ctk.CTkEntry(size_custom_entry_frame, width=60, font=ctk.CTkFont(size=16))
    size_custom_entry_max.pack(side="left", padx=5)
    size_custom_entry_max.insert(0, int(max_size))

    # Removed size unit label as per your request
    # Debounce function for size entries
    def debounce_size_entry(event):
        global size_entry_timer
        if size_entry_timer:
            size_custom_controls_frame.after_cancel(size_entry_timer)
        size_entry_timer = size_custom_controls_frame.after(750, update_size_slider)

    def update_size_slider():
        global size_entry_timer
        size_entry_timer = None
        try:
            lower = float(size_custom_entry_min.get())
            upper = float(size_custom_entry_max.get())
            # Ensure values are within min and max
            if lower < min_size:
                lower = min_size
                size_custom_entry_min.delete(0, tk.END)
                size_custom_entry_min.insert(0, int(lower))
            if lower > max_size:
                lower = max_size
                size_custom_entry_min.delete(0, tk.END)
                size_custom_entry_min.insert(0, int(lower))
            if upper < min_size:
                upper = min_size
                size_custom_entry_max.delete(0, tk.END)
                size_custom_entry_max.insert(0, int(upper))
            if upper > max_size:
                upper = max_size
                size_custom_entry_max.delete(0, tk.END)
                size_custom_entry_max.insert(0, int(upper))
            # Adjust lower limit if upper < lower
            if upper < lower:
                if min_size <= upper <= max_size:
                    lower = upper
                    size_custom_entry_min.delete(0, tk.END)
                    size_custom_entry_min.insert(0, int(lower))
            size_slider["set"](lower, upper)
            # Update filter tags
            update_filter_tags()
            # Fetch and display stalls
            perform_search()
        except ValueError:
            pass

    size_custom_entry_min.bind("<KeyRelease>", debounce_size_entry)
    size_custom_entry_max.bind("<KeyRelease>", debounce_size_entry)

    # Price Filter
    price_label = ctk.CTkLabel(filter_frame, text="Price Filter", font=ctk.CTkFont(size=18, weight="bold"))
    price_label.grid(row=2, column=0, padx=20, pady=(20, 10))
    center_widget(price_label)

    price_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
    price_filter_container.grid(row=3, column=0, padx=20)
    center_widget(price_filter_container)

    price_filter_container.columnconfigure(0, weight=1)

    price_options = [
        ("All", "all"),
        ("Below RM250", "below_250"),
        ("RM250 to RM500", "250_500"),
        ("Above RM500", "above_500"),
        ("Custom", "custom")
    ]

    price_filter_option.set("all")
    price_filter_selected_button = None

    price_buttons_frame = ctk.CTkFrame(price_filter_container, fg_color="transparent")
    price_buttons_frame.grid(row=0, column=0)
    center_widget(price_buttons_frame)

    price_buttons_frame.columnconfigure(0, weight=1)

    for idx, (text, value) in enumerate(price_options):
        button = ctk.CTkButton(
            price_buttons_frame,
            text=text,
            font=ctk.CTkFont(size=16),
            fg_color=UNSELECTED_BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=180,  # Adjusted width to fit within filter frame
            height=40,
            text_color="white"
        )
        button.configure(command=partial(price_filter_button_click, value, button))
        button.grid(row=idx, column=0, pady=5)
        center_widget(button)

    price_custom_controls_frame = ctk.CTkFrame(price_filter_container, fg_color="transparent")
    price_custom_controls_frame.grid(row=1, column=0, pady=10)
    center_widget(price_custom_controls_frame)
    price_custom_controls_frame.grid_remove()  # Initially hidden

    # Price Custom Controls
    def price_slider_callback(value):
        lower, upper = value
        price_custom_entry_min.delete(0, tk.END)
        price_custom_entry_min.insert(0, int(lower))
        price_custom_entry_max.delete(0, tk.END)
        price_custom_entry_max.insert(0, int(upper))
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    price_slider = create_range_slider(price_custom_controls_frame, from_=min_price, to=max_price, width=160, command=price_slider_callback)
    price_slider["set"](min_price, max_price)

    # Entry Boxes without RM Prefix
    price_custom_entry_frame = ctk.CTkFrame(price_custom_controls_frame, fg_color="transparent")
    price_custom_entry_frame.pack(pady=10)
    price_custom_entry_frame.pack(anchor="center")  # Center the entry frame

    price_custom_entry_min = ctk.CTkEntry(price_custom_entry_frame, width=60, font=ctk.CTkFont(size=16))
    price_custom_entry_min.pack(side="left", padx=5)
    price_custom_entry_min.insert(0, int(min_price))

    price_to_label = ctk.CTkLabel(price_custom_entry_frame, text=" to ", font=ctk.CTkFont(size=16))
    price_to_label.pack(side="left")

    price_custom_entry_max = ctk.CTkEntry(price_custom_entry_frame, width=60, font=ctk.CTkFont(size=16))
    price_custom_entry_max.pack(side="left", padx=5)
    price_custom_entry_max.insert(0, int(max_price))

    # Removed RM labels as per your request
    # Debounce function for price entries
    def debounce_price_entry(event):
        global price_entry_timer
        if price_entry_timer:
            price_custom_controls_frame.after_cancel(price_entry_timer)
        price_entry_timer = price_custom_controls_frame.after(750, update_price_slider)

    def update_price_slider():
        global price_entry_timer
        price_entry_timer = None
        try:
            lower = float(price_custom_entry_min.get())
            upper = float(price_custom_entry_max.get())
            # Ensure values are within min and max
            if lower < min_price:
                lower = min_price
                price_custom_entry_min.delete(0, tk.END)
                price_custom_entry_min.insert(0, int(lower))
            if lower > max_price:
                lower = max_price
                price_custom_entry_min.delete(0, tk.END)
                price_custom_entry_min.insert(0, int(lower))
            if upper < min_price:
                upper = min_price
                price_custom_entry_max.delete(0, tk.END)
                price_custom_entry_max.insert(0, int(upper))
            if upper > max_price:
                upper = max_price
                price_custom_entry_max.delete(0, tk.END)
                price_custom_entry_max.insert(0, int(upper))
            # Adjust lower limit if upper < lower
            if upper < lower:
                if min_price <= upper <= max_price:
                    lower = upper
                    price_custom_entry_min.delete(0, tk.END)
                    price_custom_entry_min.insert(0, int(lower))
            price_slider["set"](lower, upper)
            # Update filter tags
            update_filter_tags()
            # Fetch and display stalls
            perform_search()
        except ValueError:
            pass

    price_custom_entry_min.bind("<KeyRelease>", debounce_price_entry)
    price_custom_entry_max.bind("<KeyRelease>", debounce_price_entry)

    # State Filter
    state_label = ctk.CTkLabel(filter_frame, text="State Filter", font=ctk.CTkFont(size=18, weight="bold"))
    state_label.grid(row=4, column=0, padx=20, pady=(20, 10))
    center_widget(state_label)

    state_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
    state_filter_container.grid(row=5, column=0, padx=20)
    center_widget(state_filter_container)

    state_filter_container.columnconfigure(0, weight=1)

    state_buttons_frame = ctk.CTkFrame(state_filter_container, fg_color="transparent")
    state_buttons_frame.grid(row=0, column=0)
    center_widget(state_buttons_frame)

    state_buttons_frame.columnconfigure(0, weight=1)

    for idx, state in enumerate(state_options):
        button = ctk.CTkButton(
            state_buttons_frame,
            text=state,
            font=ctk.CTkFont(size=16),
            fg_color=UNSELECTED_BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=180,  # Adjusted width to fit within filter frame
            height=40,
            text_color="white"
        )
        button.configure(command=partial(state_filter_button_click, state, button))
        button.grid(row=idx, column=0, pady=5)
        center_widget(button)
        # Store the button in state_buttons for reference
        state_buttons[state] = button

    # Availability Status Filter
    status_label = ctk.CTkLabel(filter_frame, text="Availability Filter", font=ctk.CTkFont(size=18, weight="bold"))
    status_label.grid(row=6, column=0, padx=20, pady=(20, 10))
    center_widget(status_label)

    status_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
    status_filter_container.grid(row=7, column=0, padx=20)
    center_widget(status_filter_container)

    status_filter_container.columnconfigure(0, weight=1)

    # Add status filter variables
    status_vars = {
        "Available": False,
        "Under Application": False,
        "Rented": False
    }
    status_buttons = {}

    status_buttons_frame = ctk.CTkFrame(status_filter_container, fg_color="transparent")
    status_buttons_frame.grid(row=0, column=0)
    center_widget(status_buttons_frame)

    status_buttons_frame.columnconfigure(0, weight=1)

    def status_filter_button_click(status, button):
        # Toggle the selection state
        status_vars[status] = not status_vars[status]
        if status_vars[status]:
            button.configure(fg_color=SELECTED_BUTTON_COLOR, text_color="black")
        else:
            button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    # Create buttons for each status
    for idx, status in enumerate(status_vars.keys()):
        button = ctk.CTkButton(
            status_buttons_frame,
            text=status,
            font=ctk.CTkFont(size=16),
            fg_color=UNSELECTED_BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=180,
            height=40,
            text_color="white"
        )
        button.configure(command=lambda s=status, b=button: status_filter_button_click(s, b))
        button.grid(row=idx, column=0, pady=5)
        center_widget(button)
        status_buttons[status] = button

    # Apply Filters Button (Now placed at the bottom of the filter frame)
    apply_filters_button = ctk.CTkButton(
        filter_frame,
        text="Apply Filters",
        font=ctk.CTkFont(size=18, weight="bold"),
        width=180,  # Adjusted width to fit within filter frame
        height=40,
        fg_color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
        command=perform_search
    )
    apply_filters_button.grid(row=8, column=0, pady=20)
    center_widget(apply_filters_button)

    # Search Result Label Frame
    search_result_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
    search_result_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0,10))

    # Search Result Label
    search_result_label = ctk.CTkLabel(
        search_result_frame,
        text="All stalls: X stalls found",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=TEXT_COLOR
    )
    search_result_label.pack(side="left", anchor="w")

    # Filter Tags Frame (now between search_result_frame and stall list)
    filter_tags_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
    filter_tags_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))

    # Ensure filter_tags_frame expands properly
    filter_tags_frame.columnconfigure(0, weight=1)

    # Function to update filter tags
    def update_filter_tags():
        # Clear existing tags
        for widget in filter_tags_frame.winfo_children():
            widget.destroy()

        # Size Filter Tag
        tags_present = False
        size_filter = size_filter_option.get()
        if size_filter != "all":
            tags_present = True
            if size_filter == "below_300":
                size_text = "Size: Below 300 sqft"
            elif size_filter == "300_600":
                size_text = "Size: 300 to 600 sqft"
            elif size_filter == "above_600":
                size_text = "Size: Above 600 sqft"
            elif size_filter == "custom":
                lower = size_custom_entry_min.get()
                upper = size_custom_entry_max.get()
                size_text = f"Size: {lower} to {upper} sqft"
            else:
                size_text = "Size: All"
            # Create size filter tag
            create_filter_tag(size_text, "size")

        # Price Filter Tag
        price_filter = price_filter_option.get()
        if price_filter != "all":
            tags_present = True
            if price_filter == "below_250":
                price_text = "Price: Below RM250"
            elif price_filter == "250_500":
                price_text = "Price: RM250 to RM500"
            elif price_filter == "above_500":
                price_text = "Price: Above RM500"
            elif price_filter == "custom":
                lower = price_custom_entry_min.get()
                upper = price_custom_entry_max.get()
                price_text = f"Price: RM{lower} to RM{upper}"
            else:
                price_text = "Price: All"
            # Create price filter tag
            create_filter_tag(price_text, "price")

        # State Filter Tags
        selected_states = [state for state, selected in state_vars.items() if selected]
        if selected_states:
            tags_present = True
            state_text = "States: " + ", ".join(selected_states)
            # Create state filter tag
            create_filter_tag(state_text, "state")

        # Status Filter Tags
        selected_statuses = [status for status, selected in status_vars.items() if selected]
        if selected_statuses:
            tags_present = True
            status_text = "Status: " + ", ".join(selected_statuses)
            # Create status filter tag
            create_filter_tag(status_text, "status")

        # Only display filter_tags_frame if there are tags
        if tags_present:
            filter_tags_frame.grid()
        else:
            filter_tags_frame.grid_remove()

    # Function to create filter tag
    def create_filter_tag(text, filter_type):
        tag_frame = ctk.CTkFrame(filter_tags_frame, fg_color=BUTTON_COLOR, corner_radius=15)
        tag_frame.pack(side="left", padx=5, pady=5)

        tag_label = ctk.CTkLabel(tag_frame, text=text, font=ctk.CTkFont(size=14), text_color="white")
        tag_label.pack(side="left", padx=(10, 5), pady=5)

        close_button = ctk.CTkButton(
            tag_frame,
            text="✕",
            width=20,
            height=20,
            fg_color="transparent",
            text_color="white",
            hover_color=BUTTON_HOVER_COLOR,
            font=ctk.CTkFont(size=14),
            command=lambda: remove_filter(filter_type)
        )
        close_button.pack(side="left", padx=(0, 5))

    # Function to remove filter
    def remove_filter(filter_type):
        global size_filter_selected_button, price_filter_selected_button
        if filter_type == "size":
            size_filter_option.set("all")
            if size_filter_selected_button is not None:
                size_filter_selected_button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
                size_filter_selected_button = None
            size_custom_controls_frame.grid_remove()
        elif filter_type == "price":
            price_filter_option.set("all")
            if price_filter_selected_button is not None:
                price_filter_selected_button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
                price_filter_selected_button = None
            price_custom_controls_frame.grid_remove()
        elif filter_type == "state":
            for state in state_vars:
                state_vars[state] = False
                # Update button appearance
                button = state_buttons.get(state)
                if button:
                    button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        elif filter_type == "status":
            for status in status_vars:
                status_vars[status] = False
                button = status_buttons.get(status)
                if button:
                    button.configure(fg_color=UNSELECTED_BUTTON_COLOR, text_color="white")
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    # Scrollable Frame for Stall List
    scrollable_frame = ctk.CTkScrollableFrame(
        results_frame,
        scrollbar_button_color="gray",
        fg_color=SECONDARY_COLOR
    )
    scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))

    # Ensure scrollable_frame expands properly
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.rowconfigure("all", weight=0)

    # Initially fetch and display all stalls
    num_stalls = fetch_and_display_stalls()
    stall_text = "stall" if num_stalls == 1 else "stalls"
    search_result_label.configure(text=f"All stalls: {num_stalls} {stall_text} found")
    update_filter_tags()

    # Run the application
    stall_frame.mainloop()

def main():
    root = ctk.CTk()
    root.title("Admin Manage Stall")
    root.geometry("1920x1080")
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Stall Management",
        command=lambda: show_admin_manage_stall(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()