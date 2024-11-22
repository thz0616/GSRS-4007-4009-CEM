import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
import sqlite3


# Function to generate and download PDF receipt
def download_receipt():
    try:
        # Connect to the database
        conn = sqlite3.connect("properties.db")
        cursor = conn.cursor()

        # Get the latest payment record
        cursor.execute("""
            SELECT pr.rentalID, pr.payment_method, pr.cardholder_name,
                   r.stallName, r.stallPurpose, r.rentalAmount,
                   cp.addressLine1, cp.addressLine2, cp.postcode, cp.city, cp.state
            FROM payment_records pr
            JOIN rental r ON pr.rentalID = r.rentalID
            JOIN combined_properties cp ON r.combined_properties_id = cp.id
            ORDER BY pr.id DESC LIMIT 1
        """)
        
        payment_data = cursor.fetchone()
        
        if payment_data:
            (rental_id, payment_method, cardholder_name, 
             stall_name, stall_purpose, rental_amount,
             address1, address2, postcode, city, state) = payment_data

            # Create a PDF instance
            pdf = FPDF()
            pdf.add_page()

            # Set font and add content
            pdf.set_font("Arial", "B", size=16)
            pdf.cell(200, 10, txt="Government Stall Rental Receipt", ln=True, align='C')
            pdf.ln(10)  # Line break

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Rental ID: {rental_id}", ln=True)
            pdf.cell(200, 10, txt=f"Payment Method: {payment_method}", ln=True)
            
            if payment_method == "Card":
                pdf.cell(200, 10, txt=f"Cardholder Name: {cardholder_name}", ln=True)
            
            pdf.ln(5)
            pdf.cell(200, 10, txt=f"Stall Name: {stall_name}", ln=True)
            pdf.cell(200, 10, txt=f"Stall Purpose: {stall_purpose}", ln=True)
            
            # Format address
            address = f"{address1}"
            if address2:
                address += f", {address2}"
            address += f", {postcode} {city}, {state}"
            
            pdf.cell(200, 10, txt=f"Address: {address}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt=f"Amount Paid: RM {rental_amount:.2f}", ln=True)

            # Save the PDF to the current directory
            pdf.output("rental_receipt.pdf")

            # Show confirmation message
            messagebox.showinfo("Success", "Receipt downloaded successfully!")
            
            # Close the window after successful download
            root.destroy()
            
        else:
            messagebox.showerror("Error", "No payment record found!")

        # Close the database connection
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Database error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download receipt: {str(e)}")


# Create the Tkinter window
root = tk.Tk()
root.title("Payment Receipt")
root.geometry("1920x1080")
root.attributes("-fullscreen", True)

# Add a title label at the top
title_label = tk.Label(root, text="Payment Confirmed!", font=("Arial", 28, "bold"))
title_label.place(relx=0.5, rely=0.2, anchor="center")

# Add an instruction label above the button
instruction_label = tk.Label(root, text="Press the button below to download your receipt.", font=("Arial", 16))
instruction_label.place(relx=0.5, rely=0.4, anchor="center")

# Add a button to download the receipt with larger size and centered placement
download_button = tk.Button(root, text="Download Receipt", 
                          command=download_receipt, 
                          width=20, 
                          height=2,
                          font=("Arial", 16))
download_button.place(relx=0.5, rely=0.5, anchor="center")

# Run the Tkinter event loop
root.mainloop()
