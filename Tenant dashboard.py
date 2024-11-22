from customtkinter import *
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog  # Import filedialog for file selection
import os

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.geometry("1920x1080")
root.title("Signup Page")
root.resizable(False, False)
root.attributes("-fullscreen", True)

# Define screen dimensions
screen_width = 1920
screen_height = 1080

# Left and right frame widths
left_frame_width = 500
right_frame_width = 1420  # 1920 - 500 = 1420

# Create left and right frames
left_frame = CTkFrame(root, width=left_frame_width, height=screen_height, fg_color="#c2b8ae")
left_frame.place(x=0, y=0)
right_frame = CTkFrame(root, width=right_frame_width, height=screen_height, fg_color="#fffcf7")
right_frame.place(x=left_frame_width, y=0)


# Fonts (Adjusted sizes for better visibility)
font_header = ("Goudy Old Style", 56, "bold")
font_subheader = ("Arial", 28)
font_label = ("Arial", 20)
font_input = ("Arial", 20)
font_button = ("Arial", 28)
font_signup = ("Goudy Old Style", 28)


# Photo slideshow banner on the top right frame
class PhotoSlideshow:
    def __init__(self, parent, images, delay):
        self.parent = parent
        self.images = [ImageTk.PhotoImage(Image.open(image).resize((1200, 370))) for image in images]
        self.current_image = 0
        self.label = tk.Label(self.parent, image=self.images[self.current_image])
        self.label.place(x=130, y=40)
        self.delay = delay
        self.update_image()

    def update_image(self):
        self.current_image = (self.current_image + 1) % len(self.images)
        self.label.config(image=self.images[self.current_image])
        self.parent.after(self.delay, self.update_image)


# Set image folder path (replace with your own folder containing images)
image_folder = "C:/Users/tanho/OneDrive/Pictures"

# Check if the folder exists and get the list of image files
if os.path.isdir(image_folder):
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                   f.endswith(('.png', '.jpg', '.jpeg'))]
else:
    image_files = []

# Ensure at least two images are available
if len(image_files) < 2:
    placeholder_image = "360_F_107579101_QVlTG43Fwg9Q6ggwF436MPIBTVpaKKtb.jpg"
    image_files.append(placeholder_image)
    if len(image_files) < 2:
        image_files.append(placeholder_image)

# Create the photo slideshow banner
if image_files:
    slideshow = PhotoSlideshow(right_frame, image_files, 3000)

# Positioning headers and buttons on the right frame
activity_header = CTkLabel(right_frame, text="Activity", font=font_header, text_color="black")
activity_header.place(x=150, y=450)

# Create the navigation buttons (placed outside of the payment_frame so they are always visible)
my_store_image = CTkImage(light_image=Image.open("mystore.png"), size=(50, 50))
view_store_image = CTkImage(light_image=Image.open("bank.png"), size=(50, 50))
payment_image = CTkImage(light_image=Image.open("payment.png"), size=(50, 50))
message_image = CTkImage(light_image=Image.open("message.jpg"), size=(50, 50))

# My store Button
my_store_button = CTkButton(
    right_frame, text="My Store", image=my_store_image, font=font_button, text_color="#654633", fg_color="#eaeaf4", hover_color="#c89ef2",
    corner_radius=20, width=1150, height=100
)
my_store_button.place(x=150, y=540)

# View store Button
view_store_button = CTkButton(
    right_frame, text="View Store", image=view_store_image,font=font_button, text_color="#654633", fg_color="#fedee9", hover_color="#c89ef2",
    corner_radius=20, width=1150, height=100
)
view_store_button.place(x=150, y=670)

# Payment Button
payment_button = CTkButton(
    right_frame, text="Payment", image=payment_image,font=font_button, text_color="#654633", fg_color="#ffb98d", hover_color="#c89ef2",
    corner_radius=20, width=1150, height=100
)
payment_button.place(x=150, y=800)

# Message Button
message_button = CTkButton(
    right_frame, text="Message and Announcement", image=message_image, font=font_button, text_color="#f8e5e5", fg_color="#654633",
    hover_color="#c89ef2",
    corner_radius=20, width=1150, height=100
)
message_button.place(x=150, y=930)


# Circular profile image creation
def create_circular_image(image_path, size):
    img = Image.open(image_path).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    circular_img = Image.new("RGBA", (size, size))
    circular_img.paste(img, (0, 0), mask)
    return circular_img


# Load and display profile image in a circular frame
def display_profile_image():
    image_path = "20200722_jjlin_st.jpg"
    if os.path.exists(image_path):
        circular_img = create_circular_image(image_path, 230)
        profile_image_tk = ImageTk.PhotoImage(circular_img)
        profile_label = tk.Label(left_frame, image=profile_image_tk, background="#c2b8ae")
        profile_label.image = profile_image_tk
        profile_label.place(x=140, y=100)
    else:
        print("Profile image not found.")


from tkinter import Frame, Scrollbar

