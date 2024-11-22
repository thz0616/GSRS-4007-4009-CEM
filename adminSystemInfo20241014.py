import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import os

# Initialize customtkinter appearance
ctk.set_appearance_mode("Light")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # We'll customize colors manually

# Global variables
banner_image_paths = []
current_image_index = 0
current_photo = None  # To keep a reference to the PhotoImage
is_modified = False  # Flag to track if changes have been made
passcode_var = None  # For passcode entry

def upload_images():
    global banner_image_paths, current_image_index, is_modified
    # Open file dialog to select images
    file_paths = filedialog.askopenfilenames(
        title="Select Banner Images",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )

    if file_paths:
        # Prevent duplicate uploads
        new_paths = [path for path in file_paths if path not in banner_image_paths]
        if not new_paths:
            messagebox.showinfo("No New Images", "No new images were selected to upload.")
            return
        banner_image_paths.extend(new_paths)
        if len(banner_image_paths) > 0:
            current_image_index = len(banner_image_paths) - len(new_paths)  # Start with first of new images
            display_current_image()
            is_modified = True
            update_save_button_state()

def display_current_image():
    global current_photo
    if not banner_image_paths:
        image_label.configure(image='', text="No Images Uploaded")
        back_button.configure(state="disabled")
        next_button.configure(state="disabled")
        return

    # Load the current image
    try:
        img_path = banner_image_paths[current_image_index]
        img = Image.open(img_path)
        img = img.resize((800, 600), Image.LANCZOS)  # Use high-quality downsampling filter
        current_photo = ImageTk.PhotoImage(img)
        image_label.configure(image=current_photo, text="")
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to load image.\nError: {e}")
        image_label.configure(image='', text="Error Loading Image")

    # Update button states
    back_button.configure(state="normal" if current_image_index > 0 else "disabled")
    next_button.configure(state="normal" if current_image_index < len(banner_image_paths) - 1 else "disabled")
    remove_button.configure(state="normal")

def show_previous_image():
    global current_image_index
    if current_image_index > 0:
        current_image_index -= 1
        display_current_image()

def show_next_image():
    global current_image_index
    if current_image_index < len(banner_image_paths) - 1:
        current_image_index += 1
        display_current_image()

def remove_current_image():
    global banner_image_paths, current_image_index, is_modified
    if not banner_image_paths:
        messagebox.showinfo("No Images", "There are no images to remove.")
        return

    # Confirm removal
    confirm = messagebox.askyesno("Remove Image", "Are you sure you want to remove the current image?")
    if not confirm:
        return

    removed_image = banner_image_paths.pop(current_image_index)
    messagebox.showinfo("Image Removed", f"Removed image: {os.path.basename(removed_image)}")
    is_modified = True
    update_save_button_state()

    # Adjust current_image_index
    if current_image_index >= len(banner_image_paths) and current_image_index > 0:
        current_image_index -= 1

    display_current_image()

def save_information():
    global is_modified
    agreement = agreement_text_var.get("1.0", ctk.END).strip()
    passcode = passcode_var.get().strip()  # Get passcode value

    if not agreement:
        messagebox.showerror("Input Error", "Please enter the tenant rental application agreement.")
        return

    if not banner_image_paths:
        messagebox.showerror("Input Error", "Please upload at least one tenant banner image.")
        return

    api_key = api_key_var.get().strip()
    if not api_key:
        messagebox.showerror("Input Error", "Please enter the API key for AI features.")
        return

    if not passcode:  # Validate passcode
        messagebox.showerror("Input Error", "Please enter the admin registration passcode.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Insert into systemInformation with passcode
        cursor.execute('''
            INSERT INTO systemInformation (rental_agreement, api_key, passcode) 
            VALUES (?, ?, ?)
        ''', (agreement, api_key, passcode))
        system_info_id = cursor.lastrowid

        # Insert banner image paths
        for path in banner_image_paths:
            cursor.execute('''
                INSERT INTO bannerImages (system_info_id, image_path) 
                VALUES (?, ?)
            ''', (system_info_id, path))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "System information saved successfully.")

        # Clear the form and reload data
        banner_image_paths.clear()
        current_image_index = 0
        agreement_text_var.delete("1.0", ctk.END)
        passcode_var.delete(0, ctk.END)  # Clear passcode
        display_current_image()
        is_modified = False
        update_save_button_state()
        load_information()

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while saving to the database:\n{e}")

def load_information():
    global banner_image_paths, current_image_index, is_modified
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, rental_agreement, api_key, passcode 
            FROM systemInformation 
            ORDER BY created_at DESC LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            latest_system_id, rental_agreement, api_key, passcode = result
            
            # Populate the agreement textbox
            agreement_text_var.delete("1.0", ctk.END)
            agreement_text_var.insert(ctk.END, rental_agreement)
            
            # Populate the API key entry
            api_key_var.delete(0, ctk.END)
            if api_key:
                api_key_var.insert(0, api_key)
                
            # Populate the passcode entry
            passcode_var.delete(0, ctk.END)
            if passcode:
                passcode_var.insert(0, passcode)

            # Fetch associated banner images
            cursor.execute('''
                SELECT image_path FROM bannerImages WHERE system_info_id = ?
            ''', (latest_system_id,))
            images = cursor.fetchall()
            banner_image_paths = [img[0] for img in images]
            if banner_image_paths:
                current_image_index = 0
                display_current_image()
            else:
                display_current_image()
        else:
            # No existing data
            display_current_image()

        conn.close()
        is_modified = False
        update_save_button_state()

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred while loading data from the database:\n{e}")

