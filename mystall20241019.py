import customtkinter as ctk
from PIL import Image, ImageTk
import sqlite3
from tkinter import messagebox
import datetime
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import ttk
import sys
from get_rental_info import get_rental_information, start_verification_process, main
import subprocess
import os


ctk.set_appearance_mode("Light")
# Add these color definitions after the imports
# Define colors to match the beige/brown theme
HEADER_COLOR = "#E7D7C7"  # Light beige for header (My Store color)
BACKGROUND_COLOR = "#fffcf7"  # Very light beige for background
BUTTON_COLOR = "#c2b8ae"  # Muted beige for buttons
HOVER_COLOR = "#c89ef2"  # Keep existing hover color
TEXT_COLOR = "#654633"  # Brown for text
SECONDARY_TEXT_COLOR = "#8B7355"  # Lighter brown for secondary text
LIGHT_PURPLE = "#F0E6FF"  # Light purple for accents
DARK_PURPLE = "#4A3F75"  # Dark purple for text
MUTED_LIGHT_PURPLE = "#D1C2F0"  # Muted light purple for buttons

    # -------------------- Database Functions --------------------

def get_rental_info(rental_id):
        """
        Retrieves rental, property, and tenant information based on the provided rentalID.
        Returns a dictionary with all necessary details or None if not found.
        """
        try:
            conn = sqlite3.connect("properties.db")
            cursor = conn.cursor()

            # Parameterized query to prevent SQL injection
            cursor.execute("""
                SELECT 
                    rental.tenantID,
                    rental.combined_properties_id,
                    rental.startDate,
                    rental.endDate,
                    rental.stallPurpose,
                    rental.stallName,
                    rental.startOperatingTime,
                    rental.endOperatingTime,
                    tenants.fullName,
                    tenants.ICNumber,
                    combined_properties.city,
                    combined_properties.sqft,
                    combined_properties.state,
                    combined_properties.price,
                    combined_properties.description,
                    combined_properties.image_path,
                    combined_properties.addressLine1,
                    combined_properties.addressLine2,
                    combined_properties.postcode
                FROM rental
                JOIN tenants ON rental.tenantID = tenants.tenantID
                JOIN combined_properties ON rental.combined_properties_id = combined_properties.id
                WHERE rental.rentalID = ?
            """, (rental_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                # Store the raw data first
                raw_data = {
                    "tenantID": result[0],
                    "combined_properties_id": result[1],
                    "startDate": result[2],
                    "endDate": result[3],
                    "stallPurpose": result[4],
                    "stallName": result[5],
                    "startOperatingTime": result[6],
                    "endOperatingTime": result[7],
                    "fullName": result[8],
                    "ICNumber": result[9],
                    "city": result[10],
                    "sqft": result[11],
                    "state": result[12],
                    "price": result[13],
                    "description": result[14],
                    "image_path": result[15],
                    "addressLine1": result[16],
                    "addressLine2": result[17],
                    "postcode": result[18]
                }

                # Return both raw data and formatted data in the same dictionary
                return {
                    # Raw data
                    "tenantID": raw_data["tenantID"],
                    "combined_properties_id": raw_data["combined_properties_id"],
                    "startDate": raw_data["startDate"],
                    "endDate": raw_data["endDate"],
                    # Formatted data
                    "Tenant Name": raw_data["fullName"],
                    "Tenant IC": raw_data["ICNumber"],
                    "Stall Name": raw_data["stallName"],
                    "Stall Purpose": raw_data["stallPurpose"],
                    "Location": f"{raw_data['addressLine1']}, {raw_data['addressLine2']}, {raw_data['postcode']} {raw_data['city']}, {raw_data['state']}",
                    "Rental Fee": f"RM {raw_data['price']:.2f}/month",
                    "price": raw_data['price'],
                    "Size": f"{raw_data['sqft']} sqft",
                    "Tenancy Period": {
                        "Start Date": raw_data["startDate"],
                        "End Date": raw_data["endDate"],
                    },
                    "Operating Hours": f"{raw_data['startOperatingTime']} - {raw_data['endOperatingTime']}",
                    "image_path": raw_data["image_path"]
                }
            else:
                return None

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return None

    # -------------------- GUI Application --------------------
def start_check_in(rental_id):
    try:
        # Call the main function with the rental_id
        main(rental_id)
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def confirm_check_in(rental_id):
    global content_frame, footer, app
    
    try:
        # Hide current content and footer
        if content_frame:
            content_frame.grid_forget()
        if 'footer' in globals() and footer:
            footer.grid_forget()
            footer.grid_remove()  # This ensures the footer is completely hidden
        
        # Create check-in method selection page with proper sizing
        checkin_page = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)
        checkin_page.grid(row=0, column=0, sticky="nsew", rowspan=3)  # rowspan=3 to cover footer area
        
        # Define return_to_mystall function here
        def return_to_mystall():
            # Destroy the check-in page
            checkin_page.destroy()
            
            # Show the original content and footer
            if content_frame:
                content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
            if 'footer' in globals() and footer:
                footer.grid(row=2, column=0, sticky="nsew")
                footer.grid_configure(column=0, sticky="nsew")  # Ensure footer is properly configured
        
        # Configure grid weights for full screen
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)
        checkin_page.grid_rowconfigure(1, weight=1)  # For content
        checkin_page.grid_columnconfigure(0, weight=1)

        # Create header with gradient effect
        header = ctk.CTkFrame(checkin_page, height=120, fg_color=HEADER_COLOR)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 30))
        header.grid_columnconfigure(1, weight=1)

        # Main content container with shadow effect
        content = ctk.CTkFrame(
            checkin_page,
            fg_color=HEADER_COLOR,
            corner_radius=20,
            border_width=2,
            border_color="#E0D5C9"
        )
        content.grid(row=1, column=0, padx=300, pady=(0, 50), sticky="nsew")  # Increased padding
        
        # Configure content grid weights
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Back Button with enhanced styling
        back_button = ctk.CTkButton(
            header,
            text="← Back",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=return_to_mystall,
            corner_radius=15,
            width=100,
            height=40
        )
        back_button.grid(row=0, column=0, padx=40, pady=40, sticky="w")

        # Header Title with enhanced styling
        title_label = ctk.CTkLabel(
            header,
            text="Choose Your Check-in Method",
            font=ctk.CTkFont(family="Helvetica", size=42, weight="bold"),
            text_color=TEXT_COLOR
        )
        title_label.grid(row=0, column=1, pady=40)

        # Local Check-in Section
        local_frame = ctk.CTkFrame(
            content,
            fg_color=BACKGROUND_COLOR,
            corner_radius=15,
            border_width=2,
            border_color="#E0D5C9"
        )
        local_frame.grid(row=0, column=0, padx=60, pady=60, sticky="nsew")  # Increased padding

        # Icon for local check-in (you can replace with actual icon)
        local_icon = ctk.CTkLabel(
            local_frame,
            text="💻",  # Computer emoji
            font=("Arial", 72),  # Increased from 48
            text_color=TEXT_COLOR
        )
        local_icon.pack(pady=(40, 20))  # Adjusted padding

        local_title = ctk.CTkLabel(
            local_frame,
            text="Local Check-in",
            font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),  # Increased from 28
            text_color=TEXT_COLOR
        )
        local_title.pack(pady=(0, 30))  # Increased padding

        local_desc = ctk.CTkLabel(
            local_frame,
            text="Use your computer's camera\nfor quick and easy check-in",
            font=ctk.CTkFont(family="Helvetica", size=24),  # Increased from 16
            text_color=SECONDARY_TEXT_COLOR
        )
        local_desc.pack(pady=(0, 40))  # Increased padding

        local_button = ctk.CTkButton(
            local_frame,
            text="Start Local Check-in",
            command=lambda: local_check_in(),
            width=300,  # Increased from 250
            height=60,  # Increased from 50
            corner_radius=30,
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),  # Increased from 18
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        local_button.pack(pady=(0, 40))

        # Web Check-in Section
        web_frame = ctk.CTkFrame(
            content,
            fg_color=BACKGROUND_COLOR,
            corner_radius=15,
            border_width=2,
            border_color="#E0D5C9"
        )
        web_frame.grid(row=0, column=1, padx=60, pady=60, sticky="nsew")  # Increased padding

        # Icon for web check-in
        web_icon = ctk.CTkLabel(
            web_frame,
            text="📱",  # Mobile phone emoji
            font=("Arial", 72),  # Increased from 48
            text_color=TEXT_COLOR
        )
        web_icon.pack(pady=(40, 20))  # Adjusted padding

        web_title = ctk.CTkLabel(
            web_frame,
            text="Web Check-in",
            font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),  # Increased from 28
            text_color=TEXT_COLOR
        )
        web_title.pack(pady=(0, 30))  # Increased padding

        web_desc = ctk.CTkLabel(
            web_frame,
            text="Use your phone or tablet\nfor mobile check-in experience",
            font=ctk.CTkFont(family="Helvetica", size=24),  # Increased from 16
            text_color=SECONDARY_TEXT_COLOR
        )
        web_desc.pack(pady=(0, 40))  # Increased padding

        web_button = ctk.CTkButton(
            web_frame,
            text="Start Web Check-in",
            command=lambda: web_check_in(),
            width=300,  # Increased from 250
            height=60,  # Increased from 50
            corner_radius=30,
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),  # Increased from 18
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        web_button.pack(pady=(0, 40))

        def local_check_in():
            subprocess.Popen([sys.executable, 'get_rental_info.py', str(rental_id)])
            return_to_mystall()

        def web_check_in():
            try:
                # Get tenant ID from rental ID
                conn = sqlite3.connect("properties.db")
                cursor = conn.cursor()
                
                # Query to get tenantID from rental table
                cursor.execute("""
                    SELECT tenantID 
                    FROM rental 
                    WHERE rentalID = ?
                """, (rental_id,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    tenant_id = result[0]
                    print(f"Found tenant ID: {tenant_id} for rental ID: {rental_id}")
                    
                    # Launch color_pages_app.py with the correct tenant ID
                    subprocess.Popen([
                        sys.executable, 
                        'color_pages_app.py', 
                        '--tenant_id', 
                        str(tenant_id)
                    ])
                    return_to_mystall()
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Could not find tenant ID for rental ID: {rental_id}"
                    )
                    
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Database Error", 
                    f"Error retrieving tenant information: {str(e)}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"An unexpected error occurred: {str(e)}"
                )

        # Show the new page
        checkin_page.lift()
        
        # Force update geometry
        app.update_idletasks()

    except Exception as e:
        print(f"Error in confirm_check_in: {e}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def get_check_in_attempts(rental_id):
    """Get the number of check-in attempts for today for a specific rental"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.date.today().strftime('%Y-%m-%d')
        
        # Count check-in attempts for today (both local and web check-ins)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dailyCheckInStatus 
            WHERE rentalID = ? 
            AND date LIKE ?
        """, (rental_id, f"{today}%"))
        
        attempts = cursor.fetchone()[0]
        conn.close()
        
        return attempts
        
    except sqlite3.Error as e:
        print(f"Database error checking attempts: {e}")
        return 0  # Return 0 on error to allow check-in
    except Exception as e:
        print(f"Error checking attempts: {e}")
        return 0  # Return 0 on error to allow check-in

