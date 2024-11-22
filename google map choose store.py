import customtkinter as ctk
import sqlite3
from tkintermapview import TkinterMapView

# Connect to the stalls.db database (or create it if it doesn't exist)
conn = sqlite3.connect("stalls.db")
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    status INTEGER
)
""")
conn.commit()

# Check if 'status' column exists, if not, add it
cursor.execute("PRAGMA table_info(locations)")
columns = cursor.fetchall()
if not any(column[1] == 'status' for column in columns):
    cursor.execute("ALTER TABLE locations ADD COLUMN status INTEGER DEFAULT 1")
    conn.commit()


# Function to save a location to the database with a status
def save_location_to_db(lat, lon, status):
    cursor.execute("INSERT INTO locations (latitude, longitude, status) VALUES (?, ?, ?)", (lat, lon, status))
    conn.commit()


# Function to retrieve saved locations from the database
def load_locations_from_db():
    cursor.execute("SELECT latitude, longitude, status FROM locations")
    return cursor.fetchall()


# Function to remove a location from the database
def remove_location_from_db(lat, lon):
    cursor.execute("DELETE FROM locations WHERE latitude = ? AND longitude = ?", (lat, lon))
    conn.commit()


# Function to capture and place a marker on the map when the user clicks on the map
def on_click():
    lat, lon = map_widget.get_position()  # Get the current position
    print(f"Latitude: {lat}, Longitude: {lon}")

    # Ask the user for status (for demonstration purposes, this could be dynamic in a real app)
    status = int(input("Enter status (1 = green, 2 = yellow, 3 = orange, 4 = red): "))

    # Save the location to the database with the selected status
    save_location_to_db(lat, lon, status)

    # Determine marker color based on status
    marker_color = get_marker_color(status)

    # Add a marker at the clicked position with the selected color
    marker = map_widget.set_marker(lat, lon, text="Saved Location", marker_color_outside=marker_color)
    saved_locations.append((lat, lon, marker))  # Save the coordinates and marker to the list


# Function to remove the last saved location
def remove_last_location():
    if saved_locations:
        # Remove the last saved location from the map and list
        lat, lon, marker = saved_locations.pop()  # Get and remove the last location
        marker.delete()  # Remove the marker from the map

        # Remove the location from the database
        remove_location_from_db(lat, lon)

    else:
        print("No saved locations to remove.")


# Function to load saved locations from the database and place them on the map
def load_saved_locations():
    locations = load_locations_from_db()
    for lat, lon, status in locations:
        marker_color = get_marker_color(status)
        marker = map_widget.set_marker(lat, lon, text="Saved Location", marker_color_outside=marker_color)
        saved_locations.append((lat, lon, marker))


# Function to determine marker color based on status
def get_marker_color(status):
    if status == 1:
        return "green"
    elif status == 2:
        return "yellow"
    elif status == 3:
        return "orange"
    elif status == 4:
        return "red"
    else:
        return "blue"  # Default color if status is not valid


# Setup customTkinter appearance and theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

# Create the main window
root = ctk.CTk()
root.geometry("800x600")
root.title("World Map Location Selector")

# Create the map widget using TkinterMapView
map_widget = TkinterMapView(root, width=800, height=600)
map_widget.pack(fill="both", expand=True)

# Set the starting position for the map (centered on Malaysia)
map_widget.set_position(4.2105, 101.9758)  # Centered on Malaysia
map_widget.set_zoom(6)  # Zoom level for better focus on Malaysia

# Initialize a list to keep track of saved locations
saved_locations = []

# Load saved locations from the database and add them to the map
load_saved_locations()

# Binding the right-click event to capture the coordinates
map_widget.add_right_click_menu_command("Get Coordinates", on_click)
map_widget.add_right_click_menu_command("Remove Coordinates", remove_last_location)

# Running the customTkinter mainloop
root.mainloop()

# Close the database connection when the program ends
conn.close()
