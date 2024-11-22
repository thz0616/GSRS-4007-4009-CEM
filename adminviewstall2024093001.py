import customtkinter as ctk
import tkinter as tk
import sqlite3
from PIL import Image, ImageTk
from functools import partial

# Initialize the main window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1920x1080")
app.title("Manage Stall")

# Define custom colors
PRIMARY_COLOR = "#B39DDB"       # Light Purple
SECONDARY_COLOR = "#E1BEE7"     # Lighter Purple
BUTTON_COLOR = "#9575CD"        # Medium Purple for Edit
BUTTON_HOVER_COLOR = "#7E57C2"  # Darker Purple for Edit Hover
SELECTED_BUTTON_COLOR = "#FFC107"  # Amber color for selected filter buttons
UNSELECTED_BUTTON_COLOR = "#9575CD"  # Medium purple (same as BUTTON_COLOR)

# Function to handle Delete button click
def delete_stall(stall_id):
    print(f"Stall {stall_id} deleted")

# Function to handle Edit button click
def edit_stall(stall_id):
    print(f"Stall {stall_id} edit window open")

# Function to get min and max size
def get_size_range():
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(sqft), MAX(sqft) FROM properties")
    min_size, max_size = cursor.fetchone()
    conn.close()
    return min_size if min_size else 0, max_size if max_size else 1000

# Function to get min and max price
def get_price_range():
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(price), MAX(price) FROM properties")
    min_price, max_price = cursor.fetchone()
    conn.close()
    return min_price if min_price else 0, max_price if max_price else 1000

# Get min and max values for size and price
min_size, max_size = get_size_range()
min_price, max_price = get_price_range()

# Create Header
header_frame = ctk.CTkFrame(app, height=100, fg_color=PRIMARY_COLOR)
header_frame.pack(fill="x")

header_label = ctk.CTkLabel(
    header_frame,
    text="Manage Stall",
    font=ctk.CTkFont(size=36, weight="bold"),
    text_color="white"
)
header_label.pack(pady=30)

# Create Main Frame
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)

# Create Search Bar Frame
search_frame = ctk.CTkFrame(main_frame, fg_color=SECONDARY_COLOR, corner_radius=10)
search_frame.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

# Search Entry
search_entry = ctk.CTkEntry(
    search_frame,
    placeholder_text="Search by Location...",
    font=ctk.CTkFont(size=18),
    width=600,
    height=50
)
search_entry.pack(side="left", padx=(20, 10), pady=10, expand=True, fill="x")

# Search Button
search_button = ctk.CTkButton(
    search_frame,
    text="Search",
    font=ctk.CTkFont(size=18, weight="bold"),
    width=150,
    height=50,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_HOVER_COLOR,
    command=lambda: [perform_search()]
)
search_button.pack(side="left", padx=(10, 10), pady=10)

# Filter Button
filter_button = ctk.CTkButton(
    search_frame,
    text="Filter",
    font=ctk.CTkFont(size=18, weight="bold"),
    width=150,
    height=50,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_HOVER_COLOR,
    command=lambda: [toggle_filter()]
)
filter_button.pack(side="left", padx=(10, 20), pady=10)

# Variables for filters
size_filter_option = tk.StringVar(value="all")
price_filter_option = tk.StringVar(value="all")
size_filter_selected_button = None
price_filter_selected_button = None
filter_frame_visible = False

# To keep a reference to images to prevent garbage collection
image_refs = []

# Debounce timers
size_entry_timer = None
price_entry_timer = None

# Function to perform search and filter
def perform_search():
    query = search_entry.get().strip()
    # Use global variables for filters
    global size_filter_option, price_filter_option
    # Clear the current stall list
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    # Fetch and display stalls based on the search query and filters
    fetch_and_display_stalls(query, size_filter_option.get(), price_filter_option.get())

# Function to open or close the filter GUI
def toggle_filter():
    global filter_frame_visible
    if not filter_frame_visible:
        show_filter_frame()
    else:
        hide_filter_frame()

def show_filter_frame():
    global filter_frame_visible
    filter_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
    filter_frame_visible = True

def hide_filter_frame():
    global filter_frame_visible
    filter_frame.grid_forget()
    filter_frame_visible = False

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
        size_custom_controls_frame.pack(side="left", padx=5)
    else:
        size_custom_controls_frame.pack_forget()

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
        price_custom_controls_frame.pack(side="left", padx=5)
    else:
        price_custom_controls_frame.pack_forget()

