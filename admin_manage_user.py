import sqlite3
from tkinter import ttk, messagebox, Canvas
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
import os

# At the beginning of your file, after other imports
#current_dir = os.path.dirname(os.path.abspath(__file__))
#exclamation_icon_path = os.path.join(current_dir, "stock-vector-exclamation-mark-icon-in-a-red-circle-2309104531.png")

# Load the exclamation icon
#exclamation_icon = Image.open(exclamation_icon_path)
#exclamation_icon = exclamation_icon.resize((20, 20), Image.LANCZOS)
#exclamation_photo = ctk.CTkImage(light_image=exclamation_icon, dark_image=exclamation_icon, size=(20, 20))

# At the top of the file, after imports
global user_frame
user_frame = None

def fetch_tenants(query=None):
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()

    if query:
        cursor.execute("""
            SELECT tenantID, username, fullName, ICNumber, emailAddress, phoneNumber, icProblem 
            FROM tenants 
            WHERE username LIKE ? OR fullName LIKE ? OR ICNumber LIKE ? OR emailAddress LIKE ? OR phoneNumber LIKE ?
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
    else:
        cursor.execute("""
            SELECT tenantID, username, fullName, ICNumber, emailAddress, phoneNumber, icProblem 
            FROM tenants
        """)

    tenants = cursor.fetchall()
    connection.close()
    return tenants

def add_tenant_to_db(username, fullName, ICNumber, emailAddress, phoneNumber, password, ICImagePath, FaceImagePath):
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tenants (username, fullName, ICNumber, emailAddress, phoneNumber, password, ICImagePath, FaceImagePath) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, fullName, ICNumber, emailAddress, phoneNumber, password, ICImagePath, FaceImagePath))
    connection.commit()
    connection.close()

def delete_tenant_from_db(tenant_id):
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tenants WHERE tenantID=?", (tenant_id,))
    connection.commit()
    connection.close()

def update_tenant_in_db(tenant_id, username, fullName, ICNumber, emailAddress, phoneNumber, ICImagePath, FaceImagePath):
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tenants 
        SET username=?, fullName=?, ICNumber=?, emailAddress=?, phoneNumber=?, ICImagePath=?, FaceImagePath=?
        WHERE tenantID=?
    """, (username, fullName, ICNumber, emailAddress, phoneNumber, ICImagePath, FaceImagePath, tenant_id))
    connection.commit()
    connection.close()

def update_treeview(tenants):
    for row in treeview.get_children():
        treeview.delete(row)

    for tenant in tenants:
        values = list(tenant[:6]) + ['']  # Convert to list and add empty string for icon
        if len(tenant) > 6 and tenant[6] == '1':  # Check if icProblem exists and is '1'
            item = treeview.insert('', 'end', values=values)
            treeview.set(item, 'icon', '❗')
            treeview.item(item, tags=('ic_problem',))
        else:
            treeview.insert('', 'end', values=values)

def on_search():
    query = search_var.get()
    tenants = fetch_tenants(query=query)
    update_tenant_boxes(tenants)

def on_filter():
    query = search_var.get()
    tenants = fetch_tenants(query=query)
    update_tenant_boxes(tenants)

def on_add_tenant():
    def submit():
        username = username_var.get()
        fullName = fullName_var.get()
        ICNumber = ICNumber_var.get()
        emailAddress = emailAddress_var.get()
        phoneNumber = phoneNumber_var.get()
        password = password_var.get()
        ICImagePath = ICImagePath_var.get()
        FaceImagePath = FaceImagePath_var.get()

        add_tenant_to_db(username, fullName, ICNumber, emailAddress, phoneNumber, password, ICImagePath, FaceImagePath)
        update_tenant_boxes(fetch_tenants())
        update_tenant_counts(user_frame)  # Update the counts
        add_window.destroy()

    add_window = ctk.CTkToplevel(user_frame)
    add_window.geometry("400x700")
    add_window.title("Add Tenant")

    username_var = ctk.StringVar()
    fullName_var = ctk.StringVar()
    ICNumber_var = ctk.StringVar()
    emailAddress_var = ctk.StringVar()
    phoneNumber_var = ctk.StringVar()
    password_var = ctk.StringVar()
    ICImagePath_var = ctk.StringVar()
    FaceImagePath_var = ctk.StringVar()

    ctk.CTkLabel(add_window, text="Username").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=username_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="Full Name").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=fullName_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="IC Number").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=ICNumber_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="Email Address").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=emailAddress_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="Phone Number").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=phoneNumber_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="Password").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=password_var, show="*").pack(pady=5)

    ctk.CTkLabel(add_window, text="IC Image Path").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=ICImagePath_var).pack(pady=5)

    ctk.CTkLabel(add_window, text="Face Image Path").pack(pady=5)
    ctk.CTkEntry(add_window, textvariable=FaceImagePath_var).pack(pady=5)

    ctk.CTkButton(add_window, text="Submit", command=submit).pack(pady=20)

