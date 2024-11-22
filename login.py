from customtkinter import *
import tkinter as tk

# Set the appearance mode and default color theme
set_appearance_mode("light")
set_default_color_theme("blue")

# Create the main window
root = CTk()
root.geometry("1920x1080")  # Set window size to 1920x1080 pixels
root.title("Login Page")
root.resizable(False, False)
root.attributes("-fullscreen",True)

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

# Function to create a vertical gradient on the canvas
def create_gradient(canvas, width, height, color1, color2):
    limit = height
    (r1, g1, b1) = root.winfo_rgb(color1)
    (r2, g2, b2) = root.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / limit
    g_ratio = float(g2 - g1) / limit
    b_ratio = float(b2 - b1) / limit

    for i in range(limit):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = "#%04x%04x%04x" % (nr, ng, nb)
        canvas.create_line(0, i, width, i, fill=color)

# Create a canvas in the left frame and add the gradient background
gradient_canvas = tk.Canvas(left_frame, width=left_frame_width, height=screen_height, highlightthickness=0)
gradient_canvas.place(x=0, y=0)
create_gradient(gradient_canvas, left_frame_width, screen_height, "#d1c4e9", "#f8bbd0")  # Purple to pink gradient

# Fonts (Adjusted sizes for better visibility)
font_header = ("Arial", 72, "bold")
font_subheader = ("Arial", 32)
font_label = ("Arial", 28)
font_input = ("Arial", 28)
font_button = ("Arial", 36)
font_signup = ("Arial", 28)

# "Login" Header
login_label = CTkLabel(
    right_frame, text="Login", font=font_header, text_color="#000000", fg_color="white"
)
login_label.place(x=150, y=150)  # Positioned at y=150

# Subheader
welcome_label = CTkLabel(
    right_frame,
    text="Welcome back! Please login to your account.",
    font=font_subheader,
    text_color="#808080",
    fg_color="white",
)
welcome_label.place(x=150, y=250)

# Username Label
username_label = CTkLabel(
    right_frame, text="Username", font=font_label, text_color="#666666", fg_color="white"
)
username_label.place(x=150, y=350)

# Username Entry
username_entry = CTkEntry(
    right_frame,
    width=820,  # Increased width to fill more space
    height=90,  # Increased height
    font=font_input,
    corner_radius=30,  # Increased corner radius
    border_color="#CCCCCC",
    fg_color="white",
    text_color="#000000",
)
username_entry.place(x=150, y=400)

# Password Label
password_label = CTkLabel(
    right_frame, text="Password", font=font_label, text_color="#666666", fg_color="white"
)
password_label.place(x=150, y=540)

# Password Entry
password_entry = CTkEntry(
    right_frame,
    width=820,
    height=90,  # Increased height
    font=font_input,
    corner_radius=30,  # Increased corner radius
    border_color="#CCCCCC",
    fg_color="white",
    text_color="#000000",
    show="*",
)
password_entry.place(x=150, y=590)

# Login Button
login_button = CTkButton(
    right_frame,
    text="LOGIN",
    font=font_button,
    text_color="#000000",
    fg_color="#d0a9f5",
    hover_color="#c89ef2",
    corner_radius=30,  # Increased corner radius
    width=820,
    height=90,
)
login_button.place(x=150, y=750)  # Shifted down by 50 pixels (y=740)

# "New user? Sign up" Labels
def on_signup_click():
    # Placeholder for signup action
    print("Sign up clicked")

new_user_label = CTkLabel(
    right_frame,
    text="New user? ",
    font=font_signup,
    text_color="#808080",
    fg_color="white",
)
new_user_label.place(x=150, y=930)  # Positioned at y=930

sign_up_label = CTkLabel(
    right_frame,
    text="Sign up",
    font=(font_signup[0], font_signup[1], "underline"),
    text_color="#9a68ed",
    fg_color="white",
)
sign_up_label.place(x=320, y=930)
sign_up_label.bind("<Button-1>", lambda e: on_signup_click())
sign_up_label.configure(cursor="hand2")

root.mainloop()