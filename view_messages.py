import customtkinter as ctk
import sqlite3
from tkinter import ttk, messagebox

class ViewMessagesPage:
    def __init__(self):
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("View Messages")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)
        self.root.attributes("-fullscreen", True)

        # Set default appearance mode and custom color theme
        ctk.set_appearance_mode("light")
        
        # Custom beige/brown color scheme
        self.color_theme = {
            "bg_color": "#F5F0EB",         # Light beige background
            "frame_color": "#E8DCD5",      # Slightly darker beige for frames
            "button_color": "#A69586",      # Brown for buttons
            "button_hover_color": "#8B7355", # Darker brown for button hover
            "text_color": "#4A4039",        # Dark brown for text
            "selected_color": "#C4B5A8"     # Medium brown for selected items
        }

        # Set root background color
        self.root._set_appearance_mode("light")
        self.root.configure(fg_color=self.color_theme["bg_color"])

        # Create main frame
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=20,
            fg_color=self.color_theme["frame_color"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title and Back Button Container
        title_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            fg_color=self.color_theme["frame_color"]
        )
        title_container.pack(fill="x", pady=20)

        # Back Button
        back_button = ctk.CTkButton(
            title_container,
            text="Back",
            width=100,
            height=30,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            command=self.root.destroy,
            fg_color=self.color_theme["button_color"],
            hover_color=self.color_theme["button_hover_color"]
        )
        back_button.pack(side="left", padx=20)

        # Title
        self.view_title = ctk.CTkLabel(
            title_container,
            text="View Messages",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.color_theme["text_color"]
        )
        self.view_title.pack(pady=20)

        # Create container frame for dual-pane layout
        self.messages_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            fg_color=self.color_theme["frame_color"]
        )
        self.messages_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Configure grid for dual-pane
        self.messages_container.grid_rowconfigure(0, weight=1)
        self.messages_container.grid_columnconfigure(0, weight=1)
        self.messages_container.grid_columnconfigure(1, weight=0)

        self.create_messages_list_pane()
        self.create_message_details_pane()
        self.messages_list = []
        self.populate_messages()

    def create_messages_list_pane(self):
        # Left pane for messages list
        self.messages_list_pane = ctk.CTkFrame(
            self.messages_container,
            corner_radius=20,
            fg_color=self.color_theme["frame_color"]
        )
        self.messages_list_pane.grid(row=0, column=0, sticky="nsew")
        self.messages_list_pane.grid_columnconfigure(0, weight=1)
        self.messages_list_pane.grid_rowconfigure(1, weight=1)

        # Search Bar
        search_frame = ctk.CTkFrame(
            self.messages_list_pane,
            corner_radius=10,
            fg_color=self.color_theme["frame_color"]
        )
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=400,
            height=40,
            font=ctk.CTkFont(size=18),
            corner_radius=10
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=120,
            height=40,
            font=ctk.CTkFont(size=18),
            corner_radius=10,
            command=self.search_messages,
            fg_color=self.color_theme["button_color"],
            hover_color=self.color_theme["button_hover_color"]
        )
        search_button.grid(row=0, column=1)

        # Treeview for messages
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",  # Create a custom style name
            background="#F5F0EB",          
            foreground="#4A4039",          
            rowheight=100,                 
            fieldbackground="#F5F0EB",     
            font=("Arial", 40)  # Increased font size from 32 to 40
        )
        style.configure(
            "Custom.Treeview.Heading",     # Custom heading style
            font=("Arial", 34, "bold"),    
            background="#E8DCD5"           
        )
        style.map("Custom.Treeview",
                 background=[('selected', '#C4B5A8')],    
                 foreground=[('selected', '#4A4039')])    

        self.messages_tree = ttk.Treeview(
            self.messages_list_pane,
            columns=("Timestamp", "Topic"),
            show='headings',
            selectmode="browse",
            style="Custom.Treeview"  # Apply the custom style
        )
        self.messages_tree.heading("Timestamp", text="Date & Time")
        self.messages_tree.heading("Topic", text="Topic")
        self.messages_tree.column("Timestamp", width=200, anchor='center')
        self.messages_tree.column("Topic", width=600, anchor='w')

        # Scrollbar
        tree_scroll = ttk.Scrollbar(
            self.messages_list_pane,
            orient="vertical",
            command=self.messages_tree.yview
        )
        self.messages_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.grid(row=1, column=1, sticky='ns')
        self.messages_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Bind selection event
        self.messages_tree.bind("<<TreeviewSelect>>", self.display_message_details)

    def create_message_details_pane(self):
        # Right pane for message details
        self.message_details_pane = ctk.CTkFrame(
            self.messages_container,
            corner_radius=20,
            fg_color=self.color_theme["frame_color"]
        )

        # Message Details Widgets
        self.topic_detail_label = ctk.CTkLabel(
            self.message_details_pane,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.color_theme["text_color"],
            anchor="w"
        )
        self.topic_detail_label.pack(pady=(20, 5), padx=20, anchor="w")

        self.timestamp_detail_label = ctk.CTkLabel(
            self.message_details_pane,
            text="",
            font=ctk.CTkFont(size=18),
            text_color=self.color_theme["text_color"],
            anchor="w"
        )
        self.timestamp_detail_label.pack(pady=(0, 10), padx=20, anchor="w")

        content_detail_label = ctk.CTkLabel(
            self.message_details_pane,
            text="Content:",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.color_theme["text_color"],
            anchor="w"
        )
        content_detail_label.pack(pady=(20, 5), padx=20, anchor="w")

        self.content_detail_text = ctk.CTkTextbox(
            self.message_details_pane,
            wrap="word",
            font=ctk.CTkFont(size=22),
            corner_radius=10,
            border_width=2,
            border_color=self.color_theme["button_color"],
            fg_color="white"
        )
        self.content_detail_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.content_detail_text.configure(state="disabled")

    def populate_messages(self, search_query=None):
        for item in self.messages_tree.get_children():
            self.messages_tree.delete(item)
        self.messages_list = []
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            if search_query:
                cursor.execute('''
                    SELECT id, topic, strftime('%Y-%m-%d %H:%M', timestamp, '+8 hours') as formatted_timestamp 
                    FROM announcements
                    WHERE topic LIKE ? OR content LIKE ?
                    ORDER BY timestamp DESC
                ''', (f'%{search_query}%', f'%{search_query}%'))
            else:
                cursor.execute('''
                    SELECT id, topic, strftime('%Y-%m-%d %H:%M', timestamp, '+8 hours') as formatted_timestamp
                    FROM announcements
                    ORDER BY timestamp DESC
                ''')
            messages = cursor.fetchall()
            conn.close()

            for msg in messages:
                msg_id, topic, timestamp = msg
                self.messages_tree.insert('', 'end', values=(timestamp, topic), tags=(msg_id,))
                self.messages_list.append({'id': msg_id, 'topic': topic, 'timestamp': timestamp})
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def search_messages(self):
        query = self.search_entry.get().strip()
        self.populate_messages(search_query=query)

    def display_message_details(self, event):
        selected_item = self.messages_tree.focus()
        if not selected_item:
            return
        item_values = self.messages_tree.item(selected_item, 'values')
        if not item_values:
            return
        timestamp, topic = item_values
        msg_id = self.messages_tree.item(selected_item, 'tags')[0]

        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute(
                'SELECT content, strftime("%Y-%m-%d %H:%M", timestamp, "+8 hours") as formatted_timestamp FROM announcements WHERE id = ?',
                (msg_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                content, timestamp = result
                self.topic_detail_label.configure(text=topic)
                self.timestamp_detail_label.configure(text=f"Date: {timestamp}")
                self.content_detail_text.configure(state="normal")
                self.content_detail_text.delete("1.0", "end")
                self.content_detail_text.insert("end", content)
                self.content_detail_text.configure(state="disabled")

                # Show the message details pane
                self.message_details_pane.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
                self.messages_container.grid_columnconfigure(1, weight=3)
            else:
                messagebox.showerror("Not Found", "Selected message not found in the database.")
                return
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ViewMessagesPage()
    app.run() 