def on_delete_tenant(tenant_id=None):
    if tenant_id is None:
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a tenant to delete")
            return
        tenant = treeview.item(selected_item, 'values')
        tenant_id = tenant[0]

    # Ask for confirmation before deleting
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this tenant?"):
        delete_tenant_from_db(tenant_id)
        update_tenant_boxes(fetch_tenants())
        update_tenant_counts(user_frame)  # Update the counts
        messagebox.showinfo("Success", "Tenant deleted successfully")

def on_edit_tenant(tenant_id=None):
    if tenant_id is None:
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a tenant to edit")
            return
        tenant = treeview.item(selected_item, 'values')
        tenant_id = tenant[0]

    # Fetch complete tenant data including image paths
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT username, fullName, ICNumber, emailAddress, phoneNumber, ICImagePath, FaceImagePath 
        FROM tenants 
        WHERE tenantID = ?
    """, (tenant_id,))
    tenant_data = cursor.fetchone()
    connection.close()

    if tenant_data:
        def submit_edit():
            username = username_var.get()
            fullName = fullName_var.get()
            ICNumber = ICNumber_var.get()
            emailAddress = emailAddress_var.get()
            phoneNumber = phoneNumber_var.get()
            ICImagePath = ICImagePath_var.get()
            FaceImagePath = FaceImagePath_var.get()

            update_tenant_in_db(tenant_id, username, fullName, ICNumber, emailAddress, phoneNumber, ICImagePath, FaceImagePath)
            update_tenant_boxes(fetch_tenants())
            update_tenant_counts(user_frame)  # Update the counts
            edit_window.destroy()

        edit_window = ctk.CTkToplevel(user_frame)
        edit_window.geometry("400x700")
        edit_window.title("Edit Tenant")

        # Use tenant_data for the complete information
        username_var = ctk.StringVar(value=tenant_data[0])
        fullName_var = ctk.StringVar(value=tenant_data[1])
        ICNumber_var = ctk.StringVar(value=tenant_data[2])
        emailAddress_var = ctk.StringVar(value=tenant_data[3])
        phoneNumber_var = ctk.StringVar(value=tenant_data[4])
        ICImagePath_var = ctk.StringVar(value=tenant_data[5])
        FaceImagePath_var = ctk.StringVar(value=tenant_data[6])

        ctk.CTkLabel(edit_window, text="Username").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=username_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="Full Name").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=fullName_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="IC Number").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=ICNumber_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="Email Address").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=emailAddress_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="Phone Number").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=phoneNumber_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="IC Image Path").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=ICImagePath_var).pack(pady=5)

        ctk.CTkLabel(edit_window, text="Face Image Path").pack(pady=5)
        ctk.CTkEntry(edit_window, textvariable=FaceImagePath_var).pack(pady=5)

        ctk.CTkButton(edit_window, text="Submit", command=submit_edit).pack(pady=20)

    else:
        messagebox.showerror("Error", "Could not fetch tenant data")

def set_background(app, image_path):
    # Load and resize the image
    image = Image.open(image_path)
    resized_image = image.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)

    # Create a Canvas and place the image
    canvas = Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Store reference to prevent garbage collection
    canvas.image = bg_image

# Add this new function to fetch tenants with IC problems
def fetch_tenants_with_ic_problems():
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT tenantID, username, fullName, ICNumber, emailAddress, phoneNumber
        FROM tenants
        WHERE icProblem = '1'
    """)
    tenants = cursor.fetchall()
    connection.close()
    return tenants

