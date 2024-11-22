import customtkinter as ctk
from tkintermapview import TkinterMapView
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from deepface import DeepFace
from tkinter import filedialog
from tkcalendar import Calendar
from datetime import datetime, timedelta

# Define color constants
LIGHT_PURPLE = "#F0E6FF"
DARK_PURPLE = "#4A3F75"
MUTED_LIGHT_PURPLE = "#D1C2F0"

# Set the appearance mode and default color theme
ctk.set_appearance_mode("light")

# Add at the top of the file with other imports and constants
current_date = datetime.now().strftime('%Y-%m-%d')  # Global variable for selected date

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('properties.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_all_properties():
    """Retrieve all properties from the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT cp.id, cp.latitude, cp.longitude, cp.status, cp.addressLine1, cp.addressLine2, 
                   cp.postcode, cp.city, cp.state, cp.sqft, cp.price, r.stallName,
                   t.fullName, t.ICNumber, r.startOperatingTime, r.endOperatingTime
            FROM combined_properties cp
            LEFT JOIN rental r ON cp.id = r.combined_properties_id
            LEFT JOIN tenants t ON r.tenantID = t.tenantID
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving properties: {e}")
        finally:
            conn.close()
    return []

def get_marker_color(status, rental_id=None, selected_date=None):
    """Determine marker color based on daily check-in status"""
    # If no rental_id or date provided, show gray
    if not rental_id or not selected_date:
        return "gray"
    
    conn = None
    try:
        conn = sqlite3.connect('properties.db', timeout=20)
        cursor = conn.cursor()
        
        # First check if this is an approved rental
        cursor.execute("""
            SELECT startOperatingTime 
            FROM rental 
            WHERE rentalID = ? AND isApprove = 1
        """, (rental_id,))
        
        rental_result = cursor.fetchone()
        if not rental_result:
            return "gray"  # Not an approved rental
            
        start_time = rental_result[0]
        
        # Get the check-in status for the selected date
        cursor.execute('''
            SELECT checkInStatus, date
            FROM dailyCheckInStatus 
            WHERE rentalID = ? AND date LIKE ?
            ORDER BY date DESC LIMIT 1
        ''', (rental_id, f"{selected_date}%"))
        
        result = cursor.fetchone()
        
        if result:
            daily_status = int(result[0])
            
            # Unified status colors - status 5 uses red like status 4
            status_colors = {
                1: "green",    # Check-in Successfully
                2: "yellow",   # Camera verification passed, Location failed
                3: "orange",   # Location verification passed, Camera failed
                4: "red",      # Both verifications failed
                5: "red"       # Exceeded time check-in failed (same color as status 4)
            }
            
            return status_colors.get(daily_status, "gray")
        else:
            # Check if we should show it as failed (past deadline with no check-in)
            current_datetime = datetime.now()
            selected_datetime = datetime.strptime(f"{selected_date} {start_time}", '%Y-%m-%d %H:%M')
            deadline_datetime = selected_datetime + timedelta(minutes=30)
            
            # If selected date is today and past deadline, or if it's a past date
            if (selected_date == current_datetime.strftime('%Y-%m-%d') and 
                current_datetime > deadline_datetime) or \
               (datetime.strptime(selected_date, '%Y-%m-%d').date() < current_datetime.date()):
                return "red"  # Show as failed
            
            return "gray"  # No check-in record yet and not past deadline
            
    except sqlite3.Error as e:
        print(f"Database error retrieving status: {e}")
        return "gray"
    except Exception as e:
        print(f"Error determining marker color: {e}")
        return "gray"
    finally:
        if conn:
            conn.close()

def show_stall_details(stall_info, info_frame, map_widget, properties, main_frame):
    """Display stall details in the info frame using text boxes with auto line-changing"""
    # Clear previous information
    for widget in info_frame.winfo_children():
        widget.destroy()

    try:
        (stall_id, _, _, status, address1, address2, postcode, city, state, sqft, price, 
         stall_name, tenant_name, tenant_ic, start_time, end_time) = stall_info
    except ValueError:
        messagebox.showerror("Error", "Incomplete stall information.")
        return

    ctk.CTkLabel(info_frame, text="Stall Information", font=("Arial", 24, "bold"), text_color=DARK_PURPLE).pack(pady=(20, 30))

    def create_text_pair(parent, label, value, height=2):
        frame = ctk.CTkFrame(parent, fg_color=LIGHT_PURPLE)
        frame.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(frame, text=label, font=("Arial", 16, "bold"), text_color=DARK_PURPLE, width=150, anchor="e").pack(side="left", padx=(0, 10))
        text_box = ctk.CTkTextbox(frame, font=("Arial", 16), text_color="black", width=300, height=height*24, wrap="word")
        text_box.pack(side="left", fill="x", expand=True)
        text_box.insert("1.0", value)
        text_box.configure(state="disabled")
        return text_box

    create_text_pair(info_frame, "Stall Name:", stall_name or "N/A")
    create_text_pair(info_frame, "Stall ID:", str(stall_id))
    
    # Add Rental ID
    rental_id = get_rental_id(stall_id)
    create_text_pair(info_frame, "Rental ID:", str(rental_id) if rental_id else "N/A")
    
    # Format location as multiple lines
    location = f"{address1}\n{address2}\n{postcode} {city}, {state}"
    create_text_pair(info_frame, "Location:", location, height=4)
    
    create_text_pair(info_frame, "Size:", f"{sqft} sqft")
    create_text_pair(info_frame, "Price:", f"RM {price:.2f}/month")
    create_text_pair(info_frame, "Tenant Name:", tenant_name or "N/A")
    create_text_pair(info_frame, "Tenant IC:", tenant_ic or "N/A")
    create_text_pair(info_frame, "Operating Hours:", f"{start_time} - {end_time}" if start_time and end_time else "N/A")
    
    # Get the current selected date from the calendar
    selected_date = current_date  # This is the global variable storing selected date
    
    # Get check-in status from dailyCheckInStatus for the selected date
    conn = None
    try:
        conn = sqlite3.connect('properties.db', timeout=20)
        cursor = conn.cursor()
        
        # First check if this is an approved rental
        cursor.execute("""
            SELECT startOperatingTime 
            FROM rental 
            WHERE rentalID = ? AND isApprove = 1
        """, (rental_id,))
        
        rental_result = cursor.fetchone()
        if rental_result:
            start_time = rental_result[0]
            
            # Get check-in record for the selected date
            cursor.execute('''
                SELECT checkInStatus, date
                FROM dailyCheckInStatus 
                WHERE rentalID = ? AND date LIKE ?
                ORDER BY date DESC LIMIT 1
            ''', (rental_id, f"{selected_date}%"))
            
            result = cursor.fetchone()
            
            # Parse times and calculate deadline
            start_hour = int(start_time.split(':')[0])
            start_minute = int(start_time.split(':')[1])
            
            # Calculate deadline time (30 minutes after start time)
            deadline_minute = start_minute + 30
            deadline_hour = start_hour
            if deadline_minute >= 60:
                deadline_hour += 1
                deadline_minute -= 60
            
            deadline_time = f"{deadline_hour:02d}:{deadline_minute:02d}"
            deadline_datetime = datetime.strptime(f"{selected_date} {deadline_time}", '%Y-%m-%d %H:%M')
            current_datetime = datetime.now()
            
            # Define status text based on conditions
            if result:
                daily_status = int(result[0])
                status_text = {
                    1: "Check-in Successfully",
                    2: "Partially Check-in\nCamera verification passed",
                    3: "Partially Check-in\nLocation verification passed",
                    4: "Check-in Failed",
                    5: "Check-in Failed\n(Exceeded Time Limit)"
                }.get(daily_status, f"Unknown Status ({daily_status})")
                
                # Add manual verification button if camera verification failed (status 3 or 4)
                if daily_status in [3, 4]:
                    manual_verify_btn = ctk.CTkButton(
                        info_frame,
                        text="Manual Verification",
                        command=lambda: show_manual_verification(rental_id, tenant_name, map_widget, properties, main_frame, info_frame),
                        font=("Arial", 16),
                        fg_color="#9370DB",
                        hover_color="#8A2BE2"
                    )
                    manual_verify_btn.pack(pady=10)
            else:
                # Check if we're past the deadline
                if (selected_date == current_datetime.strftime('%Y-%m-%d') and 
                    current_datetime > deadline_datetime) or \
                   (datetime.strptime(selected_date, '%Y-%m-%d').date() < current_datetime.date()):
                    status_text = f"No check-in record after {start_time}\n(30-minute deadline exceeded)\nStatus: Failed"
                else:
                    # If it's today but before deadline
                    if selected_date == current_datetime.strftime('%Y-%m-%d'):
                        time_until_deadline = deadline_datetime - current_datetime
                        minutes_left = int(time_until_deadline.total_seconds() / 60)
                        if minutes_left > 0:
                            status_text = f"Check-in deadline: {start_time}\n({minutes_left} minutes remaining)"
                        else:
                            status_text = "Check-in deadline approaching"
                    else:
                        # Future date
                        status_text = f"Check-in deadline will be {start_time}\n(30 minutes allowed)"
        else:
            status_text = "Not an approved rental"
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        status_text = "Error retrieving check-in status"
    finally:
        if conn:
            conn.close()
    
    create_text_pair(info_frame, "Check-in Status:", status_text, height=3)

    # Make the info frame visible
    info_frame.grid()

def update_verification_status(rental_id, passed, verification_window):
    """Update dailyCheckInStatus table after manual verification"""
    conn = None
    try:
        conn = sqlite3.connect('properties.db', timeout=20)
        cursor = conn.cursor()
        
        # First get the current status from dailyCheckInStatus
        cursor.execute('''
        SELECT checkInStatus 
        FROM dailyCheckInStatus 
        WHERE rentalID = ? AND date = ?
        ''', (rental_id, current_date))  # Use global current_date
        
        result = cursor.fetchone()
        if result:
            current_status = int(result[0])
            print(f"Current status: {current_status}")  # Debug print
            
            # Determine new status based on current status and verification result
            if passed:
                if current_status == 3:  # Location passed, camera failed
                    new_status = 1  # Both passed
                elif current_status == 4:  # Both failed
                    new_status = 2  # Only camera passed
                else:
                    new_status = current_status  # Keep current status for other cases
            else:
                if current_status == 3:  # Location passed, camera failed
                    new_status = 3  # Keep status (camera still failed)
                elif current_status == 4:  # Both failed
                    new_status = 4  # Keep status (still failed)
                else:
                    new_status = current_status  # Keep current status for other cases
            
            print(f"New status to be set: {new_status}")  # Debug print
            
            # Update dailyCheckInStatus
            cursor.execute('''
            UPDATE dailyCheckInStatus 
            SET checkInStatus = ? 
            WHERE rentalID = ? AND date = ?
            ''', (new_status, rental_id, current_date))
            
            print(f"Rows affected: {cursor.rowcount}")  # Debug print
            
            conn.commit()
            verification_window.destroy()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"Verification status updated successfully to {new_status}")
                return new_status
            else:
                messagebox.showwarning("Warning", "No records were updated")
                return None
            
        else:
            messagebox.showerror("Error", "No check-in record found for today")
            return None
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()

def show_manual_verification(rental_id, tenant_name, map_widget, properties, main_frame, info_frame):
    verification_window = ctk.CTkToplevel()
    verification_window.title(f"Manual Verification - Rental ID: {rental_id}")
    verification_window.geometry("880x750")
    verification_window.configure(fg_color=LIGHT_PURPLE)

    ctk.CTkLabel(verification_window, text=f"Tenant: {tenant_name}", font=("Arial", 20, "bold"), text_color=DARK_PURPLE).pack(pady=20)

    image_frame = ctk.CTkFrame(verification_window, fg_color=MUTED_LIGHT_PURPLE)
    image_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Load and display entity face image
    entity_image_path = get_entity_face_image_path(rental_id)
    if entity_image_path:
        entity_image = load_and_resize_image(entity_image_path, (400, 300))
        ctk.CTkLabel(image_frame, image=entity_image, text="").grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(image_frame, text="Entity Face Image", font=("Arial", 14)).grid(row=1, column=0)
    else:
        ctk.CTkLabel(image_frame, text="Entity Image Not Found", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)

    # Load and display failed verification image
    failed_image_path = get_failed_verification_image_path(rental_id)
    if failed_image_path:
        failed_image = load_and_resize_image(failed_image_path, (400, 300))
        ctk.CTkLabel(image_frame, image=failed_image, text="").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(image_frame, text="Failed Verification Image", font=("Arial", 14)).grid(row=1, column=1)
    else:
        ctk.CTkLabel(image_frame, text="Failed Verification Image Not Found", font=("Arial", 14)).grid(row=0, column=1, padx=10, pady=10)

    # Add upload button and result label
    upload_button = ctk.CTkButton(
        verification_window,
        text="Upload New Image for Comparison",
        command=lambda: upload_and_compare(entity_image_path, verification_window, rental_id, map_widget, properties, main_frame, info_frame),
        font=("Arial", 16),
        fg_color="#9370DB",
        hover_color="#8A2BE2"
    )
    upload_button.pack(pady=10)

    global comparison_result_label
    comparison_result_label = ctk.CTkLabel(verification_window, text="", font=("Arial", 16))
    comparison_result_label.pack(pady=10)

    button_frame = ctk.CTkFrame(verification_window, fg_color=LIGHT_PURPLE)
    button_frame.pack(pady=20)

    def handle_verification(passed):
        new_status = update_verification_status(rental_id, passed, verification_window)
        if new_status is not None:
            print(f"Status updated to: {new_status}")  # Debug print
            # Refresh the map with current date to show updated status
            refresh_map(map_widget, properties, main_frame, info_frame, current_date)
            # Update the info panel
            try:
                stall_info = next(p for p in properties if get_rental_id(p[0]) == rental_id)
                show_stall_details(stall_info, info_frame, map_widget, properties, main_frame)
            except StopIteration:
                print(f"Could not find property for rental ID: {rental_id}")

    ctk.CTkButton(button_frame, text="Pass", command=lambda: handle_verification(True),
                  font=("Arial", 16), fg_color="green", hover_color="dark green").pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Fail", command=lambda: handle_verification(False),
                  font=("Arial", 16), fg_color="red", hover_color="dark red").pack(side="left", padx=10)

def upload_and_compare(entity_image_path, window, rental_id, map_widget, properties, main_frame, info_frame):
    if not entity_image_path:
        messagebox.showerror("Error", "Entity face image not found.")
        return

    new_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not new_image_path:
        return  # User cancelled the file dialog

    try:
        # Perform face verification using DeepFace
        result = DeepFace.verify(
            img1_path=entity_image_path, 
            img2_path=new_image_path, 
            model_name="VGG-Face",
            enforce_detection=False  # Add this to be more lenient with face detection
        )
        
        # Find the image frame
        image_frame = None
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == MUTED_LIGHT_PURPLE:
                image_frame = widget
                break

        if image_frame:
            # Clear existing widgets in the second column
            for widget in image_frame.grid_slaves(column=1):
                widget.grid_forget()

            # Load and display the new uploaded image
            try:
                new_image = load_and_resize_image(new_image_path, (400, 300))
                new_image_label = ctk.CTkLabel(image_frame, image=new_image, text="")
                new_image_label.grid(row=0, column=1, padx=10, pady=10)
                new_image_label.image = new_image  # Keep a reference
                ctk.CTkLabel(image_frame, text="New Uploaded Image", font=("Arial", 14)).grid(row=1, column=1)
            except Exception as img_error:
                print(f"Error loading image: {img_error}")
                messagebox.showerror("Error", "Failed to load the uploaded image")
                return

        # Update verification result
        if result.get("verified", False):
            similarity = result.get("distance", 0)
            verification_text = f"Face Verified! Similarity: {1 - similarity:.2%}"
            text_color = "green"
        else:
            verification_text = "Face Verification Failed"
            text_color = "red"

        # Update the comparison result label
        global comparison_result_label
        comparison_result_label.configure(text=verification_text, text_color=text_color)

    except Exception as e:
        print(f"Verification error: {str(e)}")
        messagebox.showerror("Error", "Face verification failed. Please ensure the image contains a clear face.")

def get_entity_face_image_path(rental_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT t.FaceImagePath
            FROM rental r
            JOIN tenants t ON r.tenantID = t.tenantID
            WHERE r.rentalID = ?
            ''', (rental_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print(f"No face image found for rental ID: {rental_id}")
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return None

def get_failed_verification_image_path(rental_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT imagePath
            FROM verificationFailedTenantPictures
            WHERE rentalID = ?
            ORDER BY date DESC
            LIMIT 1
            ''', (rental_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print(f"No failed verification image found for rental ID: {rental_id}")
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return None

def load_and_resize_image(image_path, size):
    img = Image.open(image_path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def refresh_map(map_widget, properties, main_frame, info_frame, selected_date=None):
    """Refresh the map with updated markers"""
    # Clear existing markers
    map_widget.delete_all_marker()
    print(f"Refreshing map for date: {selected_date}")  # Debug print

    # Add markers for each property
    for prop in properties:
        stall_id, latitude, longitude, status, *_, stall_name = prop[:12]
        rental_id = get_rental_id(stall_id)
        
        # Debug prints
        print(f"Stall ID: {stall_id}, Rental ID: {rental_id}")
        
        color = get_marker_color(status, rental_id, selected_date)
        print(f"Marker color for stall {stall_id}: {color}")  # Debug print
        
        def create_command(p):
            return lambda marker: (
                show_stall_details(p, info_frame, map_widget, properties, main_frame), 
                main_frame.grid_columnconfigure(0, weight=3),
                main_frame.grid_columnconfigure(1, weight=0),
                info_frame.grid(),
                map_widget.set_width(1420)
            )
        
        marker_text = stall_name if stall_name else f"Stall {stall_id}"
        
        marker = map_widget.set_marker(
            latitude, 
            longitude, 
            text=marker_text,
            marker_color_outside=color, 
            marker_color_circle=color,
            command=create_command(prop)
        )

def update_not_completed_verification_status():
    """
    Check and update verification status for rentals that haven't checked in
    after 30 minutes of their start operating time
    """
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # Get current date and time
        current_datetime = datetime.now()
        current_date = current_datetime.strftime('%Y-%m-%d')
        
        # Get all approved rentals
        cursor.execute("""
            SELECT 
                r.rentalID,
                r.startOperatingTime,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 
                        FROM dailyCheckInStatus d 
                        WHERE d.rentalID = r.rentalID 
                        AND d.date LIKE ?
                    ) THEN 1 
                    ELSE 0 
                END as has_check_in
            FROM rental r
            WHERE r.isApprove = 1
            AND r.startDate <= ?
            AND r.endDate >= ?
        """, (f"{current_date}%", current_date, current_date))
        
        rentals = cursor.fetchall()
        
        for rental_id, start_time, has_check_in in rentals:
            try:
                # Parse the start time
                start_hour = int(start_time.split(':')[0])
                start_minute = int(start_time.split(':')[1])
                
                # Calculate deadline time (30 minutes after start time)
                deadline_minute = start_minute + 30
                deadline_hour = start_hour
                if deadline_minute >= 60:
                    deadline_hour += 1
                    deadline_minute -= 60
                
                # Create deadline datetime
                deadline_time = f"{deadline_hour:02d}:{deadline_minute:02d}"
                deadline_datetime = datetime.strptime(f"{current_date} {deadline_time}", '%Y-%m-%d %H:%M')
                
                # Check if current time is past deadline and no check-in record exists
                if current_datetime > deadline_datetime and not has_check_in:
                    # Insert failed check-in status with status 5 for exceeded time
                    try:
                        cursor.execute("""
                            INSERT INTO dailyCheckInStatus (rentalID, date, checkInStatus)
                            VALUES (?, ?, 5)
                        """, (rental_id, current_datetime.strftime('%Y-%m-%d %H:%M:%S')))
                        
                        # Also update combined_properties status
                        cursor.execute("""
                            UPDATE combined_properties 
                            SET status = 5 
                            WHERE id = (
                                SELECT combined_properties_id 
                                FROM rental 
                                WHERE rentalID = ?
                            )
                        """, (rental_id,))
                        
                        conn.commit()
                        print(f"Updated status for rental {rental_id} to exceeded time check-in (Deadline was {deadline_time})")
                        
                    except sqlite3.IntegrityError:
                        # Record already exists for this date
                        conn.rollback()
                        print(f"Check-in record already exists for rental {rental_id}")
                        
            except ValueError as e:
                print(f"Error processing time for rental {rental_id}: {e}")
                continue
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def show_stalls_on_map():
    # Call the update function first
    update_not_completed_verification_status()
    
    global current_date  # Declare we're using the global variable
    
    # Create the main window
    root = ctk.CTk()
    root.title("Stalls Map")
    
    # Make it fullscreen
    root.attributes('-fullscreen', True)
    
    # Add escape key binding to exit fullscreen
    def exit_fullscreen(event=None):
        root.quit()  # Stop the mainloop
        root.destroy()  # Destroy the window
    
    root.bind('<Escape>', exit_fullscreen)
    
    # Create exit button first so it's on top
    exit_btn = ctk.CTkButton(
        root,
        text="✕",
        command=exit_fullscreen,
        width=40,
        height=40,
        fg_color="red",
        hover_color="darkred",
        font=ctk.CTkFont(size=18, weight="bold"),
        corner_radius=6
    )
    exit_btn.place(x=root.winfo_screenwidth()-60, y=5)

    # Set the background color to light purple
    root.configure(fg_color=LIGHT_PURPLE)

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Create a frame for the date selection at the top with reduced width
    date_frame = ctk.CTkFrame(root, fg_color=LIGHT_PURPLE)
    date_frame.pack(fill="x", padx=(20, 100), pady=10)  # Added right padding of 100 pixels
    
    # Create a frame for the collapsed view
    collapsed_frame = ctk.CTkFrame(date_frame, fg_color=LIGHT_PURPLE)
    collapsed_frame.pack(fill="x")
    
    # Create a frame for the expanded view (calendar)
    expanded_frame = ctk.CTkFrame(date_frame, fg_color=LIGHT_PURPLE)
    
    # Create label for current date display using the global current_date
    current_date_label = ctk.CTkLabel(
        collapsed_frame, 
        text=f"Current Date: {current_date}", 
        font=("Arial", 16, "bold"), 
        text_color=DARK_PURPLE
    )
    current_date_label.pack(side="left", padx=20)
    
    # Create the calendar widget in expanded frame with today's date selected
    cal = Calendar(
        expanded_frame,
        selectmode='day',
        date_pattern='yyyy-mm-dd',
        showweeknumbers=False,
        background='white',
        foreground='black',
        selectforeground='white',
        selectbackground=DARK_PURPLE,
        width=20,
        height=2
    )
    cal.pack(side="left", padx=20)
    
    def toggle_calendar():
        if expanded_frame.winfo_viewable():
            # Collapse
            expanded_frame.pack_forget()
            toggle_btn.configure(text="▼ Show Calendar")
        else:
            # Expand
            expanded_frame.pack(fill="x", pady=(5, 0))
            toggle_btn.configure(text="▲ Hide Calendar")
    
    def on_date_select():
        global current_date  # Declare we're modifying the global variable
        selected_date = cal.get_date()
        current_date = selected_date  # Update the global variable
        current_date_label.configure(text=f"Current Date: {current_date}")
        print(f"Selected Date: {selected_date}")
        # Refresh the map with the new date
        refresh_map(map_widget, properties, main_frame, info_frame, selected_date)
        # Collapse the calendar after selection
        expanded_frame.pack_forget()
        toggle_btn.configure(text="▲ Hide Calendar")

    # Add toggle button
    toggle_btn = ctk.CTkButton(
        collapsed_frame,
        text="▼ Show Calendar",
        command=toggle_calendar,
        font=("Arial", 16),
        fg_color="#9370DB",
        hover_color="#8A2BE2",
        width=150
    )
    toggle_btn.pack(side="left", padx=20)

    # Add update button
    select_date_btn = ctk.CTkButton(
        expanded_frame,
        text="Update Map",
        command=on_date_select,
        font=("Arial", 16),
        fg_color="#9370DB",
        hover_color="#8A2BE2"
    )
    select_date_btn.pack(side="left", padx=20)

    # Create the frame to hold the map and info panel
    main_frame = ctk.CTkFrame(root, fg_color=LIGHT_PURPLE)
    main_frame.pack(fill="both", expand=True)

    # Create the map widget with screen-adjusted dimensions
    map_width = int(screen_width * 0.75)  # 75% of screen width when info panel is hidden
    map_height = screen_height - 100  # Adjust for top bar
    map_widget = TkinterMapView(main_frame, width=map_width, height=map_height, corner_radius=0)
    map_widget.grid(row=0, column=0, sticky="nsew")

    # Create the info panel with screen-adjusted dimensions
    info_frame = ctk.CTkFrame(main_frame, width=int(screen_width * 0.25), height=map_height, fg_color=LIGHT_PURPLE)
    info_frame.grid(row=0, column=1, sticky="nsew")
    info_frame.grid_remove()  # Hide the info panel initially
    info_frame.grid_propagate(False)  # Prevent the frame from resizing

    # Configure the grid
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=0)
    main_frame.grid_rowconfigure(0, weight=1)

    # Set the map to center on Malaysia
    map_widget.set_position(4.2105, 101.9758)
    map_widget.set_zoom(6)

    # Get all properties from the database
    properties = get_all_properties()

    # Initial map population with today's date
    refresh_map(map_widget, properties, main_frame, info_frame, current_date)

    # Run the application
    root.mainloop()

# Add this new function to get the rental ID
def get_rental_id(stall_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT rentalID
            FROM rental
            WHERE combined_properties_id = ?
            ''', (stall_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return None

def update_info_panel(info_frame, new_status, rental_id):
    status_text = {
        0: "New Stall",
        1: "Check-in Successfully",
        2: "Partially Check-in\nLocation verification failed",
        3: "Partially Check-in\nCamera verification failed",
        4: "Check-in Failed",
        5: "Check-in Failed\n(Exceeded Time Limit)"
    }.get(new_status, "Unknown Status")

    # Find and update the check-in status label
    for widget in info_frame.winfo_children():
        if isinstance(widget, ctk.CTkTextbox) and widget.get("1.0", "end-1c").startswith("Check-in Status:"):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", f"Check-in Status: {status_text}")
            widget.configure(state="disabled")
            break

    # Remove the manual verification button if status is now 1 or 2
    if new_status in [1, 2]:
        for widget in info_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Manual Verification":
                widget.destroy()
                break

if __name__ == "__main__":
    show_stalls_on_map()
