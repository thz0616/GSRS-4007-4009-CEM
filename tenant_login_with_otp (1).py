from customtkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from gmail_otp import generate_otp, send_email
import threading
import time

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.geometry("1920x1080")  # Set window size to 1920x1080 pixels
root.title("Login Page")
root.resizable(False, False)
root.attributes("-fullscreen", True)

# Define screen dimensions
screen_width = 1920
screen_height = 1080

# Left and right frame widths
left_frame_width = 800
right_frame_width = 1120  # 1920 - 800 = 1120

# Create left and right frames
left_frame = CTkFrame(root, width=left_frame_width, height=screen_height)
left_frame.place(x=0, y=0)
right_frame = CTkFrame(root, width=right_frame_width, height=screen_height, fg_color="white")
right_frame.place(x=left_frame_width, y=0)

# Load and set background image on the left frame
def set_background_image(frame, image_path, width, height):
    try:
        image = Image.open(image_path)
        image = image.resize((width, height), Image.LANCZOS)  # Resize the image to fit the frame
        bg_image = ImageTk.PhotoImage(image)

        label = tk.Label(frame, image=bg_image)
        label.image = bg_image  # Keep a reference to avoid garbage collection
        label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Error loading image: {e}")

# Set background image for the left frame
set_background_image(left_frame, "malaysia_skyscrapers_houses_megapolis_night_kuala_lumpur_cities_1920x10801.jpg", left_frame_width, screen_height)

# Fonts (Adjusted sizes for better visibility)
font_header = ("Arial", 72, "bold")
font_label = ("Arial", 28)
font_input = ("Arial", 28)
font_button = ("Arial", 36)

# "Login" Header
login_label = CTkLabel(right_frame, text="Login", font=font_header, text_color="#000000", fg_color="white")
login_label.place(x=150, y=150)

# Username Label and Entry
username_label = CTkLabel(right_frame, text="Username", font=font_label, text_color="#666666", fg_color="white")
username_label.place(x=150, y=350)

username_entry = CTkEntry(right_frame, width=820, height=90, font=font_input, corner_radius=30, border_color="#CCCCCC", fg_color="white", text_color="#000000")
username_entry.place(x=150, y=400)

# Password Label and Entry
password_label = CTkLabel(right_frame, text="Password", font=font_label, text_color="#666666", fg_color="white")
password_label.place(x=150, y=540)

password_entry = CTkEntry(right_frame, width=820, height=90, font=font_input, corner_radius=30, border_color="#CCCCCC", fg_color="white", text_color="#000000", show="*")
password_entry.place(x=150, y=590)

# Login Button
login_button = CTkButton(right_frame, text="LOGIN", font=font_button, text_color="#000000", fg_color="#c2b8ae", hover_color="#c89ef2", corner_radius=30, width=820, height=90)
login_button.place(x=150, y=750)

