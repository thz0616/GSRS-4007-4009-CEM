import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import ttk


# Initialize the database
def init_db():
    conn = sqlite3.connect('tenants.db')
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


# Function to show a specific frame
def show_frame(frame):
    frame.tkraise()


# Function to submit an announcement
def submit_announcement():
    topic = topic_entry.get().strip()
    content = content_text.get("1.0", "end").strip()

    if not topic or not content:
        messagebox.showerror("Input Error", "Please enter both topic and content.")
        return

    try:
        conn = sqlite3.connect('tenants.db')
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
    topic_entry.delete(0, 'end')
    content_text.delete("1.0", "end")

    # Refresh the messages list
    populate_messages()


# Function to populate messages in the Treeview
def populate_messages(search_query=None):
    for item in messages_tree.get_children():
        messages_tree.delete(item)
    global messages_list
    messages_list = []  # Reset the list
    try:
        conn = sqlite3.connect('tenants.db')
        cursor = conn.cursor()
        if search_query:
            cursor.execute('''
                SELECT id, topic, strftime('%Y-%m-%d %H:%M', timestamp, '+8 hours') as formatted_timestamp FROM announcements
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
            messages_tree.insert('', 'end', values=(timestamp, topic), tags=(msg_id,))
            messages_list.append({'id': msg_id, 'topic': topic, 'timestamp': timestamp})
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")


# Function to search messages
def search_messages():
    query = search_entry.get().strip()
    populate_messages(search_query=query)


# Function to display message details when a message is selected
def display_message_details(event):
    selected_item = messages_tree.focus()
    if not selected_item:
        return
    item_values = messages_tree.item(selected_item, 'values')
    if not item_values:
        return
    timestamp, topic = item_values
    msg_id = messages_tree.item(selected_item, 'tags')[0]

    # Fetch content from DB
    try:
        conn = sqlite3.connect('tenants.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT content, strftime("%Y-%m-%d %H:%M", timestamp, "+8 hours") as formatted_timestamp FROM announcements WHERE id = ?',
            (msg_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            content, timestamp = result
            # Update message details in the right pane
            topic_detail_label.configure(text=topic)
            timestamp_detail_label.configure(text=f"Date: {timestamp}")
            content_detail_text.configure(state="normal")
            content_detail_text.delete("1.0", "end")
            content_detail_text.insert("end", content)
            content_detail_text.configure(state="disabled")

            # ***** Show the message details pane *****
            message_details_pane.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            messages_container.grid_columnconfigure(1, weight=3)  # Adjust column weights
        else:
            messagebox.showerror("Not Found", "Selected message not found in the database.")
            return
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return


# Create the main window
root = ctk.CTk()
root.title("Tenant Management System")
root.geometry("1920x1080")
root.resizable(False, False)  # Fixed size as per requirement

# Set default appearance mode and color theme
ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Create container frames for each page
home_frame = ctk.CTkFrame(root, corner_radius=20)
announcement_frame = ctk.CTkFrame(root, corner_radius=20)
view_messages_frame = ctk.CTkFrame(root, corner_radius=20)

for frame in (home_frame, announcement_frame, view_messages_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# Configure grid to make frames expand
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# ====================== Home Page ======================

# Home Page Widgets
home_title = ctk.CTkLabel(home_frame, text="Tenant Management System", font=ctk.CTkFont(size=48, weight="bold"))
home_title.pack(pady=80)

# Make Announcement Button (Admin)
admin_button = ctk.CTkButton(
    home_frame,
    text="Make Announcement (Admin)",
    width=400,
    height=80,
    font=ctk.CTkFont(size=24),
    corner_radius=15,
    command=lambda: show_frame(announcement_frame)
)
admin_button.pack(pady=40)

# View Messages Button (Tenant)
tenant_button = ctk.CTkButton(
    home_frame,
    text="View Messages (Tenant)",
    width=400,
    height=80,
    font=ctk.CTkFont(size=24),
    corner_radius=15,
    command=lambda: show_frame(view_messages_frame)
)
tenant_button.pack(pady=40)

# ====================== Make Announcement Page ======================

# Make Announcement Page Widgets
announcement_title = ctk.CTkLabel(announcement_frame, text="Make Announcement",
                                  font=ctk.CTkFont(size=36, weight="bold"))
announcement_title.pack(pady=40)

# Topic Entry
topic_label = ctk.CTkLabel(announcement_frame, text="Topic:", font=ctk.CTkFont(size=24))
topic_label.pack(pady=(20, 10))
topic_entry = ctk.CTkEntry(announcement_frame, width=1400, height=60, font=ctk.CTkFont(size=20), corner_radius=15)
topic_entry.pack()

# Content Textbox
content_label = ctk.CTkLabel(announcement_frame, text="Content:", font=ctk.CTkFont(size=24))
content_label.pack(pady=(20, 10))
content_text = ctk.CTkTextbox(announcement_frame, width=1400, height=500, font=ctk.CTkFont(size=18), corner_radius=15)
content_text.pack()

# Submit Button
submit_button = ctk.CTkButton(
    announcement_frame,
    text="Submit Announcement",
    width=200,
    height=60,
    font=ctk.CTkFont(size=20),
    corner_radius=15,
    command=submit_announcement
)
submit_button.pack(pady=30)

# Back Button
back_button_announcement = ctk.CTkButton(
    announcement_frame,
    text="Back to Home",
    width=200,
    height=60,
    font=ctk.CTkFont(size=20),
    corner_radius=15,
    command=lambda: show_frame(home_frame)
)
back_button_announcement.pack()

# ====================== View Messages Page ======================

# View Messages Page Widgets
view_title = ctk.CTkLabel(view_messages_frame, text="View Messages", font=ctk.CTkFont(size=36, weight="bold"))
view_title.pack(pady=20)

# Back Button to Home
back_button_view = ctk.CTkButton(
    view_messages_frame,
    text="Back to Home",
    width=200,
    height=60,
    font=ctk.CTkFont(size=20),
    corner_radius=15,
    command=lambda: show_frame(home_frame)
)
back_button_view.pack(pady=10)

# Create a container frame for dual-pane layout
messages_container = ctk.CTkFrame(view_messages_frame, corner_radius=20)
messages_container.pack(fill="both", expand=True, padx=40, pady=40)

# Configure grid for dual-pane
messages_container.grid_rowconfigure(0, weight=1)
messages_container.grid_columnconfigure(0, weight=1)
# Initially, only the messages list pane is visible
messages_container.grid_columnconfigure(1, weight=0)

# ====================== Messages List Pane ======================

# Left pane for messages list
messages_list_pane = ctk.CTkFrame(messages_container, corner_radius=20)
messages_list_pane.grid(row=0, column=0, sticky="nsew")
# No padding on the right initially
messages_list_pane.grid_columnconfigure(0, weight=1)
messages_list_pane.grid_rowconfigure(1, weight=1)

# Search Bar
search_frame = ctk.CTkFrame(messages_list_pane, corner_radius=10)
search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
search_frame.grid_columnconfigure(0, weight=1)

# search_label = ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=16))
# search_label.grid(row=0, column=0, padx=(0, 10))

search_entry = ctk.CTkEntry(search_frame, width=300, height=30, font=ctk.CTkFont(size=14), corner_radius=10)
search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")  # Adjusted column

search_button = ctk.CTkButton(
    search_frame,
    text="Search",
    width=100,
    height=30,
    font=ctk.CTkFont(size=14),
    corner_radius=10,
    command=search_messages
)
search_button.grid(row=0, column=1)

# Treeview for messages
messages_tree = ttk.Treeview(messages_list_pane, columns=("Timestamp", "Topic"), show='headings', selectmode="browse")
messages_tree.heading("Timestamp", text="Date & Time")
messages_tree.heading("Topic", text="Topic")
messages_tree.column("Timestamp", width=200, anchor='center')
messages_tree.column("Topic", width=600, anchor='w')

# Attach scrollbar to Treeview
tree_scroll = ttk.Scrollbar(messages_list_pane, orient="vertical", command=messages_tree.yview)
messages_tree.configure(yscrollcommand=tree_scroll.set)
tree_scroll.grid(row=1, column=1, sticky='ns')
messages_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Style the Treeview for better appearance
style = ttk.Style()
style.theme_use("clam")  # Use 'clam' theme for better styling

# Configure Treeview style
style.configure("Treeview",
                background="#f0f0f0",
                foreground="black",
                rowheight=50,
                fieldbackground="#f0f0f0",
                font=("Arial", 16))

style.configure("Treeview.Heading",
                font=("Arial", 18, "bold"),
                background="#d9d9d9")

style.map("Treeview", background=[('selected', '#347083')], foreground=[('selected', 'white')])

# Bind selection event
messages_tree.bind("<<TreeviewSelect>>", display_message_details)

# ====================== Message Details Pane ======================

# Right pane for message details
message_details_pane = ctk.CTkFrame(messages_container, corner_radius=20)
# Do not grid the message_details_pane initially
# It will be gridded when a message is selected

# Message Details Widgets
topic_detail_label = ctk.CTkLabel(message_details_pane, text="", font=ctk.CTkFont(size=24, weight="bold"), anchor="nw")
topic_detail_label.pack(pady=(20, 5), padx=20, anchor="nw")

timestamp_detail_label = ctk.CTkLabel(message_details_pane, text="", font=ctk.CTkFont(size=14),
                                      anchor="nw")  # Removed 'slant="italic"'
timestamp_detail_label.pack(pady=(0, 10), padx=20, anchor="nw")

content_detail_label = ctk.CTkLabel(message_details_pane, text="Content:", font=ctk.CTkFont(size=24, weight="bold"),
                                    anchor="nw")
content_detail_label.pack(pady=(20, 5), padx=20, anchor="nw")

content_detail_text = ctk.CTkTextbox(message_details_pane, wrap="word", font=ctk.CTkFont(size=18), corner_radius=10)
content_detail_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
content_detail_text.configure(state="disabled")

# ====================== Running the Application ======================

# List to store messages
messages_list = []


# Populate messages in the Treeview
def on_startup():
    populate_messages()


# Initialize the database and start the application
if __name__ == "__main__":
    init_db()
    on_startup()
    show_frame(home_frame)
    root.mainloop()
