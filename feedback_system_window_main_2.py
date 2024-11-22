import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Initialize database
conn = sqlite3.connect('properties.db')
cursor = conn.cursor()

# Create feedback table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        comment TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Function to submit feedback
def submit_feedback():
    category = category_var.get()
    comment = comment_entry.get()
    
    if not category or not comment:
        messagebox.showwarning("Warning", "Please select a category and enter a comment.")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO feedback (category, comment, timestamp) VALUES (?, ?, ?)",
                   (category, comment, timestamp))
    conn.commit()
    
    messagebox.showinfo("Success", "Feedback submitted successfully!")
    comment_entry.delete(0, tk.END)
    category_var.set("")

# Function to view feedback
def view_feedback():
    view_window = tk.Toplevel(root)
    view_window.title("View Feedback")
    view_window.geometry("500x300")
    
    # Table for feedback
    tree = ttk.Treeview(view_window, columns=("ID", "Category", "Comment", "Timestamp"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Category", text="Category")
    tree.heading("Comment", text="Comment")
    tree.heading("Timestamp", text="Timestamp")
    
    # Populate feedback table
    cursor.execute("SELECT * FROM feedback")
    feedbacks = cursor.fetchall()
    for feedback in feedbacks:
        tree.insert("", tk.END, values=feedback)
    
    tree.pack(expand=True, fill=tk.BOTH)

    # Delete selected feedback
    def delete_feedback():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a feedback to delete.")
            return
        
        feedback_id = tree.item(selected_item[0], "values")[0]
        cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        conn.commit()
        
        tree.delete(selected_item)
        messagebox.showinfo("Success", "Feedback deleted successfully!")
    
    delete_button = tk.Button(view_window, text="Delete Selected Feedback", command=delete_feedback)
    delete_button.pack(pady=5)

# Main window
root = tk.Tk()
root.title("Feedback System")
root.geometry("400x300")

# Category selection
category_var = tk.StringVar()
categories = ["Complain", "UI Issue", "Payment Issue", "Feature Request"]

category_label = tk.Label(root, text="Select Feedback Category:")
category_label.pack()

for category in categories:
    rb = tk.Radiobutton(root, text=category, variable=category_var, value=category)
    rb.pack(anchor=tk.W)

# Comment entry
comment_label = tk.Label(root, text="Enter your comment:")
comment_label.pack()

comment_entry = tk.Entry(root, width=40)
comment_entry.pack(pady=5)

# Submit button
submit_button = tk.Button(root, text="Send Feedback", command=submit_feedback)
submit_button.pack(pady=10)

# View Feedback button
view_button = tk.Button(root, text="View Feedback", command=view_feedback)
view_button.pack()

root.mainloop()
conn.close()