# Function to open the signup page and close the login window
def open_signup_page():
    root.destroy()  # Close the login window

    signup_window = CTk()  # Create a new window for the signup page
    signup_window.geometry("1920x1080")  # Set the geometry to 1920x1080
    signup_window.title("Signup Page")
    signup_window.attributes("-fullscreen", True)

    # Left and right frame widths (swapped in this case)
    left_frame_width_signup = 800
    right_frame_width_signup = 1120  # 1920 - 800 = 1120

    # Create right and left frames (positions swapped)
    right_frame_signup = CTkFrame(signup_window, width=right_frame_width_signup, height=screen_height, fg_color="white")
    right_frame_signup.place(x=0, y=0)
    left_frame_signup = CTkFrame(signup_window, width=left_frame_width_signup, height=screen_height)
    left_frame_signup.place(x=right_frame_width_signup, y=0)

    # Set background image for the signup page
    set_background_image(left_frame_signup, "malaysia_skyscrapers_houses_megapolis_night_kuala_lumpur_cities_1920x10801.jpg", left_frame_width_signup, screen_height)

    # Signup Page Header
    signup_header = CTkLabel(right_frame_signup, text="Create Account", font=font_header, text_color="#000000", fg_color="white")
    signup_header.place(x=150, y=150)

    # Slides setup
    slides = [CTkFrame(right_frame_signup, width=right_frame_width_signup, height=screen_height, fg_color="white") for _ in range(2)]
    current_slide = 0

    def show_slide(index):
        nonlocal current_slide  # Declare as nonlocal to modify in the outer scope
        slides[current_slide].place_forget()  # Hide the current slide
        slides[index].place(x=0, y=0)  # Show the new slide
        current_slide = index

    # Slide 1 (Username, Full Name, Phone Number, IC Number)
    username_label = CTkLabel(slides[0], text="Username", font=font_label, text_color="#666666", fg_color="white")
    username_label.place(x=150, y=280)

    username_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
    username_entry.place(x=150, y=325)

    fullname_label = CTkLabel(slides[0], text="Fullname", font=font_label, text_color="#666666", fg_color="white")
    fullname_label.place(x=150, y=410)

    fullname_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
    fullname_entry.place(x=150, y=450)

    phone_label = CTkLabel(slides[0], text="Phone Number", font=font_label, text_color="#666666", fg_color="white")
    phone_label.place(x=150, y=530)

    phone_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
    phone_entry.place(x=150, y=570)

    ic_label = CTkLabel(slides[0], text="IC Number", font=font_label, text_color="#666666", fg_color="white")
    ic_label.place(x=150, y=650)

    ic_entry = CTkEntry(slides[0], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC", fg_color="white", text_color="#000000")
    ic_entry.place(x=150, y=685)

    email_label = CTkLabel(slides[1], text="Email Address", font=font_label, text_color="#666666", fg_color="white")
    email_label.place(x=150, y=280)

    email_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20, border_color="#CCCCCC",
                           fg_color="white", text_color="#000000")
    email_entry.place(x=150, y=325)

    password_label = CTkLabel(slides[1], text="Password", font=font_label, text_color="#666666", fg_color="white")
    password_label.place(x=150, y=410)

    password_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20,
                              border_color="#CCCCCC",
                              fg_color="white", text_color="#000000", show="*")
    password_entry.place(x=150, y=450)

    con_password_label = CTkLabel(slides[1], text="Confirm Password", font=font_label, text_color="#666666",
                                  fg_color="white")
    con_password_label.place(x=150, y=530)

    con_password_entry = CTkEntry(slides[1], width=800, height=60, font=font_input, corner_radius=20,
                                  border_color="#CCCCCC",
                                  fg_color="white", text_color="grey", show="*")
    con_password_entry.place(x=150, y=570)

    otp_label = CTkLabel(slides[1], text="OTP", font=font_label, text_color="#666666",
                                  fg_color="white")
    otp_label.place(x=150, y=650)

    otp_entry = CTkEntry(slides[1], width=580, height=60, font=font_input, corner_radius=20,
                                  border_color="#CCCCCC",
                                  fg_color="white", text_color="grey")
    otp_entry.place(x=150, y=690)

    otp_button = CTkButton(slides[1], text="Request OTP", font=("arial", 28), text_color="#FFFFFF",
                            fg_color="#c2b8ae", hover_color="#4682B4", corner_radius=20, width=200, height=60)
    otp_button.place(x=750, y=690)

    status_label = CTkLabel(slides[1], text="", font=("arial", 20), text_color="#666666", fg_color="white")
    status_label.place(x=150, y=760)

    # Add a variable to store the generated OTP
    generated_otp = None

    def send_otp():
        nonlocal generated_otp
        email = email_entry.get()
        if email:
            generated_otp = generate_otp()
            try:
                send_email(email, generated_otp)
                status_label.configure(text="OTP sent successfully!", text_color="green")
                cooldown_thread = threading.Thread(target=cooldown_timer)
                cooldown_thread.start()
            except Exception as e:
                status_label.configure(text=f"Failed to send OTP: {str(e)}", text_color="red")
        else:
            status_label.configure(text="Please enter an email address", text_color="red")

    def cooldown_timer():
        for i in range(30, 0, -1):
            otp_button.configure(text=f"{i}s", state="disabled", 
                                 text_color="white", font=("Arial", 24, "bold"))
            otp_button.update()  # Force the button to update
            time.sleep(1)
        otp_button.configure(text="Request OTP", state="normal", 
                             text_color="white", font=("arial", 28))

    otp_button.configure(command=send_otp)

    # Slide navigation buttons
    next_button = CTkButton(right_frame_signup, text="Back ←", font=font_button, text_color="#FFFFFF", fg_color="#c2b8ae", hover_color="#4682B4", corner_radius=20, width=150, height=50, command=lambda: show_slide(0))
    next_button.place(x=800, y=800)

    back_button = CTkButton(right_frame_signup, text="Next →", font=font_button, text_color="#FFFFFF", fg_color="#c2b8ae", hover_color="#4682B4", corner_radius=20, width=150, height=50, command=lambda: show_slide(1))
    back_button.place(x=600, y=800)

    # Sign up header and labels
    signup_header = CTkLabel(right_frame_signup, text="Create Account", font=font_header, text_color="#000000",
                             fg_color="white")
    signup_header.place(x=150, y=150)

    # Add a variable to store the generated OTP
    generated_otp = None

    def verify_and_signup():
        nonlocal generated_otp
        entered_otp = otp_entry.get()
        if generated_otp is None:
            status_label.configure(text="Please request an OTP first", text_color="red")
        elif entered_otp == generated_otp:
            status_label.configure(text="Sign up successful!", text_color="green")
            # Here you can add code to save the user's information to a database
        else:
            status_label.configure(text="Incorrect OTP. Please try again.", text_color="red")

    # Modify the Signup Button
    signup_button = CTkButton(right_frame_signup, text="SIGN UP", font=font_button, text_color="#000000", fg_color="#c2b8ae",
                              hover_color="#c89ef2", corner_radius=20, width=800, height=70,
                              command=verify_and_signup)
    signup_button.place(x=150, y=900)

    # Login Button on the left frame
    login_button = CTkButton(left_frame_signup, text="LOGIN", font=font_button, text_color="white", fg_color="#c2b8ae",
                             hover_color="#0056b3", width=140, height=60, border_width=2,
                             border_color="#c2b8ae")
    login_button.place(x=360, y=800)

    show_slide(0)  # Start with the first slide
    signup_window.mainloop()  # Start the event loop for the signup window


# Sign up Button on the left frame
sign_up_button = CTkButton(left_frame, text="SIGN UP", font=font_button, text_color="white", fg_color="#c2b8ae",
                           hover_color="#0056b3", width=140, height=60, border_width=2,
                           border_color="#c2b8ae", command=open_signup_page)
sign_up_button.place(x=350, y=800)

root.mainloop()
