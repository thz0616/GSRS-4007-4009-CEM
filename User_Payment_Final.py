from customtkinter import *
from tkinter import Toplevel, Label, Button, Canvas
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import sqlite3
from tkinter import messagebox

def open_payment_window():
    # Set the appearance mode and default color theme
    set_appearance_mode("light")
    set_default_color_theme("blue")

    # Create the main window
    payment_window = Toplevel()
    payment_window.geometry("1920x1080")
    payment_window.title("Payment")
    payment_window.resizable(True, True)
    payment_window.attributes("-fullscreen", True)

    # Connect to the SQLite database
    db_path = "C:/Users/Chicken Chop/PycharmProjects/ALL2/properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Modify the show_frame function to track the active frame
    def show_frame(frame, payment_method=None):
        frame.tkraise()
        global active_payment_method
        if payment_method:
            active_payment_method = payment_method
            print(f"Switched to {active_payment_method} payment method")  # Debugging line

    # Function to insert data into the database
    def insert_payment_data():
        print("Confirm payment button pressed")  # Debugging line to check if the function is triggered

        try:
            print(f"Active payment method: {active_payment_method}")  # Debugging line to check payment method

            if active_payment_method == "Card":
                # Insert credit card data
                name = name_entry.get()
                card_number = card_entry.get()
                expiry = expiry_entry.get()
                cvc = cvc_entry.get()

                print(f"Credit card data: {name}, {card_number}, {expiry}, {cvc}")  # Debugging line to check inputs

                # Perform insertion for credit card details
                cursor.execute('''
                    INSERT INTO payment_records (payment_method, cardholder_name, card_number, expire_date, cvc) 
                    VALUES (?, ?, ?, ?, ?)
                ''', ("Card", name, card_number, expiry, cvc))

            elif active_payment_method == "Online Banking":
                global bank_image_path
                print(f"Bank image path: {bank_image_path}")  # Debugging line to check image path

                if bank_image_path:  # Check if the image path is set
                    cursor.execute('''
                        INSERT INTO payment_records (payment_method, receipt) 
                        VALUES (?, ?)
                    ''', ("Online Banking", bank_image_path))
                else:
                    print("Please upload a bank receipt image.")  # Error message if no image is uploaded

            elif active_payment_method == "TNG":
                global tng_image_path
                print(f"TNG image path: {tng_image_path}")  # Debugging line to check image path

                if tng_image_path:  # Check if the image path is set
                    cursor.execute('''
                        INSERT INTO payment_records (payment_method, receipt) 
                        VALUES (?, ?)
                    ''', ("TNG", tng_image_path))
                else:
                    print("Please upload a TNG receipt image.")  # Error message if no image is uploaded

            # Commit changes to the database
            conn.commit()
            print("Payment data successfully inserted")  # Debugging line to check successful insertion

        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")  # Catch SQLite-specific errors
        except Exception as e:
            print(f"An error occurred: {e}")  # Catch any other errors

    def set_background(app, image_path):
        global bg_image
        image = Image.open(image_path)
        resized_image = image.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(resized_image)
        canvas = Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_image, anchor="nw")
        canvas.image = bg_image

    set_background(payment_window, "C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/payment bakcground.jpg")

    # Fonts (Adjusted sizes for better visibility)
    font_header = ("Arial", 56, "bold")
    font_subheader = ("Arial", 30, "bold")
    font_label = ("Arial", 25)
    font_input = ("Arial", 20)
    font_button = ("Arial", 28)
    font_signup = ("Arial", 24)

    # Add the header image to the bank_frame
    main_image = Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/main.png")
    main_image = main_image.resize((1000, 50), Image.LANCZOS)  # Resize if needed
    main_ctk_image = CTkImage(light_image=main_image, size=(1000, 50))
    main_image_label = CTkLabel(payment_window, image=main_ctk_image, text="", fg_color="#fffcf7")
    main_image_label.place(x=440, y=60)  # Adjust position as needed
    main_image_label.image = main_ctk_image  # Keep a reference to avoid garbage collection

    # Main payment frame (this will always stay visible)
    payment_frame = CTkFrame(payment_window, fg_color="white", width=1150, height=800, corner_radius=15, border_width=2,
                             border_color="black")
    payment_frame.place(x=60, y=200)
    payment_header = CTkLabel(payment_frame, text="How would you like to pay?", font=font_subheader, text_color="black")
    payment_header.place(x=50, y=60)

    # Subframe for the sliding content (this part will change)
    content_frame = CTkFrame(payment_frame, fg_color="white", width=1050, height=660)
    content_frame.place(x=50, y=100)

    # Declare global variables for the image paths
    bank_image_path = None
    tng_image_path = None

    # Image Upload function
    def upload_image_bank():
        global bank_image_path
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((300, 300), Image.LANCZOS)
                ctk_image = CTkImage(light_image=img, size=(300, 300))
                bank_image_label.configure(image=ctk_image, text="")
                bank_image_label.image = ctk_image  # Prevent garbage collection
                bank_image_path = file_path  # Save the image path globally
            except Exception as e:
                print(f"Error loading image: {e}")
        payment_window.lift()  # Bring the payment window to the front

    # Image Upload function for Touch n Go
    def upload_image_tng():
        global tng_image_path  # Declare as global
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((300, 300), Image.LANCZOS)
                ctk_image = CTkImage(light_image=img, size=(300, 300))
                tng_image_label.configure(image=ctk_image, text="")
                tng_image_label.image = ctk_image  # Prevent garbage collection

                # Set the image path to the global variable
                tng_image_path = file_path
                print(f"TNG image uploaded: {tng_image_path}")  # Debugging line to check image path

            except Exception as e:
                print(f"Error loading image: {e}")
        payment_window.lift()  # Bring the payment window to the front

    # Create subframes inside content_frame for different payment methods
    credit_card_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)
    bank_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)
    touch_n_go_frame = CTkFrame(content_frame, fg_color="white", width=1050, height=600)

    for frame in (credit_card_frame, bank_frame, touch_n_go_frame):
        frame.place(x=0, y=0, relwidth=1, relheight=1)

    # Add content to credit card frame
    name_label = CTkLabel(credit_card_frame, text="Cardholder's Name *", font=font_label, text_color="black")
    name_label.place(x=50, y=300)
    name_entry = CTkEntry(credit_card_frame, width=950, height=50, font=font_input, corner_radius=20)
    name_entry.place(x=50, y=350)

    card_label = CTkLabel(credit_card_frame, text="Card Number *", font=font_label, text_color="black")
    card_label.place(x=50, y=430)
    card_entry = CTkEntry(credit_card_frame, width=950, height=50, font=font_input, corner_radius=20)
    card_entry.place(x=50, y=480)

    expiry_label = CTkLabel(credit_card_frame, text="Expire date *", font=font_label, text_color="black")
    expiry_label.place(x=50, y=550)
    expiry_entry = CTkEntry(credit_card_frame, width=450, height=50, font=font_input, corner_radius=20)
    expiry_entry.place(x=50, y=600)

    cvc_label = CTkLabel(credit_card_frame, text="CVC *", font=font_label, text_color="black")
    cvc_label.place(x=550, y=550)
    cvc_entry = CTkEntry(credit_card_frame, width=450, height=50, font=font_input, corner_radius=20)
    cvc_entry.place(x=550, y=600)

    # Add content to bank frame
    upload_bank_image_btn = CTkButton(bank_frame, text="Upload Bank Image", text_color="black", width=200, height=50,
                                      fg_color="#c2b8ae", corner_radius=20, command=upload_image_bank)
    upload_bank_image_btn.place(x=720, y=600)

    # Image display area
    bank_image_label = CTkLabel(bank_frame, text="No Image Uploaded", fg_color="lightgray", width=300, height=300)
    bank_image_label.place(x=670, y=280)

    # Add the bank acc image to the bank_frame
    bank_acc_image = Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/bank acc image.png")
    bank_acc_image = bank_acc_image.resize((400, 400), Image.LANCZOS)  # Resize if needed
    bank_acc_ctk_image = CTkImage(light_image=bank_acc_image, size=(400, 400))
    bank_acc_image_label = CTkLabel(bank_frame, image=bank_acc_ctk_image, text="")
    bank_acc_image_label.place(x=100, y=280)  # Adjust position as needed
    bank_acc_image_label.image = bank_acc_ctk_image  # Keep a reference to avoid garbage collection

    # Add content to touch n go frame
    upload_touch_n_go_image_btn = CTkButton(touch_n_go_frame, text="Upload Touch n Go Image", text_color="black",
                                            width=200, height=50, fg_color="#c2b8ae", corner_radius=20,
                                            command=upload_image_tng)
    upload_touch_n_go_image_btn.place(x=720, y=600)

    # Image display area
    tng_image_label = CTkLabel(touch_n_go_frame, text="No Image Uploaded", fg_color="lightgray", width=300, height=300)
    tng_image_label.place(x=670, y=280)

    # Add the tng image to the bank_frame
    tng_acc_image = Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/tng acc image.png")
    tng_acc_image = tng_acc_image.resize((300, 400), Image.LANCZOS)  # Resize if needed
    tng_acc_ctk_image = CTkImage(light_image=tng_acc_image, size=(300, 400))
    tng_acc_image_label = CTkLabel(touch_n_go_frame, image=tng_acc_ctk_image, text="")
    tng_acc_image_label.place(x=100, y=250)  # Adjust position as needed
    tng_acc_image_label.image = tng_acc_ctk_image  # Keep a reference to avoid garbage collection

    # Show default credit card frame initially
    show_frame(credit_card_frame, "Card")

    # Create the navigation buttons (placed outside of the payment_frame so they are always visible)
    credit_card_image = CTkImage(
        light_image=Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/credit card.png"),
        size=(300, 200))
    bank_image = CTkImage(
        light_image=Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/bank.png"),
        size=(300, 200))
    touch_n_go_image = CTkImage(
        light_image=Image.open("C:/Users/Chicken Chop/PycharmProjects/ALL2/User Payment/Images/touch n go.png"),
        size=(300, 200))

    credit_card_button = CTkButton(payment_window, image=credit_card_image, text="", width=300, height=200, fg_color="white",
                                   hover_color="grey", command=lambda: show_frame(credit_card_frame, "Card"))
    credit_card_button.place(x=120, y=330)

    bank_button = CTkButton(payment_window, image=bank_image, text="", width=300, height=200, fg_color="white",
                            hover_color="grey", command=lambda: show_frame(bank_frame, "Online Banking"))
    bank_button.place(x=490, y=330)

    touch_n_go_button = CTkButton(payment_window, image=touch_n_go_image, text="", width=300, height=200, fg_color="white",
                                  hover_color="grey", command=lambda: show_frame(touch_n_go_frame, "TNG"))
    touch_n_go_button.place(x=850, y=330)

    # Adding rental_frame with black border
    rental_frame = CTkFrame(payment_window, fg_color="white", width=600, height=800, corner_radius=15, border_width=2,
                            border_color="black")
    rental_frame.place(x=1240, y=200)

    rental_header = CTkLabel(rental_frame, text="Rental Details", font=font_subheader, text_color="black")
    rental_header.place(x=40, y=50)

    back_button = CTkButton(payment_window, text="Back", text_color="black", width=100, height=30,
                                       font=font_button, fg_color="#c2b8ae", hover_color="white", corner_radius=20,
                                       command=payment_window.destroy)
    back_button.place(x=100, y=60)

    # Function to fetch and display rental data
    def display_rental_data():
        try:
            # Query to fetch rental data from the database
            cursor.execute("SELECT addressLine1, postcode, city, state, price FROM combined_properties")
            rental_data = cursor.fetchone()  # Assuming there's only one row to display for simplicity

            if rental_data:
                # Unpack data
                address, postcode, city, state, price = rental_data

                # Display the data in the rental frame
                rental_details_text = f"{address},{postcode} {city}\n{state}\n\n\nPrice: RM {price}"
                rental_details_label.configure(text=rental_details_text)
            else:
                rental_details_label.configure(text="No rental data available.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    # Label to display the rental details
    rental_details_label = CTkLabel(rental_frame, text="", font=font_label, text_color="black", justify="left")
    rental_details_label.place(x=40, y=150)  # Adjust position as needed

    from receipt_page import open_receipt_window

    # Call the function to display rental data initially
    display_rental_data()
    # Adding Confirm Payment Button in rental_frame
    confirm_payment_button = CTkButton(rental_frame, text="Confirm Payment", text_color="black", width=200, height=50,
                                       font=font_button, fg_color="#c2b8ae", hover_color="white", corner_radius=20,
                                       command=lambda: [insert_payment_data(), open_receipt_window()])
    confirm_payment_button.place(x=200, y=700)  # Adjust position as needed


    # Run the application
    payment_window.mainloop()

if __name__ == "__main__":
    open_payment_window()