# Add this new function to display tenants with IC problems
def show_ic_problem_tenants():
    ic_problem_window = ctk.CTkToplevel(user_frame)
    ic_problem_window.geometry("1200x800")
    ic_problem_window.title("Verify IC Problems")

    # Create main container
    main_container = ctk.CTkFrame(ic_problem_window, fg_color="#F0E6FF")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Add title
    title_label = ctk.CTkLabel(
        main_container, 
        text="IC Verification Required", 
        font=("Arial", 24, "bold"),
        text_color="#4B0082"
    )
    title_label.pack(pady=(0, 20))

    # Create scrollable frame for tenant boxes
    scroll_container = ctk.CTkScrollableFrame(
        main_container,
        fg_color="#F0E6FF",
        width=1100,
        height=600
    )
    scroll_container.pack(fill="both", expand=True)

    # Fetch tenants with IC problems
    problem_tenants = fetch_tenants_with_ic_problems()

    if not problem_tenants:
        no_problems_label = ctk.CTkLabel(
            scroll_container,
            text="No IC verification issues found!",
            font=("Arial", 20),
            text_color="#4B0082"
        )
        no_problems_label.pack(pady=50)
    else:
        for tenant in problem_tenants:
            # Create a frame for each tenant
            tenant_frame = ctk.CTkFrame(
                scroll_container,
                fg_color="white",
                corner_radius=10,
                height=150
            )
            tenant_frame.pack(fill="x", pady=10, padx=5)
            tenant_frame.pack_propagate(False)

            # Tenant details
            ctk.CTkLabel(
                tenant_frame,
                text=f"Name: {tenant[2]}",
                font=("Arial", 16, "bold")
            ).place(x=20, y=20)

            ctk.CTkLabel(
                tenant_frame,
                text=f"IC Number: {tenant[3]}",
                font=("Arial", 14)
            ).place(x=20, y=50)

            ctk.CTkLabel(
                tenant_frame,
                text=f"Email: {tenant[4]}",
                font=("Arial", 14)
            ).place(x=20, y=80)

            # Add verify button
            verify_button = ctk.CTkButton(
                tenant_frame,
                text="Verify IC",
                command=lambda t=tenant: show_tenant_images(t[0]),
                font=("Arial", 14),
                fg_color="#9370DB",
                hover_color="#7B68EE",
                width=120
            )
            verify_button.place(x=900, y=55)

    # Add close button at the bottom
    close_button = ctk.CTkButton(
        main_container,
        text="Close",
        command=ic_problem_window.destroy,
        font=("Arial", 16),
        fg_color="#FF6B6B",
        hover_color="#FF4757",
        width=200
    )
    close_button.pack(pady=20)

def show_ic_comparison(tenant_id):
    item = treeview.selection()[0]
    tenant_id = treeview.item(item, "values")[0]

    # Fetch tenant details including image paths
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT ICImagePath, FaceImagePath, fullName
        FROM tenants
        WHERE tenantID = ?
    """, (tenant_id,))
    tenant_data = cursor.fetchone()
    connection.close()

    if tenant_data:
        ic_image_path, face_image_path, full_name = tenant_data
        
        image_window = ctk.CTkToplevel(user_frame)
        image_window.geometry("960x600")
        image_window.title(f"Images for {full_name}")

        # Create a main frame
        main_frame = ctk.CTkFrame(image_window)
        main_frame.pack(fill="both", expand=True)

        # Add a title label
        title_label = ctk.CTkLabel(main_frame, text=f"Images for {full_name}", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 20))

        # Create a frame for images
        image_frame = ctk.CTkFrame(main_frame)
        image_frame.pack(fill="both", expand=True)

        # Load and display IC image
        ic_image = Image.open(ic_image_path)
        ic_image = ic_image.resize((476, 300), Image.LANCZOS)
        ic_photo = ImageTk.PhotoImage(ic_image)
        ic_label = ctk.CTkLabel(image_frame, image=ic_photo, text="")
        ic_label.image = ic_photo
        ic_label.grid(row=0, column=0, padx=10, pady=10)

        # Load and display Face image
        face_image = Image.open(face_image_path)
        face_image = face_image.resize((400, 300), Image.LANCZOS)
        face_photo = ImageTk.PhotoImage(face_image)
        face_label = ctk.CTkLabel(image_frame, image=face_photo, text="")
        face_label.image = face_photo
        face_label.grid(row=0, column=1, padx=10, pady=10)

        # Create a frame for buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)

        def on_pass():
            update_ic_problem_status(tenant_id, 0)
            image_window.destroy()
            show_ic_problem_tenants()  # Refresh the IC problem tenants list

        def on_fail():
            update_ic_problem_status(tenant_id, 1)
            image_window.destroy()

        pass_button = ctk.CTkButton(button_frame, text="Pass", command=on_pass, fg_color="green", hover_color="dark green", width=150, height=40)
        pass_button.grid(row=0, column=0, padx=10)

        fail_button = ctk.CTkButton(button_frame, text="Fail", command=on_fail, fg_color="red", hover_color="dark red", width=150, height=40)
        fail_button.grid(row=0, column=1, padx=10)

def update_ic_problem_status(tenant_id, status):
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE tenants
        SET icProblem = ?
        WHERE tenantID = ?
    """, (status, tenant_id))
    connection.commit()
    connection.close()

