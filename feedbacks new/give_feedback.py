import customtkinter as ctk
from PIL import Image, ImageTk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, set_appearance_mode, set_default_color_theme
import tkinter as tk
import sqlite3
from datetime import datetime


# Initialize the application
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("1000x1000")
root.title("Add your feedback")
root.configure(bg="#F4F1E9")
root.attributes("-fullscreen", True)


# Function to set background image
def set_background(root, image_path):
    image = Image.open(image_path)
    resized_image = image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)
    canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    canvas.image = bg_image  # Keep a reference to avoid garbage collection


set_background(root, "C:/Users/tanji/OneDrive/Desktop/fedbacks/WhatsApp Image 2024-11-07 at 13.22.12_0ba57abf.jpg")

# Add a new frame to the app
my_frame = CTkFrame(master=root, width=1600, height=780, fg_color="#C2B8AE", corner_radius=30)
my_frame.place(x=190, y=100)

label = ctk.CTkLabel(master=my_frame, text="Feedback", text_color="black", font=("Arial", 64, "bold"))
label.place(x=670, y=40)

sub_label = ctk.CTkLabel(
    master=my_frame,
    text="If you have found any defect on your property or would like to give a suggestion,\nplease let us know in the field below.",
    text_color="#897A6E",
    font=("Arial", 23)
)
sub_label.place(x=390, y=130)


# Function to set subject text when buttons are clicked
def set_subject_text(category):
    subject_entry.delete(0, ctk.END)
    subject_entry.insert(0, category)
    subject_entry.icursor(len(category))


# Buttons
complain_button = CTkButton(my_frame, text="Complain +", text_color="black", font=("Century Gothic", 20),
                            width=200, height=50, corner_radius=30, fg_color="#C2B8AE", hover_color="#897A6E",
                            border_color="#897A6E", border_width=2,
                            command=lambda: set_subject_text("Complain"))
complain_button.place(x=200, y=210)

ui_button = CTkButton(my_frame, text="System Issue +", text_color="black", font=("Century Gothic", 20),
                      width=200, height=50, corner_radius=30, fg_color="#C2B8AE", hover_color="#897A6E",
                      border_color="#897A6E", border_width=2,
                      command=lambda: set_subject_text("System Issue"))
ui_button.place(x=420, y=210)

payment_button = CTkButton(my_frame, text="Payment Issue +", text_color="black", font=("Century Gothic", 20),
                           width=280, height=50, corner_radius=30, fg_color="#C2B8AE", hover_color="#897A6E",
                           border_color="#897A6E", border_width=2,
                           command=lambda: set_subject_text("Payment Issue"))
payment_button.place(x=200, y=290)

feature_button = CTkButton(my_frame, text="Feature Request +", text_color="black", font=("Century Gothic", 20),
                           width=280, height=50, corner_radius=30, fg_color="#C2B8AE", hover_color="#897A6E",
                           border_color="#897A6E", border_width=2,
                           command=lambda: set_subject_text("Feature Request"))
feature_button.place(x=500, y=290)

subject_entry = ctk.CTkEntry(
    master=my_frame,
    placeholder_text="Subject",
    width=1200,
    height=80,
    font=("Arial", 16),
    corner_radius=30,
    fg_color="#C2B8AE",
    border_color="#897A6E",
    border_width=2
)
subject_entry.place(x=200, y=370)

comment_entry = ctk.CTkEntry(
    master=my_frame,
    placeholder_text="Leave your comment here",
    width=1200,
    height=250,
    font=("Arial", 16),
    corner_radius=30,
    fg_color="#C2B8AE",
    border_color="#897A6E",
    border_width=2
)
comment_entry.place(x=200, y=460)


# Function to insert feedback into the database
def insert_feedback(category, comment):
    # Connect to the properties database
    conn = sqlite3.connect("properties.db")
    cursor = conn.cursor()

    # Insert data with the current timestamp
    sql_command = """
    INSERT INTO feedback (category, comment, timestamp) 
    VALUES (?, ?, ?)
    """
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute(sql_command, (category, comment, timestamp))
        conn.commit()
        print("Feedback submitted successfully")
        # Clear the entry fields after successful submission
        subject_entry.delete(0, ctk.END)
        comment_entry.delete(0, ctk.END)
    except Exception as e:
        print(f"Failed to submit feedback: {e}")
    finally:
        conn.close()


# Function to handle data submission
def submit_feedback():
    category = subject_entry.get()
    comment = comment_entry.get()
    
    if not category or not comment:
        print("Please fill in both category and comment")
        return
        
    insert_feedback(category, comment)


# Upload button with custom size
upload_button = ctk.CTkButton(
    root,
    text="SEND",
    width=800,
    height=70,
    font=("Century Gothic", 30),
    text_color="black",
    fg_color="#C2B8AE",
    hover_color="#c89ef2",
    corner_radius=30,
)
upload_button.place(x=600, y=900)  # Button placement

# Updating the SEND button to trigger feedback submission
upload_button.configure(command=submit_feedback)

root.mainloop()