def get_latest_check_in_status(rental_id):
    """Get the latest check-in status for today"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        today = datetime.date.today().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT checkInStatus, date
            FROM dailyCheckInStatus 
            WHERE rentalID = ? AND date LIKE ?
            ORDER BY date DESC LIMIT 1
        """, (rental_id, f"{today}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            status_code = result[0]
            status_map = {
                1: ("✅ Successful", True),  # Second value indicates if check-in is complete
                2: ("⚠️ Partial (Face Only)", False),
                3: ("⚠️ Partial (Location Only)", False),
                4: ("❌ Failed", False)
            }
            return status_map.get(status_code, ("Unknown", False))
        return ("No check-in today", False)  # Return default tuple when no result
        
    except sqlite3.Error as e:
        print(f"Database error checking status: {e}")
        return ("Error checking status", False)  # Return error tuple

def open_mystall_window(rental_id=5, pipe_path=None):
    global content_frame, app  # Add global declaration
    
    if rental_id is None:
        messagebox.showerror("Error", "No rental ID provided")
        return
        
    # Fetch rental information from the database
    rental_info = get_rental_info(rental_id)
    
    if not rental_info:
        messagebox.showerror("Error", "Could not find rental information")
        return

    # Define padding constants
    title_padding = {"padx": 40, "pady": (10, 5)}
    subtitle_padding = {"padx": 40, "pady": (0, 40)}
    description_padding = {"padx": 40, "pady": (0, 10)}

    # Create the main window
    app = ctk.CTk()  # This will be accessible globally
    app.geometry("1920x1080")
    app.title("My Stall - Tenant View")
    app.attributes("-fullscreen", True)
    app.configure(fg_color=BACKGROUND_COLOR)

    # Configure grid layout for the main window
    app.grid_rowconfigure(1, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # Header Section
    header_height = 100
    header = ctk.CTkFrame(app, height=header_height, fg_color=HEADER_COLOR)
    header.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid columns - adjust weights for desired spacing
    header.grid_columnconfigure(0, weight=1)  # Back button column
    header.grid_columnconfigure(1, weight=3)  # Center space for title
    header.grid_columnconfigure(2, weight=1)  # Check-in section

    # Back Button - directly in header
    back_button = ctk.CTkButton(
        header,
        text="Back",
        font=ctk.CTkFont(size=18, weight="bold"),
        fg_color=BUTTON_COLOR,
        hover_color=HOVER_COLOR,
        text_color=TEXT_COLOR,
        command=app.destroy,
        corner_radius=15,
        width=100,
        height=40
    )
    back_button.grid(row=0, column=0, padx=40, pady=60, sticky="w")

    # Header Title - centered in header
    title_label = ctk.CTkLabel(
        header,
        text="My Stall",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color=TEXT_COLOR
    )
    title_label.grid(row=0, column=1, pady=60)

    # Create a frame for check-in related items
    checkin_frame = ctk.CTkFrame(header, fg_color=HEADER_COLOR)
    checkin_frame.grid(row=0, column=2, sticky="e", padx=40)

    # Add Check-in Button
    attempts = get_check_in_attempts(rental_id)
    latest_status = get_latest_check_in_status(rental_id)
    
    # Determine button state
    button_disabled = False
    button_text = "Check-in"
    
    if attempts >= 3:
        button_disabled = True
        button_text = "Check-in (Max Attempts Used)"
    elif latest_status and latest_status[1]:  # Check if verification is complete
        button_disabled = True
        button_text = "Check-in Complete"
    
    check_in_button = ctk.CTkButton(
        checkin_frame,
        text=button_text,
        font=ctk.CTkFont(size=18, weight="bold"),
        fg_color=BUTTON_COLOR,
        hover_color=HOVER_COLOR,
        text_color=TEXT_COLOR,
        command=lambda: confirm_check_in(rental_id),
        corner_radius=15,
        width=120,
        height=40,
        state="disabled" if button_disabled else "normal"
    )
    check_in_button.pack(pady=(20, 5))

    # Attempts Display
    attempts_label = ctk.CTkLabel(
        checkin_frame,
        text=f"Today's Check-in Attempts: {attempts}/3",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=TEXT_COLOR
    )
    attempts_label.pack(pady=(0, 5))

    # Latest Check-in Status
    if latest_status:
        status_label = ctk.CTkLabel(
            checkin_frame,
            text=f"Latest Check-in Status: {latest_status[0]}",  # Use first element of tuple
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        status_label.pack(pady=(0, 20))

    # Make header taller to accommodate all elements
    header.configure(height=160)

    # Main Content Section
    content_frame = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)  # This will be accessible globally
    content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=6)
    content_frame.grid_columnconfigure(1, weight=4)

    # Left Panel (Stall Information)
    left_panel = ctk.CTkFrame(
        content_frame,
        fg_color=HEADER_COLOR,
        corner_radius=15,
        border_color=BUTTON_COLOR,
        border_width=2
    )
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=0)

    # Right Panel (Stall Image)
    right_panel = ctk.CTkFrame(
        content_frame,
        fg_color=HEADER_COLOR,
        corner_radius=15,
        border_color=BUTTON_COLOR,
        border_width=2
    )
    right_panel.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=0)

    # Update all text colors and fonts
    title_font = ctk.CTkFont(size=54, weight="bold")
    subtitle_font = ctk.CTkFont(size=30, weight="bold")
    description_font = ctk.CTkFont(size=24)

    # Footer Section
    footer = ctk.CTkFrame(app, height=100, fg_color=HEADER_COLOR)
    footer.grid(row=2, column=0, sticky="nsew")
    footer.grid_columnconfigure(0, weight=1)

    # Define the renew_contract function before creating the button
    def renew_contract():
        # Hide the current content
        content_frame.grid_forget()
        footer.grid_forget()

        # Create and display Page 2 content
        show_page2()

    # Calculate remaining days
    current_date = datetime.date.today()
    try:
        end_date = datetime.datetime.strptime(rental_info["Tenancy Period"]["End Date"], "%Y-%m-%d").date()
        remaining_days = (end_date - current_date).days
        if remaining_days < 0:
            remaining_days = 0
    except ValueError:
        remaining_days = "N/A"  # Handle invalid date format

    stall_info = {
        "tenantID": rental_info["tenantID"],
        "combined_properties_id": rental_info["combined_properties_id"],
        "Tenant Name": rental_info["Tenant Name"],
        "Tenant IC": rental_info["Tenant IC"],
        "Stall Name": rental_info["Stall Name"],
        "Stall Purpose": rental_info["Stall Purpose"],
        "Location": rental_info["Location"],
        "Rental Fee": rental_info["Rental Fee"],
        "price": rental_info["price"],
        "Size": rental_info["Size"],
        "Tenancy Period": {
            "Start Date": rental_info["Tenancy Period"]["Start Date"],
            "End Date": rental_info["Tenancy Period"]["End Date"],
            "Remaining Days": remaining_days
        },
        "Operating Hours": rental_info["Operating Hours"],
        "image_path": rental_info["image_path"]
    }

    if stall_info:
        # Create a container frame to center the content vertically
        container_frame = ctk.CTkFrame(left_panel, fg_color=HEADER_COLOR)
        container_frame.pack(expand=True, anchor="center")

        # Stall Name (Title)
        stall_name_label = ctk.CTkLabel(
            container_frame,
            text=stall_info["Stall Name"],
            font=title_font,
            text_color=TEXT_COLOR
        )
        stall_name_label.pack(anchor="w", **title_padding)

        # Stall Purpose (Subtitle)
        stall_purpose_label = ctk.CTkLabel(
            container_frame,
            text=stall_info["Stall Purpose"],
            font=subtitle_font,
            text_color=TEXT_COLOR
        )
        stall_purpose_label.pack(anchor="w", **subtitle_padding)

        # Tenant Name
        tenant_name_label = ctk.CTkLabel(
            container_frame,
            text=f"Tenant Name: {stall_info['Tenant Name']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        tenant_name_label.pack(anchor="w", **description_padding)

        # Tenant IC Number
        tenant_ic_label = ctk.CTkLabel(
            container_frame,
            text=f"Tenant IC Number: {stall_info['Tenant IC']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        tenant_ic_label.pack(anchor="w", **description_padding)

        # Location
        location_label = ctk.CTkLabel(
            container_frame,
            text=f"Location: {stall_info['Location']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        location_label.pack(anchor="w", **description_padding)

        # Rental Fee
        rental_fee_label = ctk.CTkLabel(
            container_frame,
            text=f"Rental Fee: {stall_info['Rental Fee']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        rental_fee_label.pack(anchor="w", **description_padding)

        # Size
        size_label = ctk.CTkLabel(
            container_frame,
            text=f"Size: {stall_info['Size']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        size_label.pack(anchor="w", **description_padding)

        # Tenancy Period with Remaining Days
        tenancy_period = stall_info["Tenancy Period"]
        remaining_days = tenancy_period["Remaining Days"]
        if isinstance(remaining_days, int):
            remaining_text = f" (Remaining {remaining_days} day(s))"
        else:
            remaining_text = " (Remaining N/A day(s))"

        tenancy_label = ctk.CTkLabel(
            container_frame,
            text=f"Tenancy Period: {tenancy_period['Start Date']} to {tenancy_period['End Date']}{remaining_text}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        tenancy_label.pack(anchor="w", **description_padding)

        # Operating Hours
        operating_hours_label = ctk.CTkLabel(
            container_frame,
            text=f"Operating Hours: {stall_info['Operating Hours']}",
            font=description_font,
            text_color=TEXT_COLOR
        )
        operating_hours_label.pack(anchor="w", **description_padding)
    else:
        # If no stall_info found, display a placeholder message
        placeholder_label = ctk.CTkLabel(
            left_panel,
            text="No rental information found for the entered Rental ID.",
            font=description_font,
            text_color=TEXT_COLOR
        )
        placeholder_label.pack(padx=40, pady=20, anchor="center")

    if stall_info and stall_info["image_path"]:
        image_path = stall_info["image_path"]
    else:
        image_path = "ppl1img3.jpg"  # Default image if not specified

    try:
        stall_image = Image.open(image_path)
        # Handle Resampling based on Pillow version
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.ANTIALIAS  # For older Pillow versions

        # Adjust image size to occupy more space
        stall_image = stall_image.resize((800, 800), resample=resample_method)
        stall_photo = ImageTk.PhotoImage(stall_image)
        image_label = ctk.CTkLabel(right_panel, image=stall_photo, text="")
        image_label.image = stall_photo  # Keep a reference
        image_label.pack(expand=True, padx=20, pady=20)
    except FileNotFoundError:
        image_label = ctk.CTkLabel(
            right_panel,
            text="Image not found",
            font=description_font,
            text_color=TEXT_COLOR
        )
        image_label.pack(expand=True, padx=20, pady=20)

    # -------------------- Footer Section --------------------
    footer_height = 100

    footer = ctk.CTkFrame(app, height=footer_height, fg_color=HEADER_COLOR)
    footer.grid(row=2, column=0, sticky="nsew")
    footer.grid_columnconfigure(0, weight=1)

    # Renew Contract Button (Centered in footer)
    renew_button = ctk.CTkButton(
        footer,
        text="Renew Contract",
        font=ctk.CTkFont(size=24, weight="bold"),
        fg_color=BUTTON_COLOR,
        hover_color=HOVER_COLOR,
        text_color=TEXT_COLOR,
        command=renew_contract,
        corner_radius=15,
        width=250,
        height=60
    )
    renew_button.place(relx=0.5, rely=0.5, anchor="center")

    # Function to show Page 2
    def show_page2():
        global start_date_entry, end_date_entry
        page2 = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)
        page2.grid(row=0, column=0, sticky="nsew")
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)

        # Get the current rental's end date from the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT endDate FROM rental WHERE rentalID = ?", (rental_id,))
        current_end_date_str = cursor.fetchone()[0]
        conn.close()

        # Convert the string date to datetime.date object
        current_end_date = datetime.datetime.strptime(current_end_date_str, "%Y-%m-%d").date()

        # Create header
        header = ctk.CTkFrame(page2, height=100, fg_color=HEADER_COLOR)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(
            header,
            text="Rental Application Form",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=TEXT_COLOR
        )
        title_label.grid(row=0, column=0, pady=30)

        # Back Button
        back_button = ctk.CTkButton(
            header,
            text="Back",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=lambda: return_to_mystall(),
            corner_radius=15,
            width=100,
            height=40
        )
        back_button.grid(row=0, column=0, padx=40, pady=30, sticky="w")
        
        # Center the title by adjusting column configuration
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=2)
        title_label.grid(row=0, column=1)

        # Form Frame
        form_frame = ctk.CTkFrame(page2, fg_color=HEADER_COLOR, corner_radius=10)
        form_frame.grid(row=1, column=0, padx=200, pady=30, sticky="nsew")
        page2.grid_rowconfigure(1, weight=1)
        page2.grid_columnconfigure(0, weight=1)

        # Tenant Information
        tenant_name_label = ctk.CTkLabel(form_frame, text="Tenant Name:", font=("Arial", 28), text_color=TEXT_COLOR)
        tenant_name_label.grid(row=0, column=0, padx=20, pady=20, sticky='e')
        tenant_name_value = ctk.CTkLabel(form_frame, text=stall_info["Tenant Name"], font=("Arial", 28), text_color=TEXT_COLOR)
        tenant_name_value.grid(row=0, column=1, padx=20, pady=20, sticky='w')

        ic_number_label = ctk.CTkLabel(form_frame, text="IC Number:", font=("Arial", 28), text_color=TEXT_COLOR)
        ic_number_label.grid(row=1, column=0, padx=20, pady=20, sticky='e')
        ic_number_value = ctk.CTkLabel(form_frame, text=stall_info["Tenant IC"], font=("Arial", 28), text_color=TEXT_COLOR)
        ic_number_value.grid(row=1, column=1, padx=20, pady=20, sticky='w')

        # Stall Information
        stall_name_label = ctk.CTkLabel(form_frame, text="Stall Name:", font=("Arial", 28), text_color=TEXT_COLOR)
        stall_name_label.grid(row=2, column=0, padx=20, pady=20, sticky='e')
        stall_name_value = ctk.CTkLabel(form_frame, text=stall_info["Stall Name"], font=("Arial", 28), text_color=TEXT_COLOR)
        stall_name_value.grid(row=2, column=1, padx=20, pady=20, sticky='w')

        stall_purpose_label = ctk.CTkLabel(form_frame, text="Stall Purpose:", font=("Arial", 28),
                                           text_color=TEXT_COLOR)
        stall_purpose_label.grid(row=3, column=0, padx=20, pady=20, sticky='e')
        stall_purpose_value = ctk.CTkLabel(form_frame, text=stall_info["Stall Purpose"], font=("Arial", 28), text_color=TEXT_COLOR)
        stall_purpose_value.grid(row=3, column=1, padx=20, pady=20, sticky='w')

        stall_location_label = ctk.CTkLabel(form_frame, text="Stall Location:", font=("Arial", 28),
                                            text_color=TEXT_COLOR)
        stall_location_label.grid(row=4, column=0, padx=20, pady=20, sticky='e')
        stall_location_value = ctk.CTkLabel(form_frame, text=stall_info["Location"], font=("Arial", 28),
                                            wraplength=1200, justify='left', text_color=TEXT_COLOR)
        stall_location_value.grid(row=4, column=1, padx=20, pady=20, sticky='w')

        rental_fee_label = ctk.CTkLabel(form_frame, text="Rental Fee:", font=("Arial", 28), text_color=TEXT_COLOR)
        rental_fee_label.grid(row=5, column=0, padx=20, pady=20, sticky='e')
        rental_fee_value = ctk.CTkLabel(form_frame, text=stall_info["Rental Fee"], font=("Arial", 28), text_color=TEXT_COLOR)
        rental_fee_value.grid(row=5, column=1, padx=20, pady=20, sticky='w')

        stall_size_label = ctk.CTkLabel(form_frame, text="Stall Size:", font=("Arial", 28), text_color=TEXT_COLOR)
        stall_size_label.grid(row=6, column=0, padx=20, pady=20, sticky='e')
        stall_size_value = ctk.CTkLabel(form_frame, text=stall_info["Size"], font=("Arial", 28), text_color=TEXT_COLOR)
        stall_size_value.grid(row=6, column=1, padx=20, pady=20, sticky='w')

        # Rental Period
        rental_period_label = ctk.CTkLabel(form_frame, text="Rental Period:", font=("Arial", 28),
                                           text_color=TEXT_COLOR)
        rental_period_label.grid(row=7, column=0, padx=20, pady=20, sticky='e')

        dates_frame = ctk.CTkFrame(form_frame, fg_color="#FFFFFF")
        dates_frame.grid(row=7, column=1, padx=20, pady=20, sticky='w')

        def on_start_date_change(event):
            selected_start_date = start_date_entry.get_date()
            end_date_entry.config(mindate=selected_start_date)
            current_end_date = end_date_entry.get_date()
            if current_end_date < selected_start_date:
                end_date_entry.set_date(selected_start_date)

        def on_end_date_change(event):
            selected_end_date = end_date_entry.get_date()
            start_date_entry.config(maxdate=selected_end_date)
            current_start_date = start_date_entry.get_date()
            if current_start_date > selected_end_date:
                start_date_entry.set_date(selected_end_date)

        # Update the DateEntry initialization with the current rental's end date as mindate
        start_date_entry = DateEntry(dates_frame, width=16, background='#9370DB',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                     mindate=current_end_date, font=("Arial", 22), state="readonly")
        start_date_entry.grid(row=0, column=0, padx=(0, 10))
        start_date_entry.bind("<<DateEntrySelected>>", on_start_date_change)
        start_date_entry.set_date(current_end_date)  # Set initial date to current rental's end date

        to_label = ctk.CTkLabel(dates_frame, text=" to ", font=("Arial", 24), text_color="black")
        to_label.grid(row=0, column=1)

        end_date_entry = DateEntry(dates_frame, width=16, background='#9370DB',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                   mindate=current_end_date, font=("Arial", 22), state="readonly")
        end_date_entry.grid(row=0, column=2, padx=(10, 0))
        end_date_entry.bind("<<DateEntrySelected>>", on_end_date_change)
        end_date_entry.set_date(current_end_date)  # Set initial date to current rental's end date

        # Operating Hours (Non-editable)
        operating_hours_label = ctk.CTkLabel(form_frame, text="Operating Hours:", font=("Arial", 28),
                                             text_color=TEXT_COLOR)
        operating_hours_label.grid(row=8, column=0, padx=20, pady=20, sticky='e')
        operating_hours_value = ctk.CTkLabel(form_frame, text=stall_info["Operating Hours"], font=("Arial", 28), text_color=TEXT_COLOR)
        operating_hours_value.grid(row=8, column=1, padx=20, pady=20, sticky='w')

        # Next Button
        next_button = ctk.CTkButton(
            page2, 
            text="Next", 
            command=show_page3,
            width=300, 
            height=70, 
            font=("Arial", 32),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            corner_radius=20
        )
        next_button.grid(row=2, column=0, pady=40)

        # Hide the current content
        content_frame.grid_forget()
        footer.grid_forget()

        # Show the new page
        page2.grid(row=0, column=0, sticky="nsew")

    def show_page3():
        global start_date_entry, end_date_entry
        page3 = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)
        page3.grid(row=0, column=0, sticky="nsew")
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)

        # Create header
        header = ctk.CTkFrame(page3, height=100, fg_color=HEADER_COLOR)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(
            header,
            text="Rental Application Agreement",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=TEXT_COLOR
        )
        title_label.grid(row=0, column=0, pady=30)

        # Back Button
        back_button = ctk.CTkButton(
            header,
            text="Back",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=lambda: return_to_mystall(),
            corner_radius=15,
            width=100,
            height=40
        )
        back_button.grid(row=0, column=0, padx=40, pady=30, sticky="w")
        
        # Center the title by adjusting column configuration
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=2)
        title_label.grid(row=0, column=1)

        # Agreement Frame
        agreement_frame = ctk.CTkFrame(page3, fg_color=HEADER_COLOR, corner_radius=10)
        agreement_frame.grid(row=1, column=0, padx=50, pady=(20, 10), sticky="nsew")
        page3.grid_rowconfigure(1, weight=1)
        page3.grid_columnconfigure(0, weight=1)

        # Configure grid for agreement_frame
        agreement_frame.grid_rowconfigure(0, weight=1)
        agreement_frame.grid_columnconfigure(0, weight=1)

        # Retrieve the agreement text from the database
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("SELECT rental_agreement FROM systemInformation ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                agreement_text = result[0]
            else:
                agreement_text = "No agreement text found in the database."
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving agreement text: {e}")
            agreement_text = "Error loading agreement text."
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Replace placeholders with actual data
        agreement_text = agreement_text.replace("##tenantName##", stall_info["Tenant Name"])
        agreement_text = agreement_text.replace("##tenantICNumber##", stall_info["Tenant IC"])
        agreement_text = agreement_text.replace("##stallLocation##", stall_info["Location"])
        agreement_text = agreement_text.replace("##stallSize##", stall_info["Size"])
        agreement_text = agreement_text.replace("##stallRentalFee##", stall_info["Rental Fee"])
        agreement_text = agreement_text.replace("##startDate##", start_date_entry.get())
        agreement_text = agreement_text.replace("##endDate##", end_date_entry.get())

        # Agreement Textbox
        agreement_textbox = ctk.CTkTextbox(
            agreement_frame, 
            wrap="word",
            fg_color=HEADER_COLOR,
            text_color=TEXT_COLOR,
            border_color=BUTTON_COLOR,
            corner_radius=5, 
            font=("Arial", 16),
            width=1000,
            height=500
        )
        agreement_textbox.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Insert the agreement text
        agreement_textbox.insert("1.0", agreement_text)
        agreement_textbox.configure(state="disabled")  # Make it read-only

        # Checkbox for agreement
        agree_var = tk.BooleanVar()
        agree_checkbox = ctk.CTkCheckBox(
            page3, 
            text="I agree to the terms and conditions",
            variable=agree_var, 
            onvalue=True, 
            offvalue=False,
            command=lambda: submit_button.configure(state="normal" if agree_var.get() else "disabled"),
            font=("Arial", 16),
            text_color=TEXT_COLOR,
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR
        )
        agree_checkbox.grid(row=2, column=0, pady=(10, 20))

        # Submit Button
        submit_button = ctk.CTkButton(
            page3, 
            text="Submit Renewal",
            command=submit_renewal,
            width=300, 
            height=70, 
            font=("Arial", 32),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            corner_radius=20
        )
        submit_button.grid(row=3, column=0, pady=(0, 40))
        submit_button.configure(state="disabled")

        # Show the new page
        page3.grid(row=0, column=0, sticky="nsew")

    def submit_renewal():
        try:
            # Connect to database
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()

            # Insert new rental record with isApprove = -1 (pending renewal)
            cursor.execute("""
                INSERT INTO rental (
                    combined_properties_id,
                    tenantID,
                    startDate,
                    endDate,
                    rentalAmount,
                    stallPurpose,
                    stallName,
                    startOperatingTime,
                    endOperatingTime,
                    isApprove
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, -1)
            """, (
                stall_info["combined_properties_id"],
                stall_info["tenantID"],
                start_date_entry.get(),
                end_date_entry.get(),
                stall_info["price"],  # Use raw price value
                stall_info["Stall Purpose"],
                stall_info["Stall Name"],
                stall_info["Operating Hours"].split(" - ")[0],
                stall_info["Operating Hours"].split(" - ")[1],
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", 
                              "Renewal application submitted successfully! Please wait for admin approval.")
            app.destroy()  # Close the application after submission

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while submitting renewal: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()

    def on_window_ready(event):
        app.unbind('<Map>')
        # Signal that the window is ready by deleting the pipe file
        if pipe_path and os.path.exists(pipe_path):
            try:
                os.remove(pipe_path)
            except Exception as e:
                print(f"Error removing pipe file: {e}")

    # Bind the Map event to detect when window is ready
    app.bind('<Map>', on_window_ready)

    def return_to_mystall():
        # Destroy the current page
        for widget in app.winfo_children():
            widget.destroy()
        
        # Define renew_contract function
        def renew_contract():
            # Hide the current content
            content_frame.grid_forget()
            footer.grid_forget()
            # Create and display Page 2 content
            show_page2()
        
        # Recreate the original content
        content_frame = ctk.CTkFrame(app, fg_color=BACKGROUND_COLOR)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=6)  # Left Panel
        content_frame.grid_columnconfigure(1, weight=4)  # Right Panel

        # Recreate header
        header = ctk.CTkFrame(app, height=header_height, fg_color=HEADER_COLOR)
        header.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid columns
        header.grid_columnconfigure(0, weight=1)  # Back button column
        header.grid_columnconfigure(1, weight=3)  # Center space for title
        header.grid_columnconfigure(2, weight=1)  # Check-in section

        # Back Button - directly in header
        back_button = ctk.CTkButton(
            header,
            text="Back",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=app.destroy,
            corner_radius=15,
            width=100,
            height=40
        )
        back_button.grid(row=0, column=0, padx=40, pady=60, sticky="w")

        # Header Title - centered in header
        title_label = ctk.CTkLabel(
            header,
            text="My Stall",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=TEXT_COLOR
        )
        title_label.grid(row=0, column=1, pady=60)

        # Create a frame for check-in related items
        checkin_frame = ctk.CTkFrame(header, fg_color=HEADER_COLOR)
        checkin_frame.grid(row=0, column=2, sticky="e", padx=40)

        # Add Check-in Button
        attempts = get_check_in_attempts(rental_id)
        latest_status = get_latest_check_in_status(rental_id)
        
        # Determine button state
        button_disabled = False
        button_text = "Check-in"
        
        if attempts >= 3:
            button_disabled = True
            button_text = "Check-in (Max Attempts Used)"
        elif latest_status and latest_status[1]:  # Check if verification is complete
            button_disabled = True
            button_text = "Check-in Complete"
        
        check_in_button = ctk.CTkButton(
            checkin_frame,
            text=button_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=lambda: confirm_check_in(rental_id),
            corner_radius=15,
            width=120,
            height=40,
            state="disabled" if button_disabled else "normal"
        )
        check_in_button.pack(pady=(20, 5))

        # Attempts Display
        attempts_label = ctk.CTkLabel(
            checkin_frame,
            text=f"Today's Check-in Attempts: {attempts}/3",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        attempts_label.pack(pady=(0, 5))

        # Latest Check-in Status
        if latest_status:
            status_label = ctk.CTkLabel(
                checkin_frame,
                text=f"Latest Check-in Status: {latest_status[0]}",  # Use first element of tuple
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_COLOR
            )
            status_label.pack(pady=(0, 20))

        # Make header taller to accommodate all elements
        header.configure(height=160)

        # Recreate the main content
        left_panel = ctk.CTkFrame(
            content_frame,
            fg_color=HEADER_COLOR,
            corner_radius=15,
            border_color=BUTTON_COLOR,
            border_width=2
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=0)

        right_panel = ctk.CTkFrame(
            content_frame,
            fg_color=HEADER_COLOR,
            corner_radius=15,
            border_color=BUTTON_COLOR,
            border_width=2
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=0)

        # Recreate footer
        footer = ctk.CTkFrame(app, height=100, fg_color=HEADER_COLOR)
        footer.grid(row=2, column=0, sticky="nsew")
        footer.grid_columnconfigure(0, weight=1)

        # Renew Contract Button
        renew_button = ctk.CTkButton(
            footer,
            text="Renew Contract",
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=BUTTON_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=renew_contract,
            corner_radius=15,
            width=250,
            height=60
        )
        renew_button.place(relx=0.5, rely=0.5, anchor="center")

        # Repopulate the content
        if stall_info:
            # Create a container frame to center the content vertically
            container_frame = ctk.CTkFrame(left_panel, fg_color=HEADER_COLOR)
            container_frame.pack(expand=True, anchor="center")

            # Stall Name (Title)
            stall_name_label = ctk.CTkLabel(
                container_frame,
                text=stall_info["Stall Name"],
                font=title_font,
                text_color=TEXT_COLOR
            )
            stall_name_label.pack(anchor="w", **title_padding)

            # Stall Purpose (Subtitle)
            stall_purpose_label = ctk.CTkLabel(
                container_frame,
                text=stall_info["Stall Purpose"],
                font=subtitle_font,
                text_color=TEXT_COLOR
            )
            stall_purpose_label.pack(anchor="w", **subtitle_padding)

            # Tenant Name
            tenant_name_label = ctk.CTkLabel(
                container_frame,
                text=f"Tenant Name: {stall_info['Tenant Name']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            tenant_name_label.pack(anchor="w", **description_padding)

            # Tenant IC Number
            tenant_ic_label = ctk.CTkLabel(
                container_frame,
                text=f"Tenant IC Number: {stall_info['Tenant IC']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            tenant_ic_label.pack(anchor="w", **description_padding)

            # Location
            location_label = ctk.CTkLabel(
                container_frame,
                text=f"Location: {stall_info['Location']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            location_label.pack(anchor="w", **description_padding)

            # Rental Fee
            rental_fee_label = ctk.CTkLabel(
                container_frame,
                text=f"Rental Fee: {stall_info['Rental Fee']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            rental_fee_label.pack(anchor="w", **description_padding)

            # Size
            size_label = ctk.CTkLabel(
                container_frame,
                text=f"Size: {stall_info['Size']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            size_label.pack(anchor="w", **description_padding)

            # Tenancy Period with Remaining Days
            tenancy_period = stall_info["Tenancy Period"]
            remaining_days = (datetime.datetime.strptime(tenancy_period["End Date"], "%Y-%m-%d").date() - datetime.date.today()).days
            if isinstance(remaining_days, int):
                remaining_text = f" (Remaining {remaining_days} day(s))"
            else:
                remaining_text = " (Remaining N/A day(s))"

            tenancy_label = ctk.CTkLabel(
                container_frame,
                text=f"Tenancy Period: {tenancy_period['Start Date']} to {tenancy_period['End Date']}{remaining_text}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            tenancy_label.pack(anchor="w", **description_padding)

            # Operating Hours
            operating_hours_label = ctk.CTkLabel(
                container_frame,
                text=f"Operating Hours: {stall_info['Operating Hours']}",
                font=description_font,
                text_color=TEXT_COLOR
            )
            operating_hours_label.pack(anchor="w", **description_padding)

        # Recreate the image display
        if stall_info and stall_info["image_path"]:
            image_path = stall_info["image_path"]
            try:
                stall_image = Image.open(image_path)
                try:
                    resample_method = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_method = Image.ANTIALIAS

                stall_image = stall_image.resize((800, 800), resample=resample_method)
                stall_photo = ImageTk.PhotoImage(stall_image)
                image_label = ctk.CTkLabel(right_panel, image=stall_photo, text="")
                image_label.image = stall_photo
                image_label.pack(expand=True, padx=20, pady=20)
            except FileNotFoundError:
                image_label = ctk.CTkLabel(
                    right_panel,
                    text="Image not found",
                    font=description_font,
                    text_color=TEXT_COLOR
                )
                image_label.pack(expand=True, padx=20, pady=20)

    # Run the application
    app.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        rental_id = int(sys.argv[1])
        pipe_path = sys.argv[2]
        open_mystall_window(rental_id, pipe_path)
    elif len(sys.argv) > 1:
        rental_id = int(sys.argv[1])
        open_mystall_window(rental_id)
    else:
        print("No rental ID provided")
