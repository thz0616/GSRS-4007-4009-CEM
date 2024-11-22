from customtkinter import *
import tkinter as tk
from tkinter import Toplevel, Label, Button, Canvas, messagebox, filedialog
from PIL import Image, ImageTk
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_receipt_pdf(property_id, payment_id):
    # Connect to the database
    conn = sqlite3.connect("properties.db")
    cursor = conn.cursor()

    # Fetch property data
    cursor.execute('''
        SELECT cp.addressLine1, cp.postcode, cp.city, cp.state, cp.sqft, cp.price,
               t.fullName, r.stallName, r.rentalAmount
        FROM combined_properties cp
        JOIN rental r ON cp.id = r.combined_properties_id
        JOIN tenants t ON r.tenantID = t.tenantID
        WHERE r.rentalID = ?
    ''', (property_id,))
    property_data = cursor.fetchone()

    # Fetch payment data
    cursor.execute('''
        SELECT payment_method, payment_period, payment_date, payment_time,
               cardholder_name, receipt
        FROM payment_records 
        WHERE id = ?
    ''', (payment_id,))
    payment_data = cursor.fetchone()

    # Close the database connection
    conn.close()

    if not property_data or not payment_data:
        messagebox.showerror("Error", "Could not find property or payment data")
        return

    # Ask user for save location
    default_filename = f"receipt_{payment_data[1]}_{property_data[7]}.pdf"  # YYYY-MM_StallName.pdf
    pdf_file = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_filename,
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        title="Save Receipt As"
    )

    # If user cancels the save dialog, return without generating PDF
    if not pdf_file:
        return

    try:
        # Create a PDF
        c = canvas.Canvas(pdf_file, pagesize=letter)
        width, height = letter

        # Add content to the PDF
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, height - 100, "Payment Receipt")

        c.setFont("Helvetica", 12)
        # Property Details
        c.drawString(100, height - 150, f"Tenant Name: {property_data[6]}")
        c.drawString(100, height - 170, f"Stall Name: {property_data[7]}")
        c.drawString(100, height - 190, f"Address: {property_data[0]}")
        c.drawString(100, height - 210, f"Postcode: {property_data[1]}")
        c.drawString(100, height - 230, f"City: {property_data[2]}")
        c.drawString(100, height - 250, f"State: {property_data[3]}")

        # Payment Details
        c.drawString(100, height - 290, "Payment Details")
        c.drawString(100, height - 310, f"Payment Method: {payment_data[0]}")
        c.drawString(100, height - 330, f"Payment Period: {payment_data[1]}")
        c.drawString(100, height - 350, f"Payment Date: {payment_data[2]}")
        c.drawString(100, height - 370, f"Payment Time: {payment_data[3]}")
        c.drawString(100, height - 390, f"Amount Paid: RM {property_data[8]:.2f}")

        if payment_data[0] == "Card":
            c.drawString(100, height - 410, f"Cardholder Name: {payment_data[4]}")
        elif payment_data[0] in ["Online Banking", "TNG"]:
            c.drawString(100, height - 410, f"Receipt Reference: {payment_data[5]}")

        # Save the PDF
        c.save()

        messagebox.showinfo("Receipt Generated", f"Receipt saved successfully to:\n{pdf_file}")
        print(f"Receipt saved as {pdf_file}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")
        print(f"Error generating receipt: {e}")

def open_receipt_window(root_window=None, property_id=None, payment_id=None, dashboard_callback=None):
    # Set the appearance mode and default color theme
    set_appearance_mode("light")
    set_default_color_theme("blue")

    # Create the main window
    if root_window is None:
        # If no root window is provided, create a CTk window
        receipt_window = CTk()
    else:
        # If root window is provided, create a CTkToplevel
        receipt_window = CTkToplevel(root_window)
    
    receipt_window.geometry("1920x1080")
    receipt_window.title("Payment")
    receipt_window.resizable(True, True)
    receipt_window.attributes("-fullscreen", True)

    # Fonts (Adjusted sizes for better visibility)
    font_header = ("Arial", 66, "bold")
    font_subheader = ("Arial", 50, "bold")
    font_label = ("Arial", 25)
    font_input = ("Arial", 26)
    font_button = ("Arial", 28)
    font_signup = ("Arial", 24)

    # Positioning headers and buttons on the right frame
    confirm_header = CTkLabel(receipt_window, text="Thanks !", font=font_header, text_color="black")
    confirm_header.place(x=870, y=250)

    # frame
    sub_frame = CTkFrame(receipt_window, fg_color="#897A6E", width=1920, height=1080, corner_radius=35)
    sub_frame.place(x=0, y=400)
    sub_header = CTkLabel(sub_frame, text="Thank you for paying.", font=font_subheader, text_color="white")
    sub_header.place(x=710, y=280)

    tick_image = Image.open("Screenshot 2024-11-18 212559.png")
    tick_image = tick_image.resize((200, 200), Image.LANCZOS)
    tick_ctk_image = CTkImage(light_image=tick_image, size=(200, 200))
    tick_image_label = CTkLabel(sub_frame, image=tick_ctk_image, text="", fg_color="#897A6E")
    tick_image_label.place(x=880, y=70)  # Adjust position as needed
    tick_image_label.image = tick_ctk_image  # Keep a reference to avoid garbage collection

    # Positioning headers and buttons on the right frame
    confirm_header = CTkLabel(sub_frame, text="Your rental has been confirmed", font=font_input, text_color="white")
    confirm_header.place(x=790, y=350)

    # Update the receipt button to use the passed IDs
    receipt_button = CTkButton(
        sub_frame, text="Generate Receipt", font=font_button, text_color="black", fg_color="#C2B8AE",
        hover_color="#c89ef2",
        corner_radius=50, width=160, height=80, 
        command=lambda: generate_receipt_pdf(property_id, payment_id)
    )
    receipt_button.place(x=830, y=440)

    def handle_back_to_dashboard():
        receipt_window.destroy()  # Close the receipt window
        if dashboard_callback:
            dashboard_callback()  # Call the callback function to return to dashboard
        elif root_window:
            root_window.destroy()  # If no callback, just close the root window

    # Back to Home Button with updated command
    backhome_button = CTkButton(
        sub_frame, 
        text="Back to Dashboard", 
        font=font_button, 
        text_color="black", 
        fg_color="#C2B8AE",
        hover_color="#c89ef2",
        corner_radius=50, 
        width=160, 
        height=80, 
        command=handle_back_to_dashboard
    )
    backhome_button.place(x=820, y=550)

    # Handle window close button (X)
    receipt_window.protocol("WM_DELETE_WINDOW", handle_back_to_dashboard)

    receipt_window.mainloop()

if __name__ == "__main__":
    # Create the main CTk window when running directly
    root = CTk()
    root.withdraw()  # Hide the main window
    open_receipt_window(root)
    root.mainloop()

