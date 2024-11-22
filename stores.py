import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3


# Database functions

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("../../../PycharmProjects/ALL2/admin login 2 register/properties.db")
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
    return conn


def fetch_properties(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties")
    return cursor.fetchall()


def delete_property(conn, property_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id=?", (property_id,))
    conn.commit()


# Create the main window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Store")
root.geometry("800x600")

# Make the window fullscreen
root.attributes("-fullscreen", True)

# Create the add button
add_button = ctk.CTkButton(root, text="Add", command=lambda: print("Add button clicked"))
add_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

# Create the notebook
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")

# Create the frames for each tab
all_frame = ctk.CTkFrame(notebook)
draft_frame = ctk.CTkFrame(notebook)
archived_frame = ctk.CTkFrame(notebook)

# Add the frames to the notebook
notebook.add(all_frame, text="All")
notebook.add(draft_frame, text="Draft")
notebook.add(archived_frame, text="Archived")


# Function to create a treeview and filter
def create_treeview(frame):
    tree = ttk.Treeview(frame, columns=("ID", "Picture", "Actions"), show="headings", height=8)
    tree.column("ID", width=50)
    tree.column("Picture", width=200)
    tree.column("Actions", width=200)
    tree.heading("ID", text="ID")
    tree.heading("Picture", text="Picture")
    tree.heading("Actions", text="Actions")
    tree.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    filter_label = ctk.CTkLabel(frame, text="Filter:")
    filter_label.grid(row=0, column=0, sticky="w", padx=10)

    filter_entry = ctk.CTkEntry(frame, placeholder_text="Enter filter text")
    filter_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

    return tree, filter_entry


# Create the treeviews and filters
all_tree, all_filter = create_treeview(all_frame)
draft_tree, draft_filter = create_treeview(draft_frame)
archived_tree, archived_filter = create_treeview(archived_frame)


# Function to add a picture to the treeview
def add_picture(tree, property_data):
    property_id, location, sqft, start_date, end_date, price, description, image_path = property_data

    image = Image.open(image_path)
    image.thumbnail((100, 100))
    photo = ImageTk.PhotoImage(image)

    # Create action buttons with icons
    delete_button = ctk.CTkButton(tree, text="Delete", command=lambda: delete_property_action(property_id))
    edit_button = ctk.CTkButton(tree, text="Edit", command=lambda: edit_property_action(property_id))

    # Insert into tree
    tree.insert("", "end", values=(property_id, photo))


# Function to handle deletion of a property
def delete_property_action(property_id):
    conn = create_connection()
    delete_property(conn, property_id)
    conn.close()


# Refresh the treeview after deletion (optional)

# Function to handle editing of a property (placeholder for now)
def edit_property_action(property_id):
    print(f"Edit button clicked for ID: {property_id}")


# Load properties from database and add them to the treeviews
conn = create_connection()
if conn:
    properties = fetch_properties(conn)

    for property_data in properties:
        add_picture(all_tree, property_data)

conn.close()

# Configure rows and columns to expand properly
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()