def show_tenant_images(tenant_id):
    # Fetch tenant details including image paths
    connection = sqlite3.connect('properties.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT ICImagePath, FaceImagePath, fullName
        FROM tenants
        WHERE tenantID = ?
    """, (tenant_id,))
    tenant_data = cursor.fetchone()
    connection.close()

    if tenant_data:
        ic_image_path, face_image_path, full_name = tenant_data
        
        # Create a new window for displaying images
        image_window = ctk.CTkToplevel(user_frame)
        image_window.geometry("960x600")
        image_window.title(f"Images for {full_name}")

        # Create a main frame
        main_frame = ctk.CTkFrame(image_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Add a title label
        title_label = ctk.CTkLabel(main_frame, text=f"Images for {full_name}", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 20))

        # Create a frame for images
        image_frame = ctk.CTkFrame(main_frame)
        image_frame.pack(fill="both", expand=True)

        try:
            # Load and display IC image
            ic_image = Image.open(ic_image_path)
            ic_image = ic_image.resize((400, 300), Image.LANCZOS)
            ic_photo = ImageTk.PhotoImage(ic_image)
            ic_label = ctk.CTkLabel(image_frame, image=ic_photo, text="")
            ic_label.image = ic_photo
            ic_label.grid(row=0, column=0, padx=10, pady=10)

            # Load and display Face image
            face_image = Image.open(face_image_path)
            face_image = face_image.resize((400, 300), Image.LANCZOS)
            face_photo = ImageTk.PhotoImage(face_image)
            face_label = ctk.CTkLabel(image_frame, image=face_photo, text="")
            face_label.image = face_photo
            face_label.grid(row=0, column=1, padx=10, pady=10)

            # Add labels under the images
            ctk.CTkLabel(image_frame, text="IC Image", font=("Arial", 14)).grid(row=1, column=0)
            ctk.CTkLabel(image_frame, text="Face Image", font=("Arial", 14)).grid(row=1, column=1)

            # Create a frame for buttons
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(pady=20)

            def on_pass():
                update_ic_problem_status(tenant_id, 0)
                image_window.destroy()
                update_treeview(fetch_tenants())  # Refresh the main treeview

            def on_fail():
                update_ic_problem_status(tenant_id, 1)
                image_window.destroy()
                update_treeview(fetch_tenants())  # Refresh the main treeview

            # Add Pass/Fail buttons
            pass_button = ctk.CTkButton(button_frame, text="Pass", command=on_pass, 
                                      fg_color="green", hover_color="dark green",
                                      width=150, height=40)
            pass_button.grid(row=0, column=0, padx=10)

            fail_button = ctk.CTkButton(button_frame, text="Fail", command=on_fail,
                                      fg_color="red", hover_color="dark red",
                                      width=150, height=40)
            fail_button.grid(row=0, column=1, padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading images: {str(e)}")
            image_window.destroy()
    else:
        messagebox.showerror("Error", "Tenant images not found")

def create_tenant_box(parent_frame, tenant_data, y_position):
    # Create box frame with outline
    box_frame = ctk.CTkFrame(
        parent_frame, 
        fg_color="#E6E6FA", 
        corner_radius=10, 
        width=1200, 
        height=150,
        border_width=2,
        border_color="#9370DB"
    )
    box_frame.pack(pady=10, padx=50)
    box_frame.pack_propagate(False)

    # Username label with larger font
    username_label = ctk.CTkLabel(
        box_frame,
        text=f"{tenant_data[1]}",  # username
        font=("Arial", 20, "bold"),
        text_color="#4B0082"
    )
    username_label.place(x=20, y=10)

    # Tenant ID with larger font
    tenant_id_label = ctk.CTkLabel(
        box_frame,
        text=f"ID: {tenant_data[0]}",
        font=("Arial", 18),
        text_color="black"
    )
    tenant_id_label.place(x=500, y=10)

    # Tenant name with larger font
    tenant_name = ctk.CTkLabel(
        box_frame,
        text=f"Tenant: {tenant_data[2]}",
        font=("Arial", 18),
        text_color="black"
    )
    tenant_name.place(x=20, y=40)

    # Phone Number with larger font
    phone_label = ctk.CTkLabel(
        box_frame,
        text=f"Phone: {tenant_data[5]}",
        font=("Arial", 18),
        text_color="black"
    )
    phone_label.place(x=500, y=40)

    # IC Number with larger font
    ic_number = ctk.CTkLabel(
        box_frame,
        text=f"IC: {tenant_data[3]}",
        font=("Arial", 18),
        text_color="black"
    )
    ic_number.place(x=20, y=70)

    # Email with larger font
    email_label = ctk.CTkLabel(
        box_frame,
        text=f"Email: {tenant_data[4]}",
        font=("Arial", 18),
        text_color="black"
    )
    email_label.place(x=500, y=70)

    # Edit button with larger font
    edit_btn = ctk.CTkButton(
        box_frame,
        text="Edit Tenant",
        font=("Arial", 16),
        width=120,
        height=35,
        fg_color="#9370DB",
        hover_color="#7B68EE",
        command=lambda: on_edit_tenant(tenant_data[0])
    )
    edit_btn.place(x=1000, y=20)

    # Delete button with larger font
    delete_btn = ctk.CTkButton(
        box_frame,
        text="Delete Tenant",
        font=("Arial", 16),
        width=120,
        height=35,
        fg_color="#FF0000",
        hover_color="#CC0000",
        command=lambda: on_delete_tenant(tenant_data[0])
    )
    delete_btn.place(x=1000, y=60)

    # Add Verify IC button if tenant has IC problem
    if len(tenant_data) > 6 and tenant_data[6] == '1':
        verify_ic_btn = ctk.CTkButton(
            box_frame,
            text="Verify IC",
            font=("Arial", 16),
            width=120,
            height=35,
            fg_color="#FF6B6B",  # Red color to indicate issues
            hover_color="#FF4757",
            command=lambda: show_tenant_images(tenant_data[0])
        )
        verify_ic_btn.place(x=1000, y=100)

        # Add warning icon
        warning_label = ctk.CTkLabel(
            box_frame,
            text="❗",
            font=("Arial", 28),
            text_color="red"
        )
        warning_label.place(x=900, y=60)

def update_tenant_boxes(tenants):
    # Clear existing boxes
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    if not tenants:  # If tenants list is empty
        # Create a message frame
        message_frame = ctk.CTkFrame(scrollable_frame, fg_color="#F0E6FF", width=1200, height=150)
        message_frame.pack(pady=10, padx=50)
        message_frame.pack_propagate(False)

        # Add the "No results found!" message
        message_label = ctk.CTkLabel(
            message_frame,
            text="No results found!",
            font=("Arial", 24, "bold"),
            text_color="#4B0082"
        )
        message_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Set minimum height for scrollable frame
        scrollable_frame.configure(height=600)
    else:
        # Create boxes for each tenant as before
        for tenant in tenants:
            create_tenant_box(scrollable_frame, tenant, 0)

        # Update scrollable frame size
        total_height = len(tenants) * 170  # 150 for box height + 20 for padding
        scrollable_frame.configure(height=max(total_height, 600))  # Minimum height of 600

# Replace the treeview creation code with this
def create_scrollable_tenant_list(user_frame):
    global scrollable_frame

    # Create a canvas for scrolling
    canvas = tk.Canvas(user_frame, bg="#F0E6FF", highlightthickness=0, width=1300, height=600)
    canvas.place(x=550, y=300)

    # Create a scrollbar
    scrollbar = ttk.Scrollbar(user_frame, orient="vertical", command=canvas.yview)
    scrollbar.place(x=1850, y=300, height=600)

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas for the tenant boxes
    scrollable_frame = ctk.CTkFrame(canvas, width=1300, height=600, fg_color="#F0E6FF")
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1300)

    # Update scroll region when the frame size changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Ensure the frame stays the full width of the canvas
        canvas.itemconfig(canvas_window, width=canvas.winfo_width())
    
    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Bind mouse wheel to scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    return scrollable_frame

# Update the show_admin_manage_user function
def show_admin_manage_user(root, home_frame, show_dashboard_callback):
    global user_frame
    home_frame.pack_forget()
    
    # Create main frame with light purple background
    user_frame = ctk.CTkFrame(root, fg_color="#F0E6FF")
    user_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        user_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=user_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)

    # Remove background image setting
    # set_background(user_frame, "preview16.jpg")
    
    global search_var, treeview
    
    header_label = ctk.CTkLabel(user_frame, text="👤User Management", font=("Arial", 40, "bold"), text_color="black")
    header_label.place(x=50, y=100)
    
    # Search entry and button - aligned with right edge of boxes
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(user_frame, textvariable=search_var, placeholder_text="Search Tenant", font=("Arial", 20), width=400, height=50)
    search_entry.place(x=1325, y=120, anchor='n')  # Adjusted x coordinate
    
    search_button = ctk.CTkButton(
        user_frame, 
        text="🔍", 
        text_color="brown", 
        font=("Arial", 20), 
        width=60, 
        height=50, 
        command=on_search, 
        fg_color="#e1dad2", 
        hover_color="#c89ef2"
    )
    search_button.place(x=1550, y=120)  # Adjusted x coordinate
    
    # Add Tenant button - updated position
    add_button = ctk.CTkButton(
        user_frame, 
        text="Add Tenant", 
        text_color="white",
        font=("Arial", 20), 
        width=200, 
        height=50, 
        command=on_add_tenant, 
        fg_color="#9370DB",  # Light purple matching the boxes
        hover_color="#9370DB"  # Darker purple for hover
    )
    add_button.place(x=1630, y=120)  # Adjusted x coordinate
    
    # Stats frames with darker purple outline
    total_tenant_frame = ctk.CTkFrame(user_frame, width=280, height=250, 
                                    fg_color="white", 
                                    corner_radius=15,
                                    border_width=2,
                                    border_color="#9370DB")  # Dark purple outline
    total_tenant_frame.place(x=100, y=300)
    total_tenant_frame.pack_propagate(False)  # Prevent frame from resizing
    
    total_tenant_label = ctk.CTkLabel(total_tenant_frame, text="Total Tenants", font=('Arial', 24))
    total_tenant_label.place(x=60, y=30)
    
    total_tenant_count = len(fetch_tenants())
    total_count_label = ctk.CTkLabel(total_tenant_frame, text=f"{total_tenant_count}", font=('Arial', 50))
    total_count_label.place(x=130, y=100)
    
    # Problem Users frame with matching outline
    problem_tenant_frame = ctk.CTkFrame(user_frame, width=280, height=250, 
                                      fg_color="white", 
                                      corner_radius=15,
                                      border_width=2,
                                      border_color="#9370DB")  # Dark purple outline
    problem_tenant_frame.place(x=100, y=600)
    problem_tenant_frame.pack_propagate(False)
    
    problem_tenant_label = ctk.CTkLabel(problem_tenant_frame, text="Problem Tenants", font=('Arial', 24))
    problem_tenant_label.place(x=60, y=30)
    
    # Get the count of problem tenants (where icProblem = '1')
    problem_tenant_count = len(fetch_tenants_with_ic_problems())
    problem_count_label = ctk.CTkLabel(problem_tenant_frame, text=f"{problem_tenant_count}", font=('Arial', 50))
    problem_count_label.place(x=130, y=100)
    
    # Replace treeview creation with scrollable tenant list
    create_scrollable_tenant_list(user_frame)
    
    # Update the display with initial data
    update_tenant_boxes(fetch_tenants())

# Add these new functions for approve/reject actions
def on_approve(tenant_id):
    # Implement approval logic here
    messagebox.showinfo("Success", f"Approved tenant {tenant_id}")
    update_tenant_boxes(fetch_tenants())

def on_reject(tenant_id):
    # Implement rejection logic here
    messagebox.showinfo("Success", f"Rejected tenant {tenant_id}")
    update_tenant_boxes(fetch_tenants())

def update_tenant_counts(user_frame):
    # Find the count labels in their respective frames
    total_tenant_count = len(fetch_tenants())
    problem_tenant_count = len(fetch_tenants_with_ic_problems())
    
    # Update both counts
    for widget in user_frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and widget.winfo_width() == 280 and widget.winfo_height() == 250:
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel) and child.cget("font")[1] == 50:
                    parent_frame = child.master
                    frame_labels = [label.cget("text") for label in parent_frame.winfo_children() 
                                  if isinstance(label, ctk.CTkLabel)]
                    
                    if "Total Tenants" in frame_labels:
                        child.configure(text=str(total_tenant_count))
                    elif "Problem Tenants" in frame_labels:
                        child.configure(text=str(problem_tenant_count))

def main():
    root = ctk.CTk()
    root.title("Admin Manage User")
    root.geometry("1920x1080")
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open User Management",
        command=lambda: show_admin_manage_user(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()

























