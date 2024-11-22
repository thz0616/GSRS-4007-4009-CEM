import customtkinter as ctk
from feedback_db import insert_feedback

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.attributes('-fullscreen', True)
root.title("Feedback")
root.configure(fg_color="#897a6e")

ctk.CTkLabel(root, text="Feedback", font=("Arial", 24, "bold"), text_color="white").pack(pady=20)
ctk.CTkLabel(root, text="We want to know your thoughts and experience", font=("Arial", 14)).pack(pady=10)

clicked_emotion = None

def clicked(emotion):
    global clicked_emotion
    clicked_emotion = emotion
    print(f"You clicked: {emotion}")

def validate_and_save_feedback():
    name = name_entry.get()
    emotion = clicked_emotion
    comments = comment_entry.get()

    if not name or not emotion:
        ctk.CTkLabel(root, text="Name and Emotion are required!", font=("Arial", 12), text_color="red").pack(pady=10)
        return

    insert_feedback(name, emotion, comments)
    print("Feedback saved!")

# Name entry
ctk.CTkLabel(root, text="Enter your name", font=("Arial", 14)).pack(pady=10)
name_entry = ctk.CTkEntry(root, width=400, font=("Arial", 14))
name_entry.pack(pady=10)

# Buttons for emoji selection
frame = ctk.CTkFrame(root)
frame.pack(pady=20)

for emoji in ["😊", "😐", "☹️"]:
    button = ctk.CTkButton(frame, text=emoji, font=("Arial", 24), command=lambda e=emoji: clicked(e))
    button.pack(side="left", padx=10)

# Comments section
ctk.CTkLabel(root, text="Any additional comments?", font=("Arial", 14)).pack(pady=10)
comment_entry = ctk.CTkEntry(root, width=400, font=("Arial", 14))
comment_entry.pack(pady=10)

# Save button
save_button = ctk.CTkButton(root, text="SAVE CHANGES", font=("Arial", 14), fg_color="#c2b8ae", hover_color="#d3c8bb", command=validate_and_save_feedback)
save_button.pack(pady=20)

root.mainloop()
