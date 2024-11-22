import customtkinter
from customtkinter import *

# Initialize the application
app = CTk()
app.geometry("1920x1080")
app.title("Dashboard")
app.resizable(False, False)
app.attributes("-fullscreen",True)

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")

# Set the background color to pure white
app.configure(fg_color="#FFFFFF")

# Header Frame
header_frame = CTkFrame(master=app, width=1920, height=100, fg_color="#FFFFFF")
header_frame.place(x=0, y=0)

# Dashboard Label with house icon
dashboard_label = CTkLabel(
    master=header_frame,
    text="🏠 Dashboard",
    font=("Arial", 50, "bold"),
    width=300,
    height=60,
    bg_color="#FFFFFF",
)
dashboard_label.place(x=50, y=20)

# Right-side icons frame
icons_frame = CTkFrame(master=header_frame, width=300, height=60, fg_color="#FFFFFF")
icons_frame.place(x=1550, y=20)

# Envelope Icon Button with updated emoji and larger size
envelope_button = CTkButton(
    master=icons_frame,
    text="📧",  # Changed emoji
    width=60,
    height=60,
    fg_color=None,
    hover_color=None,
    font=("Arial", 32),  # Increased font size
)
envelope_button.grid(row=0, column=0, padx=10)

# Notification Bell Icon Button with larger emoji
notification_button = CTkButton(
    master=icons_frame,
    text="🔔",
    width=60,
    height=60,
    fg_color=None,
    hover_color=None,
    font=("Arial", 32),  # Increased font size
)
notification_button.grid(row=0, column=1, padx=10)

# User Profile Icon with "Admin 1"
profile_label = CTkLabel(
    master=icons_frame,
    text="👤 Admin 1",
    font=("Arial", 24),
    width=140,
    height=60,
    bg_color="#FFFFFF",
)
profile_label.grid(row=0, column=2, padx=10)

# Activity Label
activity_label = CTkLabel(
    master=app,
    text="Activity",
    font=("Arial", 36, "bold"),
    width=250,
    height=50,
    bg_color="#FFFFFF",
)
activity_label.place(x=50, y=130)

# Action Cards Frame
cards_frame = CTkFrame(master=app, width=1600, height=700, fg_color="#FFFFFF")
cards_frame.place(relx=0.5, y=300, anchor=N)  # Adjusted y to prevent overlap with "Activity" label

# Adjusted sizes and positions
card_width = 400
card_height = 260
card_spacing_x = 50
card_spacing_y = 50

# Calculate start_x to center the cards within cards_frame
total_width = (card_width * 3) + (card_spacing_x * 2)
start_x = (1600 - total_width) / 2
start_y = 0  # Start from top of cards_frame

# Define a list of action cards with their properties
action_cards = [
    {
        "text": "👥\nManage User",
        "fg_color": "#FF6F61",
        "hover_color": "#E85A4F",
    },
    {
        "text": "📝\nManage Stall",
        "fg_color": "#A7C7E7",
        "hover_color": "#92B4D0",
    },
    {
        "text": "💬\nSend Notification",
        "fg_color": "#F9E79F",
        "hover_color": "#F7D488",
    },
    {
        "text": "💵\nPayment Records",
        "fg_color": "#C39BD3",
        "hover_color": "#AF7AC5",
    },
    {
        "text": "📋\nView Problem",
        "fg_color": "#F5CBA7",
        "hover_color": "#EDBB99",
    },
    {
        "text": "🔍\nView Problem",
        "fg_color": "#FF6F61",
        "hover_color": "#E85A4F",
    },
]

# Create and place each action card
for i, card in enumerate(action_cards):
    row = i // 3
    col = i % 3
    x_position = start_x + col * (card_width + card_spacing_x)
    y_position = start_y + row * (card_height + card_spacing_y)

    action_button = CTkButton(
        master=cards_frame,
        text=card["text"],
        width=card_width,
        height=card_height,
        fg_color=card["fg_color"],
        hover_color=card["hover_color"],
        font=("Arial", 32),  # Increased font size for words and emojis
        corner_radius=15,
    )
    action_button.place(x=x_position, y=y_position)

# Footer Frame
footer_frame = CTkFrame(master=app, width=1920, height=50, fg_color="#FFFFFF")
footer_frame.place(x=0, y=1030)  # Positioned at the bottom of the 1080px window

footer_label = CTkLabel(
    master=footer_frame,
    text="© 2024 Your Company Name",
    font=("Arial", 18),
    bg_color="#FFFFFF",
)
footer_label.place(relx=0.5, rely=0.5, anchor=CENTER)

# Start the application
app.mainloop()