def on_agreement_change(event):
    global is_modified
    if not is_modified:
        is_modified = True
        update_save_button_state()

def update_save_button_state():
    if is_modified:
        save_button.configure(state="normal")
    else:
        save_button.configure(state="disabled")

def toggle_api_key_visibility():
    global api_key_var, show_hide_button
    if api_key_var.cget('show') == '*':
        api_key_var.configure(show="")
        show_hide_button.configure(text="Hide API Key")
    else:
        api_key_var.configure(show="*")
        show_hide_button.configure(text="Show API Key")

def toggle_passcode_visibility(entry_widget, button):
    if entry_widget.cget('show') == '*':
        entry_widget.configure(show="")
        button.configure(text="Hide Passcode")
    else:
        entry_widget.configure(show="*")
        button.configure(text="Show Passcode")

def on_passcode_change(event):
    global is_modified
    if not is_modified:
        is_modified = True
        update_save_button_state()

def show_admin_system_info(root, home_frame, show_dashboard_callback):
    global image_label, back_button, next_button, remove_button, agreement_text_var
    global save_button, api_key_var, show_hide_button, passcode_var
    
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame
    system_frame = ctk.CTkFrame(root, fg_color="#E6E6FA")
    system_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide system frame and call the dashboard callback
        system_frame.pack_forget()
        show_dashboard_callback()
    
    # Back button
    back_btn = ctk.CTkButton(
        master=system_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)
    
    # ==================== Header Section ====================
    header_frame = ctk.CTkFrame(master=system_frame, corner_radius=0, fg_color="#9370DB")
    header_frame.pack(fill="x")
    
    header_label = ctk.CTkLabel(
        master=header_frame,
        text="Government Stall Rental System - Admin Panel",
        font=("Helvetica", 28, "bold"),
        text_color="white"
    )
    header_label.pack(pady=20)
    
    # ==================== Main Content Section ====================
    main_frame = ctk.CTkFrame(master=system_frame, corner_radius=10, fg_color="#E6E6FA")
    main_frame.pack(padx=50, pady=30, fill="both", expand=True)

    # Configure grid layout: two columns - left for form, right for image preview
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # -------------------- Left Side: Form --------------------
    # Create a scrollable frame with increased width
    scrollable_frame = ctk.CTkScrollableFrame(
        master=main_frame,
        fg_color="#DCD0FF",
        width=800,  # Increased width
        height=800
    )
    scrollable_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Form Title
    form_title = ctk.CTkLabel(
        master=scrollable_frame,
        text="System Information",
        font=("Helvetica", 24, "bold"),
        text_color="#4B0082"
    )
    form_title.pack(pady=(20, 10))

    # Upload Images Button
    upload_button = ctk.CTkButton(
        master=scrollable_frame,
        text="Upload Banner Images",
        command=upload_images,
        width=250,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    upload_button.pack(pady=10)

    # Tenant Rental Application Agreement Section
    agreement_label = ctk.CTkLabel(
        master=scrollable_frame,
        text="Tenant Rental Application Agreement",
        font=("Helvetica", 20, "bold"),
        text_color="#4B0082"
    )
    agreement_label.pack(pady=(30, 10))

    # Agreement Textbox
    agreement_text_var = ctk.CTkTextbox(
        master=scrollable_frame,
        width=500,
        height=300,
        wrap="word",
        fg_color="#FFFFFF",
        text_color="black",
        border_color="#D8BFD8",
        corner_radius=5
    )
    agreement_text_var.pack(pady=10, padx=10, fill="both", expand=True)

    # Bind events to detect changes in the agreement textbox
    agreement_text_var.bind("<KeyRelease>", on_agreement_change)
    agreement_text_var.bind("<<Paste>>", on_agreement_change)

    # Adding a remark to guide the admin about placeholders
    remark_text = (
        "Note: Use the following placeholders in the agreement text:\n\n"
        "##tenantName## - Tenant's Name\n"
        "##tenantICNumber## - Tenant's IC Number\n"
        "##stallLocation## - Stall Location\n"
        "##stallSize## - Stall Size\n"
        "##stallRentalFee## - Stall Rental Fee\n"
        "##startDate## - Rental Start Date\n"
        "##endDate## - Rental End Date\n"
        "\n"
        "These placeholders will be automatically replaced with the respective tenant details when the agreement is presented to the tenant."
    )
    
    # Create a frame for the remark with full width
    remark_frame = ctk.CTkFrame(
        master=scrollable_frame,
        fg_color="transparent",
    )
    remark_frame.pack(pady=(5, 10), padx=10, fill="x")
    
    remark_label = ctk.CTkLabel(
        master=remark_frame,
        text=remark_text,
        font=("Helvetica", 14, "bold"),
        text_color="#800080",
        wraplength=700,  # Increased wraplength
        justify="left",
        anchor="w"
    )
    remark_label.pack(pady=5, padx=5, anchor="w", fill="x", expand=True)

    # API Key Section
    api_key_label = ctk.CTkLabel(
        master=scrollable_frame,
        text="AI Features API Key",
        font=("Helvetica", 20, "bold"),
        text_color="#4B0082"
    )
    api_key_label.pack(pady=(20, 10))

    # Frame for API key entry and show/hide button
    api_key_entry_frame = ctk.CTkFrame(
        master=scrollable_frame,
        fg_color="transparent"
    )
    api_key_entry_frame.pack(pady=5, padx=10, fill="x")

    # API Key Entry
    global api_key_var
    api_key_var = ctk.CTkEntry(
        master=api_key_entry_frame,
        placeholder_text="Enter your API key here",
        show="*"
    )
    api_key_var.pack(side="left", padx=5, fill="x", expand=True)

    # Show/Hide API Key Button next to entry
    show_hide_button = ctk.CTkButton(
        master=api_key_entry_frame,
        text="Show API Key",
        command=toggle_api_key_visibility,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    show_hide_button.pack(side="right", padx=5)

    # Passcode Section
    passcode_label = ctk.CTkLabel(
        master=scrollable_frame,
        text="Admin Registration Passcode",
        font=("Helvetica", 20, "bold"),
        text_color="#4B0082"
    )
    passcode_label.pack(pady=(20, 10))

    # Frame for passcode entry and show/hide button
    passcode_entry_frame = ctk.CTkFrame(
        master=scrollable_frame,
        fg_color="transparent"
    )
    passcode_entry_frame.pack(pady=5, padx=10, fill="x")

    # Passcode Entry
    global passcode_var
    passcode_var = ctk.CTkEntry(
        master=passcode_entry_frame,
        placeholder_text="Enter admin registration passcode",
        show="*"
    )
    passcode_var.pack(side="left", padx=5, fill="x", expand=True)
    # Add binding for passcode changes
    passcode_var.bind("<KeyRelease>", on_passcode_change)
    passcode_var.bind("<<Paste>>", on_passcode_change)

    # Show/Hide Passcode Button
    show_hide_passcode_button = ctk.CTkButton(
        master=passcode_entry_frame,
        text="Show Passcode",
        command=lambda: toggle_passcode_visibility(passcode_var, show_hide_passcode_button),
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    show_hide_passcode_button.pack(side="right", padx=5)

    # Save Button at the bottom of scrollable frame
    save_button = ctk.CTkButton(
        master=scrollable_frame,
        text="Save Information",
        command=save_information,
        width=250,
        height=50,
        fg_color="#32CD32",
        hover_color="#2E8B57"
    )
    save_button.pack(pady=20)
    save_button.configure(state="disabled")

    # -------------------- Right Side: Image Previews --------------------
    preview_frame = ctk.CTkFrame(master=main_frame, fg_color="#E6E6FA")
    preview_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    # Preview Title
    preview_title = ctk.CTkLabel(master=preview_frame, text="Uploaded Banner Images",
                                 font=("Helvetica", 24, "bold"), text_color="#4B0082")
    preview_title.pack(pady=(20, 10))

    # Image Display Area
    image_display_frame = ctk.CTkFrame(master=preview_frame, fg_color="#FFFFFF", corner_radius=10)
    image_display_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Label to display the image
    image_label = ctk.CTkLabel(
        master=image_display_frame,
        text="No Images Uploaded",
        font=("Helvetica", 16),
        text_color="black",
        width=800,
        height=600
    )
    image_label.pack(pady=10, padx=10, fill="both", expand=True)

    # Navigation Buttons Frame
    nav_frame = ctk.CTkFrame(master=preview_frame, fg_color="#E6E6FA")
    nav_frame.pack(pady=10)

    # Back Button
    back_button = ctk.CTkButton(
        master=nav_frame,
        text="◀️ Back",
        command=show_previous_image,
        width=100,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_button.pack(side="left", padx=20)
    back_button.configure(state="disabled")

    # Next Button
    next_button = ctk.CTkButton(
        master=nav_frame,
        text="Next ▶️",
        command=show_next_image,
        width=100,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    next_button.pack(side="left", padx=20)
    next_button.configure(state="disabled")

    # Remove Image Button
    remove_button = ctk.CTkButton(
        master=nav_frame,
        text="🗑️ Remove",
        command=remove_current_image,
        width=100,
        height=50,
        fg_color="#FF6347",
        hover_color="#FF4500"
    )
    remove_button.pack(side="left", padx=20)
    remove_button.configure(state="disabled")

    # Load existing information at the end
    load_information()

def main():
    # Create main window
    root = ctk.CTk()
    root.title("System Information - Admin")
    root.geometry("1920x1080")
    root.resizable(True, True)
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Admin System Info",
        command=lambda: show_admin_system_info(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
