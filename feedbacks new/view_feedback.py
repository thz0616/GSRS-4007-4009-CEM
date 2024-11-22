import customtkinter as ctk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk

# Color constants
PURPLE_THEME = {
    "primary": "#9370DB",    # Medium purple
    
    "secondary": "#E6E6FA",  # Lavender
    "text": "#4B0082",      # Indigo
    "background": "#F8F7FF", # Very light purple
    "button": "#9370DB",    # Medium purple
    "delete": "#FF69B4"     # Light pink
}

def get_feedback_from_db():
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, category, comment, timestamp 
            FROM feedback 
            ORDER BY timestamp DESC
        """)
        feedback_data = []
        for row in cursor.fetchall():
            feedback_data.append({
                "tenant_id": f"T{row[0]:03d}",  # Creates IDs like T001, T002, etc.
                "category": row[1],
                "comments": row[2],  # We keep this as "comments" in the dict for compatibility
                "timestamp": row[3]
            })
        conn.close()
        return feedback_data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def create_feedback_box(container, feedback_data):
    box_frame = ctk.CTkFrame(container, fg_color=PURPLE_THEME["secondary"], corner_radius=15)
    box_frame.pack(pady=10, padx=20, fill="x")

    header_frame = ctk.CTkFrame(box_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(10, 5))
    
    tenant_label = ctk.CTkLabel(header_frame, 
                               text=f"Tenant ID: {feedback_data['tenant_id']}", 
                               font=("Arial", 16, "bold"),
                               text_color=PURPLE_THEME["text"])
    tenant_label.pack(side="left")
    
    category_label = ctk.CTkLabel(header_frame, 
                                 text=feedback_data['category'],
                                 font=("Arial", 14),
                                 text_color=PURPLE_THEME["text"])
    category_label.pack(side="right")

    comments_label = ctk.CTkLabel(box_frame, 
                                 text=feedback_data['comments'],
                                 wraplength=600,
                                 text_color=PURPLE_THEME["text"])
    comments_label.pack(fill="x", padx=20, pady=5)

    footer_frame = ctk.CTkFrame(box_frame, fg_color="transparent")
    footer_frame.pack(fill="x", padx=20, pady=(5, 10))
    
    timestamp_label = ctk.CTkLabel(footer_frame, 
                                  text=feedback_data['timestamp'],
                                  font=("Arial", 12),
                                  text_color=PURPLE_THEME["text"])
    timestamp_label.pack(side="left")

def filter_feedback():
    # Clear existing feedback boxes
    for widget in container.winfo_children():
        widget.destroy()
    
    selected_type = complaint_type_combo.get()
    search_text = search_entry.get().lower()
    
    all_feedback = get_feedback_from_db()
    filtered_feedback = [
        feedback for feedback in all_feedback
        if (selected_type == "All" or feedback["category"] == selected_type) and
        (not search_text or search_text in feedback["tenant_id"].lower())
    ]
    
    for feedback in filtered_feedback:
        create_feedback_box(container, feedback)

# Initialize CustomTkinter settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Create main window
root = ctk.CTk()
root.title("Feedback View")
root.geometry("800x600")
root.attributes("-fullscreen", True)

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Background setup
background_image_path = "C:/Users/tanji/OneDrive/Desktop/fedbacks/WhatsApp Image 2024-11-07 at 13.22.23_2a26c100.jpg"
background_image = Image.open(background_image_path)
background_image = background_image.resize((screen_width, screen_height), Image.LANCZOS)
background_photo = ctk.CTkImage(light_image=background_image, 
                               dark_image=background_image,
                               size=(screen_width, screen_height))

background_label = ctk.CTkLabel(root, image=background_photo, text="")
background_label.place(relwidth=1, relheight=1)

# Title
title_label = ctk.CTkLabel(root, text="Feedback", 
                          font=("Gothic", 64, "bold"), 
                          text_color=PURPLE_THEME["text"])
title_label.place(relx=0.5, rely=0.1, anchor="center")

# Complaint type combo
COMPLAINT_TYPES = ["All", "Complain", "Feature Request", "Payment Issue", "System Issue"]
complaint_type_combo = ttk.Combobox(root, values=COMPLAINT_TYPES, 
                                   state="readonly", font=("Arial", 12))
complaint_type_combo.set("All")
complaint_type_combo.place(relx=0.2, rely=0.2, relwidth=0.15, height=40, anchor="center")

# Search entry
search_entry = ctk.CTkEntry(root, 
                           placeholder_text="Search by Tenant ID...", 
                           border_width=0,
                           text_color=PURPLE_THEME["text"],
                           fg_color="white",
                           height=40,
                           font=("Arial", 12))
search_entry.place(relx=0.5, rely=0.2, relwidth=0.4, anchor="center")

# Search button
search_button = ctk.CTkButton(root, 
                             text="Search", 
                             fg_color=PURPLE_THEME["button"],
                             height=40,
                             width=120,
                             font=("Arial", 20, "bold"),
                             command=filter_feedback)
search_button.place(relx=0.75, rely=0.2, anchor="center")

# Container for feedback boxes
container = ctk.CTkScrollableFrame(root, fg_color="transparent")
container.place(relx=0.5, rely=0.3, relwidth=0.8, relheight=0.65, anchor="n")

# Bind events
complaint_type_combo.bind("<<ComboboxSelected>>", lambda e: filter_feedback())

# Load initial feedback
initial_feedback = get_feedback_from_db()
for feedback in initial_feedback:
    create_feedback_box(container, feedback)

# Run the application
root.mainloop()
