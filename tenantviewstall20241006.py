import customtkinter as ctk
import tkinter as tk
import sqlite3
from PIL import Image, ImageTk
from functools import partial
import os
import logging
import sys
import subprocess
import tkinter.messagebox as messagebox

# Initialize the main window
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Add this near the top of the file, after imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update how we get the tenant_id from command line arguments
tenant_id = None
if len(sys.argv) > 2:
    if sys.argv[1] == '--tenant_id':
        try:
            tenant_id = int(sys.argv[2])
        except ValueError:
            print("Invalid tenant ID provided")
    elif sys.argv[1] == '--user_data':
        # Handle user data format if passed
        try:
            import ast
            user_data = ast.literal_eval(sys.argv[2])
            tenant_id = user_data.get('tenantID')
        except Exception as e:
            print(f"Error parsing user data: {e}")

def check_tenant_rental_status(tenant_id):
    """Check if tenant has any approved or pending rentals"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rentalID, isApprove 
            FROM rental 
            WHERE tenantID = ? AND (isApprove = 1 OR isApprove = 0)
        """, (tenant_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
        
    except sqlite3.Error as e:
        logger.error(f"Database error checking rental status: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking rental status: {e}")
        return False

def open_viewstall_window():
    # Check if tenant_id was provided
    if tenant_id is None:
        logger.error("No tenant ID provided")
        messagebox.showerror("Error", "No tenant ID provided")
        return
        
    # Check rental status
    if check_tenant_rental_status(tenant_id):
        messagebox.showwarning(
            "Access Denied", 
            "You already have an active or pending rental application. You cannot apply for another stall."
        )
        return
        
    verify_image_paths()
    
    app = ctk.CTk()
    app.geometry("1920x1080")
    app.title("View Stall")
    app.attributes("-fullscreen", True)

    # Define custom colors
    PRIMARY_COLOR = "#E7D7C7"  # Light beige (background color)
    SECONDARY_COLOR = "#E7D7C7"  # Light beige (same as primary for consistency)
    BUTTON_COLOR = "#A29086"  # Gray color (like the back button)
    BUTTON_HOVER_COLOR = "#8B7355"  # Darker gray for hover
    SELECTED_BUTTON_COLOR = "#8B7355"  # Darker gray for selected filter buttons
    UNSELECTED_BUTTON_COLOR = "#A29086"  # Gray for unselected buttons
    TEXT_COLOR = "#654633"  # Dark brown for text

    # Global variables
    global image_refs, size_filter_option, price_filter_option
    image_refs = []
    size_filter_option = tk.StringVar(value="all")
    price_filter_option = tk.StringVar(value="all")

    # Variables for filters
    global size_filter_selected_button, price_filter_selected_button
    size_filter_selected_button = None
    price_filter_selected_button = None

    # Function to handle Show Details button click
    def show_details(stall_id):
        app.destroy()  # Close the view stall window
        subprocess.Popen([sys.executable, 'rentalapplication20241013.py', str(tenant_id), str(stall_id)])

    # Function to get min and max size
    def get_size_range():
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(sqft), MAX(sqft) FROM combined_properties")
        min_size, max_size = cursor.fetchone()
        conn.close()

        # Ensure we have valid numeric values
        min_size = float(min_size) if min_size is not None else 0
        max_size = float(max_size) if max_size is not None else 1000

        # If min and max are the same, create a small range around that value
        if min_size == max_size:
            min_size = max(0, min_size - 10)  # Ensure min_size doesn't go below 0
            max_size = max_size + 10

        return min_size, max_size

    # Function to get min and max price
    def get_price_range():
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(price), MAX(price) FROM combined_properties")
        min_price, max_price = cursor.fetchone()
        conn.close()

        # Ensure we have valid numeric values
        min_price = float(min_price) if min_price is not None else 0
        max_price = float(max_price) if max_price is not None else 1000

        # If min and max are the same, create a small range around that value
        if min_price == max_price:
            min_price = max(0, min_price - 10)  # Ensure min_price doesn't go below 0
            max_price = max_price + 10

        return min_price, max_price

    # Get min and max values for size and price
    min_size, max_size = get_size_range()
    min_price, max_price = get_price_range()

    # Create Header
    header_frame = ctk.CTkFrame(app, height=100, fg_color=PRIMARY_COLOR)
    header_frame.pack(fill="x")

    # Back Button - moved to top left
    back_button = ctk.CTkButton(
        header_frame,
        text="Back",
        font=ctk.CTkFont(size=18, weight="bold"),
        width=150,
        height=50,
        fg_color=BUTTON_COLOR,  # Gray color
        hover_color=BUTTON_HOVER_COLOR,  # Darker gray
        text_color="white",
        command=app.destroy
    )
    back_button.place(x=20, y=10)  # Position button at top left corner

    header_label = ctk.CTkLabel(
        header_frame,
        text="View Stall",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color=TEXT_COLOR  # Dark brown text
    )
    header_label.pack(pady=30)

    # Create Main Frame
    main_frame = ctk.CTkFrame(app, fg_color=PRIMARY_COLOR)  # Light beige background
    main_frame.pack(fill="both", expand=True)

    # Create Search Bar Frame
    search_frame = ctk.CTkFrame(main_frame, fg_color=PRIMARY_COLOR, corner_radius=10)
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

    def perform_search():
        global size_filter_option, price_filter_option
        query = search_entry.get().strip()
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

    # Function to fetch and display stalls
    def fetch_and_display_stalls(search_query="", size_filter="all", price_filter="all"):
        # Connect to the SQLite database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Build the SQL query with filters and JOIN to exclude stalls that are in rental applications
        query = """
            SELECT DISTINCT cp.* 
            FROM combined_properties cp
            WHERE cp.id NOT IN (
                SELECT combined_properties_id 
                FROM rental 
                WHERE isApprove = 1 OR isApprove = 0
            )
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
                query += " AND cp.sqft < ?"
                params.append(300)
            elif size_filter == "300_600":
                query += " AND cp.sqft BETWEEN ? AND ?"
                params.extend([300, 600])
            elif size_filter == "above_600":
                query += " AND cp.sqft > ?"
                params.append(600)
            elif size_filter == "custom":
                try:
                    lower = float(size_custom_entry_min.get())
                    upper = float(size_custom_entry_max.get())
                    query += " AND cp.sqft BETWEEN ? AND ?"
                    params.extend([lower, upper])
                except ValueError:
                    print("Invalid custom size values")
                    return 0

        # Price filter
        if price_filter != "all":
            if price_filter == "below_250":
                query += " AND cp.price < ?"
                params.append(250)
            elif price_filter == "250_500":
                query += " AND cp.price BETWEEN ? AND ?"
                params.extend([250, 500])
            elif price_filter == "above_500":
                query += " AND cp.price > ?"
                params.append(500)
            elif price_filter == "custom":
                try:
                    lower = float(price_custom_entry_min.get())
                    upper = float(price_custom_entry_max.get())
                    query += " AND cp.price BETWEEN ? AND ?"
                    params.extend([lower, upper])
                except ValueError:
                    print("Invalid custom price values")
                    return 0

        # State filter
        selected_states = [state for state, selected in state_vars.items() if selected]
        if selected_states:
            placeholders = ','.join('?' for _ in selected_states)
            query += f" AND cp.state IN ({placeholders})"
            params.extend(selected_states)

        cursor.execute(query, params)
        stalls = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Clear image references
        global image_refs
        image_refs.clear()

        # Number of stalls found
        num_stalls = len(stalls)

        # If no stalls found, display a message
        if not stalls:
            no_result_label = ctk.CTkLabel(
                scrollable_frame,
                text="No stalls found matching your search and filter criteria.",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="gray"
            )
            no_result_label.pack(pady=20)
            return 0

        # Iterate over each stall and display its details
        for stall in stalls:
            # Create a dictionary to store stall details
            stall_details = {
                'stall_id': stall[0],  # Assuming stall_id is always the first column
                'city': '',
                'sqft': 0,
                'state': '',
                'price': 0,
                'description': '',
                'image_path': '',
                'addressLine1': '',
                'addressLine2': '',
                'postcode': ''
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
                image_path = stall_details['image_path']
                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"Image not found for stall {stall_details['stall_id']}: {image_path}")
                    raise FileNotFoundError
                
                image = Image.open(image_path)
                new_size = (int(250 * 1.25), int(180 * 1.25))  # Increased by 1.25x
                image = image.resize(new_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = ctk.CTkLabel(stall_inner_frame, image=photo, text="")
                image_label.image = photo  # Keep a reference
                image_label.pack(side="left", padx=10)
                image_refs.append(photo)  # Keep a reference to prevent garbage collection
                
            except (FileNotFoundError, OSError, AttributeError) as e:
                logger.error(f"Error loading image for stall ID {stall_details['stall_id']}: {e}")
                # Create a more visually appealing placeholder
                placeholder_frame = ctk.CTkFrame(
                    stall_inner_frame,
                    width=int(250 * 1.25),
                    height=int(180 * 1.25),
                    fg_color="#E0E0E0",  # Light gray background
                    corner_radius=10
                )
                placeholder_frame.pack(side="left", padx=10)
                placeholder_frame.pack_propagate(False)  # Maintain size
                
                placeholder_text = ctk.CTkLabel(
                    placeholder_frame,
                    text="No Image\nAvailable",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color="#757575",  # Darker gray text
                    justify="center"
                )
                placeholder_text.place(relx=0.5, rely=0.5, anchor="center")

            # Create a frame for the details to allow individual label spacing
            details_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
            details_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)

            # Title: addressLine1 - addressLine2
            title_text = f"{stall_details['addressLine1']} - {stall_details['addressLine2']}"
            title_label = ctk.CTkLabel(
                details_frame,
                text=title_text,
                font=ctk.CTkFont(size=32, weight="bold"),  # Increased size
                text_color=TEXT_COLOR,
                justify="left",
                anchor="w",
                wraplength=800
            )
            title_label.pack(anchor="w", pady=(0, 5))

            # Subtitle: city only
            subtitle_label = ctk.CTkLabel(
                details_frame,
                text=f"{stall_details['city']}",
                font=ctk.CTkFont(size=22),
                text_color=TEXT_COLOR,
                justify="left",
                anchor="w"
            )
            subtitle_label.pack(anchor="w", pady=(0, 10))

            # Description
            description_label = ctk.CTkLabel(
                details_frame,
                text=f"{stall_details['description']}",
                font=ctk.CTkFont(size=18),
                text_color=TEXT_COLOR,
                justify="left",
                anchor="w",
                wraplength=600
            )
            description_label.pack(anchor="w", fill="x")

            # Add empty space to push size, price, and button to the bottom
            details_frame.pack_propagate(False)
            details_frame.configure(height=200)  # Adjust as needed to ensure alignment

            # Create a frame for the size, price, and button, aligned to bottom right
            action_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=10, pady=10, anchor="se")

            # Add empty space to push content to the bottom
            spacer_label = ctk.CTkLabel(action_frame, text="")
            spacer_label.pack(expand=True)

            # Size, Price, and Button Frame
            spb_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
            spb_frame.pack(anchor="center")

            # Size Label
            size_label = ctk.CTkLabel(
                spb_frame,
                text=f"{stall_details['sqft']} sqft",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=TEXT_COLOR
            )
            size_label.pack(anchor="center", pady=(0, 5))

            # Price Label
            price_label = ctk.CTkLabel(
                spb_frame,
                text=f"RM {stall_details['price']:.2f}",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=TEXT_COLOR
            )
            price_label.pack(anchor="center", pady=(0, 5))

            # Show Details Button
            show_details_button = ctk.CTkButton(
                spb_frame,
                text="Apply Stall",
                width=150,
                height=50,
                fg_color=BUTTON_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                font=ctk.CTkFont(size=20, weight="bold"),
                command=lambda id=stall_details['stall_id']: show_details(id)
            )
            show_details_button.pack(anchor="center", pady=(0, 5))

        return num_stalls  # Return the number of stalls found

    # Create a frame for the content below the search bar
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill="both", expand=True)

    # Configure grid for content_frame
    content_frame.columnconfigure(0, weight=0)  # Fixed width for filter frame
    content_frame.columnconfigure(1, weight=1)  # Remaining space for results frame
    content_frame.rowconfigure(0, weight=1)

    # Create the filter frame container with fixed width
    filter_frame_container = ctk.CTkFrame(content_frame, fg_color=PRIMARY_COLOR, corner_radius=10, width=250)
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

    size_slider = create_range_slider(size_custom_controls_frame, from_=min_size, to=max_size, width=160,
                                      command=size_slider_callback)
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

    price_slider = create_range_slider(price_custom_controls_frame, from_=min_price, to=max_price, width=160,
                                       command=price_slider_callback)
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
    apply_filters_button.grid(row=6, column=0, pady=20)
    center_widget(apply_filters_button)

    # Search Result Label Frame
    search_result_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
    search_result_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))

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
    filter_tags_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

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
        # Update filter tags
        update_filter_tags()
        # Fetch and display stalls
        perform_search()

    # Scrollable Frame for Stall List
    scrollable_frame = ctk.CTkScrollableFrame(
        results_frame,
        scrollbar_button_color="gray",
        fg_color=PRIMARY_COLOR
    )
    scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Ensure scrollable_frame expands properly
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.rowconfigure("all", weight=0)

    # Initially fetch and display all stalls
    num_stalls = fetch_and_display_stalls()
    stall_text = "stall" if num_stalls == 1 else "stalls"
    search_result_label.configure(text=f"All stalls: {num_stalls} {stall_text} found")
    update_filter_tags()

    # Run the application
    app.mainloop()

def verify_image_paths():
    """Verify all image paths in the database and log any issues."""
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, image_path FROM combined_properties")
    results = cursor.fetchall()
    
    invalid_paths = []
    for stall_id, image_path in results:
        if not image_path or not os.path.exists(image_path):
            invalid_paths.append((stall_id, image_path))
            logger.warning(f"Invalid image path for stall {stall_id}: {image_path}")
    
    conn.close()
    
    if invalid_paths:
        logger.error(f"Found {len(invalid_paths)} stalls with invalid image paths")
    else:
        logger.info("All image paths verified successfully")
    
    return invalid_paths

def test_image_path(image_path):
    """Test if an image path is valid and can be loaded."""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            return False
            
        image = Image.open(image_path)
        image.verify()  # Verify it's a valid image file
        logger.info(f"Successfully verified image: {image_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error testing image {image_path}: {e}")
        return False

if __name__ == "__main__":
    open_viewstall_window()