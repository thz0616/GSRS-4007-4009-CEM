from customtkinter import *
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import admin_approve_rentals as approval
import adminSystemInfo20241014 as system_info
import admin_ai_report as ai_report
import announcement_page as announcement
import admin_manage_user as manage_user
import adminmanagestall as manage_stall
import payment_overview_final as payment_overview
import view_feedback as feedback
import admin_update_profile as update_profile
import sys
import sqlite3

ctk.set_appearance_mode("Light")

def show_dashboard(root, current_frame):
    # Hide current frame
    current_frame.pack_forget()
    
    # Show dashboard frame
    dashboard_frame.pack(fill="both", expand=True)

def switch_to_page(page_type, root, dashboard_frame):
    # Hide dashboard
    dashboard_frame.pack_forget()
    
    # Create white transition frame
    white_frame = ctk.CTkFrame(master=root, fg_color="white")
    white_frame.pack(fill="both", expand=True)
    
    if page_type == "system":
        # Switch to system info page with the show_dashboard callback
        system_info.show_admin_system_info(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "approval":
        # Switch to approval page with the show_dashboard callback
        approval.show_admin_approval(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "problem":
        # Switch to AI report page with the show_dashboard callback
        ai_report.show_admin_ai_report(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "user":
        # Switch to user management page with the show_dashboard callback
        manage_user.show_admin_manage_user(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "stall":
        # Switch to stall management page with the show_dashboard callback
        manage_stall.show_admin_manage_stall(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "announcement":
        announcement.show_announcement_page(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "payment":
        # Switch to payment overview page with the show_dashboard callback
        payment_overview.show_payment_overview(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "notification":
        # Switch to feedback view page with the show_dashboard callback
        feedback.show_view_feedback(root, white_frame, lambda: show_dashboard(root, white_frame))
    elif page_type == "profile":
        # Switch to profile update page with the show_dashboard callback
        update_profile.show_admin_update_profile(root, white_frame, lambda: show_dashboard(root, white_frame))
    # Add other page types as needed...

def get_admin_info(admin_id):
    """Get admin information from database"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM admin WHERE id = ?", (admin_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return username
        return "Admin"
    except Exception as e:
        print(f"Error getting admin info: {e}")
        return "Admin"
    finally:
        if conn:
            conn.close()

def main():
    global dashboard_frame
    
    # Get admin ID from command line arguments
    admin_id = None
    if len(sys.argv) > 1:
        admin_id = sys.argv[1]
    
    # Initialize the application
    app = CTk()
    app.geometry("1920x1080")
    app.title("Dashboard")
    app.resizable(False, False)
    app.attributes("-fullscreen",True)

    # Set the background color to pure white
    app.configure(fg_color="#FFFCF7")

    # Create main dashboard frame
    dashboard_frame = CTkFrame(master=app, fg_color="#FFFCF7")
    dashboard_frame.pack(fill="both", expand=True)

    # Header Frame
    header_frame = CTkFrame(master=dashboard_frame, width=1920, height=120, fg_color="#FFFCF7")
    header_frame.place(x=0, y=0)

    # Right-side icons frame - adjust position to move everything left
    icons_frame = CTkFrame(master=header_frame, width=400, height=120, fg_color="#FFFCF7")  # Width stays the same
    icons_frame.place(x=1350, y=50)  # Changed x from 1450 to 1350 to move everything left

    # Envelope Icon Button
    envelope_button = CTkButton(
        master=icons_frame,
        text="📧",
        text_color="black",
        width=60,
        height=60,
        fg_color="#fffcf7",
        hover_color=None,
        font=("Arial", 42),
        command=lambda: switch_to_page("announcement", app, dashboard_frame)
    )
    envelope_button.grid(row=0, column=0, padx=10)

    line_label = CTkLabel(
        master=icons_frame,
        text="|",
        text_color="black",
        font=("Arial", 42)
    )
    line_label.grid(row=0, column=2, padx=10)

    # Notification Bell Icon Button with larger emoji
    notification_button = CTkButton(
        master=icons_frame,
        text="🔔",
        text_color="black",
        width=60,
        height=60,
        fg_color="#fffcf7",
        hover_color=None,
        font=("Arial", 32),
        command=lambda: switch_to_page("notification", app, dashboard_frame)
    )
    notification_button.grid(row=0, column=1, padx=10)

    # User Profile Icon with username
    admin_username = get_admin_info(admin_id) if admin_id else "Admin"
    profile_button = CTkButton(
        master=icons_frame,
        text=f"👤 {admin_username}",
        text_color="black",
        font=("Arial", 25),
        width=140,
        height=60,
        fg_color="#fffcf7",
        hover_color=None,
        corner_radius=20,
        command=lambda: switch_to_page("profile", app, dashboard_frame)
    )
    profile_button.grid(row=0, column=3, padx=10)

    # Add another separator
    line_label2 = CTkLabel(
        master=icons_frame,
        text="|",
        text_color="black",
        font=("Arial", 42)
    )
    line_label2.grid(row=0, column=4, padx=10)

    # Add logout function
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            app.destroy()
            # Start the login program
            import subprocess
            import os
            import sys
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            login_path = os.path.join(current_dir, "admin_signup.py")
            
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen([sys.executable, login_path], 
                            creationflags=CREATE_NO_WINDOW)

    # Logout Button
    logout_button = CTkButton(
        master=icons_frame,
        text="Logout",
        text_color="black",
        font=("Arial", 25),
        width=100,
        height=60,
        fg_color="#FFE4E4",  # Light red background
        hover_color="#FFD1D1",  # Slightly darker red on hover
        corner_radius=20,
        command=logout
    )
    logout_button.grid(row=0, column=5, padx=10)

    # Dashboard Label with house icon
    dashboard_label = CTkLabel(
        dashboard_frame, 
        text="🏠 Dashboard",
        font=("Arial", 70, "bold"),
        width=300,
        height=60,
        bg_color="#FFFCF7",
    )
    dashboard_label.place(x=400, y=150)

    # Activity Label
    activity_label = CTkLabel(
        dashboard_frame,
        text="Activity",
        font=("Arial", 43, "bold"),
        width=250,
        height=50,
        bg_color="#FFFCF7",
    )
    activity_label.place(x=350, y=290)

    # Load images
    manage_user_image = CTkImage(light_image=Image.open("manage_user.png"), size=(350, 230))
    manage_stall_image = CTkImage(light_image=Image.open("manage_stall.png"), size=(360, 230))
    manage_system_image = CTkImage(light_image=Image.open("system_management.png"), size=(363, 230))
    payment_record_image = CTkImage(light_image=Image.open("payment_records.png"), size=(350, 230))
    pending_image = CTkImage(light_image=Image.open("pending_approval.png"), size=(350, 230))
    view_problem_image = CTkImage(light_image=Image.open("system_analysis.png"), size=(350, 230))

    # Create buttons with updated commands
    manage_user_button = CTkButton(
        dashboard_frame,
        image=manage_user_image,
        text='',
        width=350,
        height=230,
        fg_color="#FD7171",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("user", app, dashboard_frame)
    )
    manage_user_button.place(x=400,y=420)

    manage_stall_button = CTkButton(
        dashboard_frame,
        image=manage_stall_image,
        text="",
        width=350,
        height=230,
        fg_color="#ADC6FF",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("stall", app, dashboard_frame)
    )
    manage_stall_button.place(x=799,y=420)

    manage_banner = CTkButton(
        dashboard_frame,
        image=manage_system_image,
        text="",
        width=350,
        height=230,
        fg_color="#FFE4A7",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("system", app, dashboard_frame)
    )
    manage_banner.place(x=1205, y=420)

    payment_records_button = CTkButton(
        dashboard_frame,
        text="",
        image=payment_record_image,
        width=350,
        height=230,
        fg_color="#A277F6",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("payment", app, dashboard_frame)
    )
    payment_records_button.place(x=400, y=700)

    pending_button = CTkButton(
        dashboard_frame,
        image=pending_image,
        text=" ",
        width=350,
        height=230,
        fg_color="#FFBA8E",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("approval", app, dashboard_frame)
    )
    pending_button.place(x=796, y=700)

    view_problem_button = CTkButton(
        dashboard_frame,
        image=view_problem_image,
        text=" ",
        width=350,
        height=230,
        fg_color="#FD7171",
        hover_color="#FFFCF7",
        command=lambda: switch_to_page("problem", app, dashboard_frame)
    )
    view_problem_button.place(x=1200, y=700)

    # Start the application
    app.mainloop()

if __name__ == "__main__":
    main()