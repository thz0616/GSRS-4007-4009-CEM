import customtkinter as ctk
import sqlite3
from tkinter import messagebox

def show_announcement_page(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for announcement page
    announcement_frame = ctk.CTkFrame(root, fg_color="#F0E6FF")
    announcement_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide announcement frame and call the dashboard callback
        announcement_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=announcement_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)
    
    # Create the AnnouncementPage instance
    app = AnnouncementPage(announcement_frame)

class AnnouncementPage:
    def __init__(self, master):
        self.master = master
        
        # Custom purple color scheme
        self.purple_theme = {
            "bg_color": "#F0E6FF",  # Light purple background
            "frame_color": "#E6D9FF",  # Slightly darker purple for frame
            "button_color": "#9370DB",  # Medium purple for buttons
            "button_hover_color": "#8A2BE2",  # Deeper purple for button hover
            "text_color": "#4B0082"  # Dark purple for text
        }

        # Initialize database
        self.init_db()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(
            self.master, 
            corner_radius=20,
            fg_color=self.purple_theme["frame_color"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_widgets()

    def init_db(self):
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def create_widgets(self):
        # Title
        announcement_title = ctk.CTkLabel(
            self.main_frame, 
            text="Make Announcement",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.purple_theme["text_color"]
        )
        announcement_title.pack(pady=40)

        # Topic Entry
        topic_label = ctk.CTkLabel(
            self.main_frame, 
            text="Topic:", 
            font=ctk.CTkFont(size=24),
            text_color=self.purple_theme["text_color"]
        )
        topic_label.pack(pady=(20, 10))
        
        self.topic_entry = ctk.CTkEntry(
            self.main_frame, 
            width=1400, 
            height=60, 
            font=ctk.CTkFont(size=20), 
            corner_radius=15,
            border_color=self.purple_theme["button_color"]
        )
        self.topic_entry.pack()

        # Content Textbox
        content_label = ctk.CTkLabel(
            self.main_frame, 
            text="Content:", 
            font=ctk.CTkFont(size=24),
            text_color=self.purple_theme["text_color"]
        )
        content_label.pack(pady=(20, 10))
        
        self.content_text = ctk.CTkTextbox(
            self.main_frame, 
            width=1400, 
            height=500, 
            font=ctk.CTkFont(size=18), 
            corner_radius=15,
            border_color=self.purple_theme["button_color"],
            border_width=2,
            fg_color="white"
        )
        self.content_text.pack()

        # Submit Button
        submit_button = ctk.CTkButton(
            self.main_frame,
            text="Submit Announcement",
            width=200,
            height=60,
            font=ctk.CTkFont(size=20),
            corner_radius=15,
            command=self.submit_announcement,
            fg_color=self.purple_theme["button_color"],
            hover_color=self.purple_theme["button_hover_color"]
        )
        submit_button.pack(pady=30)

    def submit_announcement(self):
        topic = self.topic_entry.get().strip()
        content = self.content_text.get("1.0", "end").strip()

        if not topic or not content:
            messagebox.showerror("Input Error", "Please enter both topic and content.")
            return

        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO announcements (topic, content) VALUES (?, ?)
            ''', (topic, content))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return

        messagebox.showinfo("Success", "Announcement submitted successfully!")

        # Clear the fields
        self.topic_entry.delete(0, 'end')
        self.content_text.delete("1.0", "end")

def main():
    root = ctk.CTk()
    root.title("Make Announcement")
    root.geometry("1920x1080")
    root.resizable(False, False)
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Announcement Page",
        command=lambda: show_announcement_page(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main() 