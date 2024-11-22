from tkinter import filedialog
import customtkinter as ctk
import sqlite3
from PIL import  Image, ImageTk

# Initialize customtkinter appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_database():
    conn = sqlite3.connect("properties.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            sqft INTEGER,
            tenancy_period TEXT,
            price REAL,
            description TEXT,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_property():
    location = location_entry.get()
    sqft = sqft_entry.get()
    tenancy = tenancy_entry.get()
    price = price_entry.get()
    description = description_entry.get("1.0", ctk.END).strip()  # Get text from CTkTextbox widget
    image_path = image_label.image_path  # Get the image path from the label

    if not all([location, sqft, tenancy, price, description, image_path]):
        error_label.config(text="Please fill in all fields and upload an image.")
        return

    try:
        sqft = int(sqft)
        price = float(price)
    except ValueError:
        error_label.config(text="Sqft and price must be numbers.")
        return

    conn = sqlite3.connect("../../../PycharmProjects/ALL2/admin login 2 register/properties.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO properties (location, sqft, tenancy_period, price, description, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (location, sqft, tenancy, price, description, image_path),
    )
    conn.commit()
    conn.close()

    location_entry.delete(0, ctk.END)
    sqft_entry.delete(0, ctk.END)
    tenancy_entry.delete(0, ctk.END)
    price_entry.delete(0, ctk.END)
    description_entry.delete("1.0", ctk.END)
    image_label.config(image="", text="No Image Uploaded")
    image_label.image_path = ""
    error_label.config(text="")  # Clear error message

def upload_image():
    global image_label
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
    )
    if file_path:
        try:
            img = Image.open(file_path)
            img = img.resize((300, 200))  # Resize if needed
            photo = ImageTk.PhotoImage(img)
            image_label.config(image=photo, text="")
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.image_path = file_path  # Save the image path
        except Exception as e:
            print(f"Error loading image: {e}")
            error_label.config(text="Error loading image.")

# Create the main window using customtkinter
window = ctk.CTk()
window.title("Property Listing")

# Set window fullscreen size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width}x{screen_height}+0+0")

# Image display area
image_label = ctk.CTkLabel(window, text="No Image Uploaded", fg_color="lightgray", width=300, height=200)
image_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
image_label.image_path = ""  # Initialize image path

# Upload button
upload_button = ctk.CTkButton(window, text="Upload \u2191", command=upload_image)
upload_button.grid(row=4, column=0, padx=10, pady=(0, 10))

# Input fields
location_label = ctk.CTkLabel(window, text="Location:")
location_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
location_entry = ctk.CTkEntry(window)
location_entry.grid(row=1, column=1, padx=10, pady=10)

sqft_label = ctk.CTkLabel(window, text="Sqft:")
sqft_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
sqft_entry = ctk.CTkEntry(window)
sqft_entry.grid(row=1, column=2, padx=10, pady=10)

tenancy_label = ctk.CTkLabel(window, text="Tenancy period:")
tenancy_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")
tenancy_entry = ctk.CTkEntry(window)
tenancy_entry.grid(row=3, column=1, padx=10, pady=10)

price_label = ctk.CTkLabel(window, text="Price:")
price_label.grid(row=2, column=2, padx=10, pady=10, sticky="w")
price_entry = ctk.CTkEntry(window)
price_entry.grid(row=3, column=2, padx=10, pady=10)

description_label = ctk.CTkLabel(window, text="Description:")
description_label.grid(row=4, column=1, padx=10, pady=10, sticky="w")
description_entry = ctk.CTkTextbox(window, height=100, width=300)
description_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=10)

# Add button
add_button = ctk.CTkButton(window, text="ADD", fg_color="#b094f7", text_color="white", font=("Arial", 14), command=add_property)
add_button.grid(row=6, column=1, columnspan=2, pady=10)

# Error label
error_label = ctk.CTkLabel(window, text="", text_color="red")
error_label.grid(row=7, column=1, columnspan=2)

create_database()
window.mainloop()