# Function for creating the update PROFILE window
def open_profile_update_window():
    root.destroy()
    profile_window = CTkToplevel(fg_color="#f4f1e9")
    profile_window.geometry("1920x1080")
    profile_window.title("Update Profile")
    profile_window.resizable(False, False)
    profile_window.attributes("-fullscreen", True)

    # Create a frame inside the window that will be scrollable
    scrollable_frame = Frame(profile_window)
    scrollable_frame.place(x=0, y=0, relwidth=1, relheight=1)

    # Add a scrollbar
    scrollbar = Scrollbar(scrollable_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    # Fonts
    font_label = ("Arial", 20)
    font_input = ("Arial", 20)
    font_button = ("Arial", 28)
    font_header = ("Arial", 56, "bold")  # Header font size

    # Function to change profile image
    def change_profile_image():
        new_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if new_image_path:
            display_profile_image()  # Refresh the image in the dashboard
            update_profile_image_in_window(new_image_path)

    # Function to update profile image in the window
    def update_profile_image_in_window(image_path):
        circular_img = create_circular_image(image_path, 200)  # Adjust size as needed
        profile_image_tk = ImageTk.PhotoImage(circular_img)
        profile_image_label.config(image=profile_image_tk)
        profile_image_label.image = profile_image_tk  # Keep reference to avoid garbage collection

    # Profile image label in the update window
    profile_image_label = tk.Label(scrollable_frame)
    profile_image_label.place(x=300, y=150)

    # Call the function to initially display the profile image
    update_profile_image_in_window("20200722_jjlin_st.jpg")

    # Header
    update_header = CTkLabel(master=scrollable_frame, text="Update Profile", font=font_header, text_color="#000000")
    update_header.place(x=900, y=70)

    # User input fields
    username_label = CTkLabel(master=scrollable_frame, text="Username", font=font_label, text_color="#666666")
    username_label.place(x=900, y=200)

    username_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                              border_color="#CCCCCC", fg_color="white", text_color="#000000")
    username_entry.place(x=900, y=240)

    fullname_label = CTkLabel(master=scrollable_frame, text="Fullname", font=font_label, text_color="#666666")
    fullname_label.place(x=900, y=310)

    fullname_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                              border_color="#CCCCCC", fg_color="white", text_color="#000000")
    fullname_entry.place(x=900, y=340)

    phone_label = CTkLabel(master=scrollable_frame, text="Phone Number", font=font_label, text_color="#666666")
    phone_label.place(x=900, y=420)

    phone_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                           border_color="#CCCCCC", fg_color="white", text_color="#000000")
    phone_entry.place(x=900, y=450)

    ic_label = CTkLabel(master=scrollable_frame, text="IC Number", font=font_label, text_color="#666666")
    ic_label.place(x=900, y=520)

    ic_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                        border_color="#CCCCCC", fg_color="white", text_color="#000000")
    ic_entry.place(x=900, y=550)

    # Email, password, confirm password
    email_label = CTkLabel(master=scrollable_frame, text="Email Address", font=font_label, text_color="#666666")
    email_label.place(x=900, y=620)

    email_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                           border_color="#CCCCCC", fg_color="white", text_color="#000000")
    email_entry.place(x=900, y=650)

    password_label = CTkLabel(master=scrollable_frame, text="New password", font=font_label, text_color="#666666")
    password_label.place(x=900, y=720)

    password_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                              border_color="#CCCCCC", fg_color="white", text_color="#000000", show="*")
    password_entry.place(x=900, y=750)

    con_password_label = CTkLabel(master=scrollable_frame, text="Confirm New Password", font=font_label, text_color="#666666")
    con_password_label.place(x=900, y=820)

    con_password_entry = CTkEntry(master=scrollable_frame, width=800, height=60, font=font_input, corner_radius=20,
                                  border_color="#CCCCCC", fg_color="white", text_color="grey", show="*")
    con_password_entry.place(x=900, y=850)

    # Change Profile Image Label
    change_image_label = CTkLabel(scrollable_frame, text="Change Profile Image", font=("Arial", 24, "underline"),
                                  text_color="black", fg_color="#f4f1e9")
    change_image_label.place(x=290, y=380)
    change_image_label.bind("<Button-1>", lambda e: change_profile_image())
    change_image_label.configure(cursor="hand2")

    # Save Changes Button
    save_button = CTkButton(master=scrollable_frame, text="Save Changes", font=font_button, text_color="black",
                            fg_color="#c2b8ae", hover_color="#c89ef2", corner_radius=20, width=800, height=60,
                            command=lambda e: update_profile_image_in_window())
    save_button.place(x=900, y=950)  # Adjust y position higher if needed

    # Link the scrollbar to the frame
    scrollbar.config(command=scrollable_frame.yview)



# Profile Label
profile_label = CTkLabel(left_frame, text="My Profile", font=(font_signup[0], font_signup[1], "underline"),
                       text_color="black", fg_color="#c2b8ae")
profile_label.place(x=195, y=400)  # Positioned higher
profile_label.bind("<Button-1>", lambda e: open_profile_update_window())
profile_label.configure(cursor="hand2")

 # COntact
def on_contact_click():
    print("COntact us clicked")

contact_label = CTkLabel(left_frame, text="Contact us", font=(font_signup[0], font_signup[1], "underline"),
                       text_color="black", fg_color="#c2b8ae")
contact_label.place(x=195, y=460)  # Positioned higher
contact_label.bind("<Button-1>", lambda e: on_contact_click())
contact_label.configure(cursor="hand2")

# Feedback
def on_feedback_click():
    print("Feedback clicked")

feedback_label = CTkLabel(left_frame, text="Feedback", font=(font_signup[0], font_signup[1], "underline"),
                       text_color="black", fg_color="#c2b8ae")
feedback_label.place(x=200, y=520)  # Positioned higher
feedback_label.bind("<Button-1>", lambda e: on_feedback_click())
feedback_label.configure(cursor="hand2")

# Logout
def on_logout_click():
    print("Loging out...")

logout_label = CTkLabel(left_frame, text="Logout", font=(font_signup[0], font_signup[1], "underline"),
                       text_color="black", fg_color="#c2b8ae")
logout_label.place(x=210, y=980)  # Positioned higher
logout_label.bind("<Button-1>", lambda e: on_logout_click())
logout_label.configure(cursor="hand2")

# Call the function to display the profile image
display_profile_image()

# Run the application
root.mainloop()