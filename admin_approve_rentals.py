import customtkinter as ctk
import sqlite3
from tkinter import messagebox

# Initialize CustomTkinter appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Define color constants
LIGHT_PURPLE = "#F0E6FF"
DARK_PURPLE = "#4A3F75"
MUTED_LIGHT_PURPLE = "#D1C2F0"
TEXT_COLOR = "#333333"
HEADER_BG = "#D8BFD8"

def show_admin_approval(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for admin approval
    admin_frame = ctk.CTkFrame(root, fg_color=LIGHT_PURPLE)
    admin_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide admin frame and call the dashboard callback
        admin_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=admin_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)
    
    # Create the AdminApprovalApp instance with the admin_frame
    app = AdminApprovalApp(admin_frame)

class AdminApprovalApp:
    def __init__(self, master):
        self.master = master
        self.create_widgets()
        self.load_pending_rentals()

    def create_widgets(self):
        # Main frame with light purple background
        self.main_frame = ctk.CTkFrame(self.master, fg_color=LIGHT_PURPLE)
        self.main_frame.pack(fill="both", expand=True)

        # Title and Filter Section Frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=LIGHT_PURPLE)
        header_frame.pack(fill="x", pady=(40, 20))

        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Pending Rental Approvals",
            font=("Arial", 40, "bold"),
            text_color=DARK_PURPLE
        )
        self.title_label.pack(side="left", padx=40)

        # Filter Section
        filter_frame = ctk.CTkFrame(header_frame, fg_color=LIGHT_PURPLE)
        filter_frame.pack(side="right", padx=40)

        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filter Applications:",
            font=("Arial", 16, "bold"),
            text_color=DARK_PURPLE
        )
        filter_label.pack(side="left", padx=(0, 10))

        # Dropdown for filtering
        self.filter_var = ctk.StringVar(value="All Applications")
        filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Applications", "New Applications", "Renewal Applications"],
            variable=self.filter_var,
            command=self.filter_applications,
            width=200,
            font=("Arial", 14),
            fg_color="#9370DB",
            button_color="#8A2BE2",
            button_hover_color="#483D8B",
            dropdown_font=("Arial", 14)
        )
        filter_dropdown.pack(side="left")

        # Scrollable frame for rental boxes
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=LIGHT_PURPLE,
            width=1800,
            height=800
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=40, pady=20)

    def filter_applications(self, selection):
        # Clear current display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()

            # Modify query based on selection
            if selection == "All Applications":
                cursor.execute("""
                    SELECT rentalID 
                    FROM rental 
                    WHERE isApprove = 0 OR isApprove = -1 
                    ORDER BY isApprove DESC, rentalID
                """)
            elif selection == "New Applications":
                cursor.execute("""
                    SELECT rentalID 
                    FROM rental 
                    WHERE isApprove = 0 
                    ORDER BY rentalID
                """)
            else:  # Renewal Applications
                cursor.execute("""
                    SELECT rentalID 
                    FROM rental 
                    WHERE isApprove = -1 
                    ORDER BY rentalID
                """)

            pending_rental_ids = cursor.fetchall()
            conn.close()

            if not pending_rental_ids:
                # Show "No applications found" message
                no_apps_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="No applications found",
                    font=("Arial", 16),
                    text_color=TEXT_COLOR
                )
                no_apps_label.pack(pady=20)
            else:
                # Display the filtered applications
                for idx, (rental_id,) in enumerate(pending_rental_ids):
                    rental_info = get_rental_info(rental_id)
                    if rental_info:
                        self.create_rental_box(idx, rental_info)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def load_pending_rentals(self):
        # Initial load with "All Applications"
        self.filter_applications("All Applications")

    def create_rental_box(self, idx, rental_info):
        # Create a frame for each rental box
        box_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=MUTED_LIGHT_PURPLE, corner_radius=10)
        box_frame.grid(row=idx, column=0, padx=20, pady=10, sticky="ew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Configure grid layout for box_frame
        box_frame.grid_columnconfigure(0, weight=1)
        box_frame.grid_columnconfigure(1, weight=1)

        # Application Type Label (New/Renewal)
        application_type = "RENEWAL APPLICATION" if rental_info["isApprove"] == -1 else "NEW APPLICATION"
        type_label = ctk.CTkLabel(
            box_frame, 
            text=application_type,
            font=("Arial", 16, "bold"),
            text_color="#FF6B6B" if rental_info["isApprove"] == -1 else "#4CAF50"
        )
        type_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")

        # Stall Name (moved to row 1)
        ctk.CTkLabel(
            box_frame, 
            text=rental_info["stallName"], 
            font=("Arial", 20, "bold"), 
            text_color=DARK_PURPLE
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Tenant Name and IC (shifted down one row)
        ctk.CTkLabel(
            box_frame, 
            text=f"Tenant: {rental_info['fullName']}", 
            font=("Arial", 18), 
            text_color=TEXT_COLOR
        ).grid(row=2, column=0, padx=10, pady=2, sticky="w")
        
        ctk.CTkLabel(
            box_frame, 
            text=f"IC: {rental_info['ICNumber']}", 
            font=("Arial", 18), 
            text_color=TEXT_COLOR
        ).grid(row=2, column=1, padx=10, pady=2, sticky="w")

        # Size and Price
        ctk.CTkLabel(box_frame, text=f"Size: {rental_info['sqft']} sqft", font=("Arial", 18), text_color=TEXT_COLOR).grid(row=3, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(box_frame, text=f"Price: RM {rental_info['price']:.2f}/month", font=("Arial", 18), text_color=TEXT_COLOR).grid(row=3, column=1, padx=10, pady=2, sticky="w")

        # Rental Period
        ctk.CTkLabel(box_frame, text=f"Period: {rental_info['startDate']} to {rental_info['endDate']}", font=("Arial", 18), text_color=TEXT_COLOR).grid(row=4, column=0, columnspan=2, padx=10, pady=2, sticky="w")

        # Location
        location = f"{rental_info['addressLine1']}, {rental_info['addressLine2']}, {rental_info['postcode']} {rental_info['city']}, {rental_info['state']}"
        ctk.CTkLabel(box_frame, text=f"Location: {location}", font=("Arial", 18), text_color=TEXT_COLOR, wraplength=800).grid(row=5, column=0, columnspan=2, padx=10, pady=2, sticky="w")

        # Action Buttons
        action_frame = ctk.CTkFrame(box_frame, fg_color=MUTED_LIGHT_PURPLE)
        action_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="e")

        # Add View Current Rental button only for renewal applications
        if rental_info["isApprove"] == -1:
            ctk.CTkButton(
                action_frame, 
                text="View Current Rental", 
                command=lambda r_id=rental_info["rentalID"]: self.view_current_rental(r_id),
                fg_color="#6A5ACD", 
                hover_color="#483D8B", 
                font=("Arial", 16), 
                width=150, 
                height=40
            ).grid(row=0, column=0, padx=(0, 10))

            ctk.CTkButton(
                action_frame, 
                text="Approve", 
                command=lambda r_id=rental_info["rentalID"]: self.approve_rental(r_id),
                fg_color="green", 
                hover_color="dark green", 
                font=("Arial", 16), 
                width=100, 
                height=40
            ).grid(row=0, column=1, padx=(0, 10))

            ctk.CTkButton(
                action_frame, 
                text="Reject", 
                command=lambda r_id=rental_info["rentalID"]: self.reject_rental(r_id),
                fg_color="red", 
                hover_color="dark red", 
                font=("Arial", 16), 
                width=100, 
                height=40
            ).grid(row=0, column=2, padx=(0, 10))
        else:
            # Original buttons for new applications
            ctk.CTkButton(
                action_frame, 
                text="Approve", 
                command=lambda r_id=rental_info["rentalID"]: self.approve_rental(r_id),
                fg_color="green", 
                hover_color="dark green", 
                font=("Arial", 16), 
                width=100, 
                height=40
            ).grid(row=0, column=0, padx=(0, 10))

            ctk.CTkButton(
                action_frame, 
                text="Reject", 
                command=lambda r_id=rental_info["rentalID"]: self.reject_rental(r_id),
                fg_color="red", 
                hover_color="dark red", 
                font=("Arial", 16), 
                width=100, 
                height=40
            ).grid(row=0, column=1, padx=(0, 10))

    def approve_rental(self, rental_id):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE rental SET isApprove = 1 WHERE rentalID = ?", (rental_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Rental ID {rental_id} has been approved.")
            self.refresh_rentals()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def reject_rental(self, rental_id):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rental WHERE rentalID = ?", (rental_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Rental ID {rental_id} has been rejected and removed.")
            self.refresh_rentals()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def refresh_rentals(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_pending_rentals()

    def view_current_rental(self, renewal_rental_id):
        try:
            # Get the current active rental for the same tenant and stall
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # First get the tenant ID and stall ID from the renewal application
            cursor.execute("""
                SELECT tenantID, combined_properties_id 
                FROM rental 
                WHERE rentalID = ?
            """, (renewal_rental_id,))
            tenant_id, stall_id = cursor.fetchone()
            
            # Then get the current active rental details
            cursor.execute("""
                SELECT 
                    r.rentalID, t.fullName, r.stallName, r.startDate, r.endDate,
                    t.ICNumber, cp.addressLine1, cp.addressLine2, cp.postcode,
                    cp.city, cp.state, cp.sqft, cp.price, r.stallPurpose,
                    r.startOperatingTime, r.endOperatingTime
                FROM rental r
                JOIN tenants t ON r.tenantID = t.tenantID
                JOIN combined_properties cp ON r.combined_properties_id = cp.id
                WHERE r.tenantID = ? 
                AND r.combined_properties_id = ?
                AND r.isApprove = 1
            """, (tenant_id, stall_id))
            
            current_rental = cursor.fetchone()
            conn.close()

            if current_rental:
                # Create a new window to display current rental details
                details_window = ctk.CTkToplevel(self.master)
                details_window.title("Current Rental Details")
                details_window.geometry("800x600")
                
                # Create a frame for the content
                content_frame = ctk.CTkFrame(details_window, fg_color="white")
                content_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Title
                title_label = ctk.CTkLabel(
                    content_frame,
                    text="Current Active Rental Details",
                    font=("Arial", 24, "bold"),
                    text_color=DARK_PURPLE
                )
                title_label.pack(pady=(0, 20))
                
                # Details
                details = [
                    ("Rental ID", current_rental[0]),
                    ("Tenant Name", current_rental[1]),
                    ("Stall Name", current_rental[2]),
                    ("Rental Period", f"{current_rental[3]} to {current_rental[4]}"),
                    ("IC Number", current_rental[5]),
                    ("Location", f"{current_rental[6]}, {current_rental[7]}, {current_rental[8]} {current_rental[9]}, {current_rental[10]}"),
                    ("Size", f"{current_rental[11]} sqft"),
                    ("Rental Fee", f"RM {current_rental[12]:.2f}/month"),
                    ("Stall Purpose", current_rental[13]),
                    ("Operating Hours", f"{current_rental[14]} - {current_rental[15]}")
                ]
                
                for label, value in details:
                    detail_frame = ctk.CTkFrame(content_frame, fg_color="white")
                    detail_frame.pack(fill="x", padx=20, pady=5)
                    
                    ctk.CTkLabel(
                        detail_frame,
                        text=f"{label}:",
                        font=("Arial", 16, "bold"),
                        text_color=DARK_PURPLE
                    ).pack(side="left", padx=(0, 10))
                    
                    ctk.CTkLabel(
                        detail_frame,
                        text=str(value),
                        font=("Arial", 16),
                        text_color=TEXT_COLOR
                    ).pack(side="left")

                # Close button
                ctk.CTkButton(
                    content_frame,
                    text="Close",
                    command=details_window.destroy,
                    font=("Arial", 16),
                    fg_color="#6A5ACD",
                    hover_color="#483D8B",
                    width=100
                ).pack(pady=20)

            else:
                messagebox.showinfo("Info", "No current active rental found for this tenant and stall.")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

def get_rental_info(rental_id):
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()

        # Updated query to include isApprove status
        cursor.execute("""
            SELECT 
                r.rentalID, t.fullName, r.stallName, r.startDate, r.endDate,
                t.ICNumber, cp.addressLine1, cp.addressLine2, cp.postcode, 
                cp.city, cp.state, cp.sqft, cp.price, r.stallPurpose,
                r.startOperatingTime, r.endOperatingTime, cp.image_path,
                r.isApprove
            FROM rental r
            JOIN tenants t ON r.tenantID = t.tenantID
            JOIN combined_properties cp ON r.combined_properties_id = cp.id
            WHERE r.rentalID = ? AND (r.isApprove = 0 OR r.isApprove = -1)
        """, (rental_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "rentalID": result[0],
                "fullName": result[1],
                "stallName": result[2],
                "startDate": result[3],
                "endDate": result[4],
                "ICNumber": result[5],
                "addressLine1": result[6],
                "addressLine2": result[7],
                "postcode": result[8],
                "city": result[9],
                "state": result[10],
                "sqft": result[11],
                "price": result[12],
                "stallPurpose": result[13],
                "startOperatingTime": result[14],
                "endOperatingTime": result[15],
                "image_path": result[16],
                "isApprove": result[17]  # Added isApprove status
            }
        else:
            return None

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return None

def main():
    root = ctk.CTk()
    root.title("Admin Rental Approval")
    root.geometry("1920x1080")
    root.resizable(True, True)
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Admin Approval",
        command=lambda: show_admin_approval(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
