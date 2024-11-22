import customtkinter as ctk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk

# Color constants
PURPLE_THEME = {
    "primary": "#9370DB",    # Medium purple
    "secondary": "#E6E6FA",  # Lavender
    "text": "#4B0082",      # Indigo
    "background": "#F0E6FF", # Changed to match other pages
    "button": "#9370DB",    # Medium purple
    "delete": "#FF69B4"     # Light pink
}

def get_feedback_from_db():
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, f.category, f.comment, f.timestamp, r.stallName 
            FROM feedback f
            LEFT JOIN rental r ON f.rentalID = r.rentalID 
            ORDER BY f.timestamp DESC
        """)
        feedback_data = []
        for row in cursor.fetchall():
            feedback_data.append({
                "id": row[0],
                "category": row[1],
                "comments": row[2],
                "timestamp": row[3],
                "stall_name": row[4] if row[4] else "Unknown Stall"  # Fallback if no stall name
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
    
    stall_label = ctk.CTkLabel(header_frame, 
                              text=f"Stall: {feedback_data['stall_name']}", 
                              font=("Arial", 20, "bold"),  # Increased font size
                              text_color=PURPLE_THEME["text"])
    stall_label.pack(side="left")
    
    category_label = ctk.CTkLabel(header_frame, 
                                 text=feedback_data['category'],
                                 font=("Arial", 18),  # Increased font size
                                 text_color=PURPLE_THEME["text"])
    category_label.pack(side="right")

    comments_label = ctk.CTkLabel(box_frame, 
                                 text=feedback_data['comments'],
                                 wraplength=600,
                                 font=("Arial", 16),  # Increased font size
                                 text_color=PURPLE_THEME["text"])
    comments_label.pack(fill="x", padx=20, pady=5)

    footer_frame = ctk.CTkFrame(box_frame, fg_color="transparent")
    footer_frame.pack(fill="x", padx=20, pady=(5, 10))
    
    timestamp_label = ctk.CTkLabel(footer_frame, 
                                  text=feedback_data['timestamp'],
                                  font=("Arial", 14),  # Increased font size
                                  text_color=PURPLE_THEME["text"])
    timestamp_label.pack(side="left")

def filter_feedback(container, complaint_type_combo, search_entry):
    # Clear existing feedback boxes
    for widget in container.winfo_children():
        widget.destroy()
    
    selected_type = complaint_type_combo.get()
    search_text = search_entry.get().lower()
    
    all_feedback = get_feedback_from_db()
    filtered_feedback = [
        feedback for feedback in all_feedback
        if (selected_type == "All" or feedback["category"] == selected_type) and
        (not search_text or search_text in feedback["stall_name"].lower())
    ]
    
    for feedback in filtered_feedback:
        create_feedback_box(container, feedback)

def show_view_feedback(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for feedback view
    feedback_frame = ctk.CTkFrame(root, fg_color=PURPLE_THEME["background"])
    feedback_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide feedback frame and call the dashboard callback
        feedback_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=feedback_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)

    # Title
    title_label = ctk.CTkLabel(
        feedback_frame, 
        text="Feedback", 
        font=("Gothic", 64, "bold"), 
        text_color=PURPLE_THEME["text"]
    )
    title_label.pack(pady=(20, 40))

    # Controls frame
    controls_frame = ctk.CTkFrame(feedback_frame, fg_color="transparent")
    controls_frame.pack(fill="x", padx=20, pady=10)

    # Complaint type combo
    COMPLAINT_TYPES = ["All", "Complain", "Feature Request", "Payment Issue", "System Issue"]
    complaint_type_combo = ttk.Combobox(
        controls_frame, 
        values=COMPLAINT_TYPES, 
        state="readonly", 
        font=("Arial", 12)
    )
    complaint_type_combo.set("All")
    complaint_type_combo.pack(side="left", padx=20)

    # Search entry
    search_entry = ctk.CTkEntry(
        controls_frame, 
        placeholder_text="Search by Stall Name...", 
        border_width=0,
        text_color=PURPLE_THEME["text"],
        fg_color="white",
        height=40,
        font=("Arial", 14),  # Increased font size
        width=400
    )
    search_entry.pack(side="left", padx=20)

    # Search button
    search_button = ctk.CTkButton(
        controls_frame, 
        text="Search", 
        fg_color=PURPLE_THEME["button"],
        height=40,
        width=120,
        font=("Arial", 20, "bold"),
        command=lambda: filter_feedback(container, complaint_type_combo, search_entry)
    )
    search_button.pack(side="left", padx=20)

    # Container for feedback boxes
    container = ctk.CTkScrollableFrame(feedback_frame, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=20, pady=20)

    # Bind events
    complaint_type_combo.bind(
        "<<ComboboxSelected>>", 
        lambda e: filter_feedback(container, complaint_type_combo, search_entry)
    )

    # Load initial feedback
    initial_feedback = get_feedback_from_db()
    for feedback in initial_feedback:
        create_feedback_box(container, feedback)

def main():
    root = ctk.CTk()
    root.title("View Feedback")
    root.geometry("1920x1080")
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Feedback View",
        command=lambda: show_view_feedback(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