# Function to fetch and display stalls
def fetch_and_display_stalls(search_query="", size_filter="all", price_filter="all"):
    # Connect to the SQLite database
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()

    # Build the SQL query with filters
    query = "SELECT * FROM properties WHERE 1=1"
    params = []

    # Search query
    if search_query:
        query += " AND location LIKE ?"
        params.append('%' + search_query + '%')

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
                return

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
                return

    cursor.execute(query, params)
    stalls = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Clear image references
    global image_refs
    image_refs.clear()

    # If no stalls found, display a message
    if not stalls:
        no_result_label = ctk.CTkLabel(
            scrollable_frame,
            text="No stalls found matching your search and filter criteria.",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="gray"
        )
        no_result_label.pack(pady=20)
        return

    # Iterate over each stall and display its details
    for stall in stalls:
        stall_id, location, sqft, start_date, end_date, price, description, image_path = stall

        # Create a frame for each stall with enhanced styling
        stall_frame = ctk.CTkFrame(
            scrollable_frame,
            corner_radius=10,
            fg_color="white",
            border_width=2,
            border_color=PRIMARY_COLOR
        )
        stall_frame.pack(pady=15, padx=10, fill="x")

        # Create a horizontal layout within the stall_frame
        stall_inner_frame = ctk.CTkFrame(stall_frame, fg_color="transparent")
        stall_inner_frame.pack(fill="x", padx=20, pady=20)

        # Load and display the stall image with 1.25x scaling
        try:
            image = Image.open(image_path)
            new_size = (int(300 * 1.25), int(200 * 1.25))  # (375, 250)
            image = image.resize(new_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label = ctk.CTkLabel(stall_inner_frame, image=photo, text="")
            image_label.image = photo  # Keep a reference
            image_label.pack(side="left", padx=20)
            image_refs.append(photo)  # Keep a reference to prevent garbage collection
        except Exception as e:
            print(f"Error loading image for stall ID {stall_id}: {e}")
            # Display a placeholder if image fails to load
            placeholder = ctk.CTkLabel(
                stall_inner_frame,
                text="No Image Available",
                width=int(300 * 1.25),
                height=int(200 * 1.25),
                fg_color="gray",
                text_color="white",
                justify="center",
                corner_radius=10,
                font=ctk.CTkFont(size=20, weight="bold")
            )
            placeholder.pack(side="left", padx=20)

        # Create a frame for the details to allow individual label spacing
        details_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
        details_frame.pack(side="left", padx=30, pady=10)

        # Define each detail as a separate label
        detail_fields = [
            f"Location: {location}",
            f"Size: {sqft} sqft",
            f"Available from: {start_date} to {end_date}",
            f"Price: RM {price:.2f}",
            f"Description: {description}"
        ]

        for field in detail_fields:
            detail_label = ctk.CTkLabel(
                details_frame,
                text=field,
                justify="left",
                anchor="w",
                font=ctk.CTkFont(size=20),
                wraplength=900
            )
            detail_label.pack(anchor="w", pady=(0, 5))

        # Create a frame for buttons
        button_frame = ctk.CTkFrame(stall_inner_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=30)

        # Edit Button with enhanced styling
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit",
            width=150,
            height=50,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=lambda id=stall_id: edit_stall(id)
        )
        edit_button.pack(pady=15)

        # Delete Button with enhanced styling
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            fg_color="red",
            hover_color="#CC0000",
            width=150,
            height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=lambda id=stall_id: delete_stall(id)
        )
        delete_button.pack(pady=15)

# Create the filter frame (initially not gridded)
filter_frame = ctk.CTkFrame(main_frame, fg_color=SECONDARY_COLOR, corner_radius=10)

# Size Filter
size_label = ctk.CTkLabel(filter_frame, text="Size Filter", font=ctk.CTkFont(size=18, weight="bold"))
size_label.pack(pady=(20, 10), anchor="w", padx=20)

size_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
size_filter_container.pack(anchor="w", padx=20)

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
size_buttons_frame.pack(side="left", pady=10)

size_custom_controls_frame = ctk.CTkFrame(size_filter_container, fg_color="transparent")
# Initially not packed

for text, value in size_options:
    button = ctk.CTkButton(
        size_buttons_frame,
        text=text,
        font=ctk.CTkFont(size=16),
        fg_color=UNSELECTED_BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
        width=150,
        height=40,
        text_color="white"
    )
    button.configure(command=partial(size_filter_button_click, value, button))
    button.pack(side="left", padx=5)

# Size Custom Controls
# Custom Range Slider without OOP
def create_range_slider(master, from_, to, width, command):
    canvas = tk.Canvas(master, width=width, height=30, bg=SECONDARY_COLOR, highlightthickness=0)
    canvas.pack()

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

size_slider = create_range_slider(size_custom_controls_frame, from_=min_size, to=max_size, width=300, command=size_slider_callback)
size_slider["set"](min_size, max_size)

# Entry Boxes
size_custom_entry_min = ctk.CTkEntry(size_custom_controls_frame, width=70, font=ctk.CTkFont(size=16))
size_custom_entry_min.pack(side="left", padx=5)
size_custom_entry_min.insert(0, int(min_size))

size_to_label = ctk.CTkLabel(size_custom_controls_frame, text=" to ", font=ctk.CTkFont(size=16))
size_to_label.pack(side="left")

size_custom_entry_max = ctk.CTkEntry(size_custom_controls_frame, width=70, font=ctk.CTkFont(size=16))
size_custom_entry_max.pack(side="left", padx=5)
size_custom_entry_max.insert(0, int(max_size))

size_unit_label = ctk.CTkLabel(size_custom_controls_frame, text=" sqft", font=ctk.CTkFont(size=16))
size_unit_label.pack(side="left")

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
    except ValueError:
        pass

size_custom_entry_min.bind("<KeyRelease>", debounce_size_entry)
size_custom_entry_max.bind("<KeyRelease>", debounce_size_entry)

# Price Filter
price_label = ctk.CTkLabel(filter_frame, text="Price Filter", font=ctk.CTkFont(size=18, weight="bold"))
price_label.pack(pady=(20, 10), anchor="w", padx=20)

price_filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
price_filter_container.pack(anchor="w", padx=20)

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
price_buttons_frame.pack(side="left", pady=10)

price_custom_controls_frame = ctk.CTkFrame(price_filter_container, fg_color="transparent")
# Initially not packed

for text, value in price_options:
    button = ctk.CTkButton(
        price_buttons_frame,
        text=text,
        font=ctk.CTkFont(size=16),
        fg_color=UNSELECTED_BUTTON_COLOR,
        hover_color=BUTTON_HOVER_COLOR,
        width=150,
        height=40,
        text_color="white"
    )
    button.configure(command=partial(price_filter_button_click, value, button))
    button.pack(side="left", padx=5)

# Price Custom Controls
def price_slider_callback(value):
    lower, upper = value
    price_custom_entry_min.delete(0, tk.END)
    price_custom_entry_min.insert(0, int(lower))
    price_custom_entry_max.delete(0, tk.END)
    price_custom_entry_max.insert(0, int(upper))

price_slider = create_range_slider(price_custom_controls_frame, from_=min_price, to=max_price, width=300, command=price_slider_callback)
price_slider["set"](min_price, max_price)

# Entry Boxes with RM Prefix
price_rm_label_min = ctk.CTkLabel(price_custom_controls_frame, text="RM ", font=ctk.CTkFont(size=16))
price_rm_label_min.pack(side="left")

price_custom_entry_min = ctk.CTkEntry(price_custom_controls_frame, width=70, font=ctk.CTkFont(size=16))
price_custom_entry_min.pack(side="left", padx=5)
price_custom_entry_min.insert(0, int(min_price))

price_to_label = ctk.CTkLabel(price_custom_controls_frame, text=" to ", font=ctk.CTkFont(size=16))
price_to_label.pack(side="left")

price_rm_label_max = ctk.CTkLabel(price_custom_controls_frame, text="RM ", font=ctk.CTkFont(size=16))
price_rm_label_max.pack(side="left")

price_custom_entry_max = ctk.CTkEntry(price_custom_controls_frame, width=70, font=ctk.CTkFont(size=16))
price_custom_entry_max.pack(side="left", padx=5)
price_custom_entry_max.insert(0, int(max_price))

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
    except ValueError:
        pass

price_custom_entry_min.bind("<KeyRelease>", debounce_price_entry)
price_custom_entry_max.bind("<KeyRelease>", debounce_price_entry)

# Apply and Cancel Buttons
buttons_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
buttons_frame.pack(pady=20)

apply_button = ctk.CTkButton(
    buttons_frame,
    text="Apply Filters",
    font=ctk.CTkFont(size=18, weight="bold"),
    width=150,
    height=40,
    fg_color=BUTTON_COLOR,
    hover_color=BUTTON_HOVER_COLOR,
    command=lambda: [perform_search(), hide_filter_frame()]
)
apply_button.pack(side="left", padx=10)

cancel_button = ctk.CTkButton(
    buttons_frame,
    text="Cancel",
    font=ctk.CTkFont(size=18, weight="bold"),
    width=150,
    height=40,
    fg_color="gray",
    hover_color="#A9A9A9",
    command=hide_filter_frame
)
cancel_button.pack(side="left", padx=10)

# Create a scrollable frame
scrollable_frame = ctk.CTkScrollableFrame(
    main_frame,
    width=1900,
    height=800,
    scrollbar_button_color="gray",
    fg_color=SECONDARY_COLOR
)
scrollable_frame.grid(row=2, column=0, pady=20, padx=10, sticky="nsew")

# Configure grid weights
main_frame.rowconfigure(2, weight=1)
main_frame.columnconfigure(0, weight=1)

# Initially fetch and display all stalls
fetch_and_display_stalls()

# Run the application
app.mainloop()
