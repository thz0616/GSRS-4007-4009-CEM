import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox

class ChatView:
    def __init__(self, parent_window=None, dashboard=None):
        # Define color constants
        self.SIDEBAR_COLOR = "#E8DCD0"
        self.MAIN_BG_COLOR = "#F2EAE4"
        self.USER_MSG_COLOR = "#E8DCD0"
        self.BOT_MSG_COLOR = "#F2EAE4"
        self.TEXT_COLOR = "#6B4423"
        self.ACCENT_COLOR = "#8B4513"
        self.INPUT_BG_COLOR = "#FFFFFF"

        self.window = parent_window or ctk.CTk()
        if not parent_window:
            self.window.title("Government Stall Rental Support")
            self.window.geometry("2000x1200")
        
        self.window.configure(fg_color=self.MAIN_BG_COLOR)
        self.dashboard = dashboard
        
        # Create main container with sidebar and chat area
        self.create_layout()

    def create_layout(self):
        # Create sidebar
        self.sidebar = ctk.CTkFrame(
            self.window,
            fg_color=self.SIDEBAR_COLOR,
            width=400
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Back button
        back_btn = ctk.CTkButton(
            self.sidebar,
            text="← Back",
            command=self.go_back,
            fg_color=self.ACCENT_COLOR,
            hover_color="#6B4423",
            height=50,
            width=340,
            font=("Arial Bold", 24),
            text_color="#FFFFFF"
        )
        back_btn.pack(pady=(30, 15), padx=30)

        # New Chat button
        new_chat_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New Chat",
            command=self.new_chat,
            fg_color=self.ACCENT_COLOR,
            hover_color="#6B4423",
            height=60,
            width=340,
            font=("Arial Bold", 24),
            text_color="#FFFFFF"
        )
        new_chat_btn.pack(pady=(15, 30), padx=30)

        # Add a separator
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="#404040")
        separator.pack(fill="x", padx=20, pady=10)

        # Quick access buttons for common topics
        topics = [
            ("Check-in Guide", "🔑"),
            ("Face Verification Help", "👤"),
            ("Rental Status", "📊"),
            ("System Navigation", "🧭"),
            ("Policies & Rules", "📋")
        ]
        
        for topic, icon in topics:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {topic}",
                command=lambda t=topic: self.quick_access_topic(t),
                fg_color="transparent",
                hover_color="#D4C3B3",
                height=55,
                width=340,
                anchor="w",
                font=("Arial", 22),
                text_color=self.TEXT_COLOR
            )
            btn.pack(pady=8, padx=30)

        # Create main chat area
        self.main_area = ctk.CTkFrame(
            self.window,
            fg_color=self.MAIN_BG_COLOR
        )
        self.main_area.pack(side="right", fill="both", expand=True)

        # Create chat display area
        self.chat_frame = ctk.CTkScrollableFrame(
            self.main_area,
            fg_color=self.MAIN_BG_COLOR
        )
        self.chat_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Create input area
        self.create_input_area()

    def create_input_area(self):
        self.input_frame = ctk.CTkFrame(
            self.main_area,
            fg_color=self.MAIN_BG_COLOR,
            height=150
        )
        self.input_frame.pack(fill="x", side="bottom", padx=50, pady=40)
        self.input_frame.pack_propagate(False)

        # Create text input
        self.message_input = ctk.CTkTextbox(
            self.input_frame,
            height=90,
            fg_color=self.INPUT_BG_COLOR,
            text_color=self.TEXT_COLOR,
            wrap="word",
            font=("Arial", 24),
            border_width=1,
            border_color="#D4C3B3"
        )
        self.message_input.pack(fill="x", padx=(0, 90), pady=30)

        # Create send button with emoji
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=70,
            height=70,
            command=None,  # Will be set by controller
            fg_color=self.ACCENT_COLOR,
            hover_color="#6B4423",
            font=("Arial", 36),
            text_color="#FFFFFF"
        )
        self.send_button.place(relx=0.97, rely=0.5, anchor="center")

    def add_message(self, sender, message):
        # Create message frame
        bg_color = self.USER_MSG_COLOR if sender == "user" else self.BOT_MSG_COLOR
        message_frame = ctk.CTkFrame(
            self.chat_frame,
            fg_color=bg_color,
            corner_radius=10
        )
        message_frame.pack(fill="x", pady=10)

        # Create message content frame
        content_frame = ctk.CTkFrame(
            message_frame,
            fg_color=bg_color
        )
        content_frame.pack(fill="x", padx=300, pady=25)

        # Add sender icon/label
        icon = "👤" if sender == "user" else "🤖"
        sender_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Arial", 28)
        )
        sender_label.pack(anchor="w", pady=(0, 10))

        # Handle markdown formatting
        formatted_message = self._convert_markdown(message)

        # Add message text with proper formatting
        if "```" in message:  # Code block
            message_box = ctk.CTkTextbox(
                content_frame,
                height=120,
                wrap="none",
                font=("Courier", 20),
                text_color=self.TEXT_COLOR,
                fg_color="#F5F5F5"
            )
            message_box.pack(fill="x", pady=5)
            message_box.insert("1.0", formatted_message)
            message_box.configure(state="disabled")
        else:
            message_label = ctk.CTkLabel(
                content_frame,
                text=formatted_message,
                wraplength=800,
                justify="left",
                text_color=self.TEXT_COLOR,
                font=("Arial", 24)
            )
            message_label.pack(anchor="w")

        # Auto-scroll to the bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def update_last_message(self, new_text):
        """Update the last message in the chat frame"""
        if self.chat_frame.winfo_children():
            last_message = self.chat_frame.winfo_children()[-1]
            content_frame = last_message.winfo_children()[0]
            
            # Remove existing message label
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            # Add bot emoji
            sender_label = ctk.CTkLabel(
                content_frame,
                text="🤖",
                font=("Arial", 28)
            )
            sender_label.pack(anchor="w", pady=(0, 10))
            
            # Add updated message with larger font
            message_label = ctk.CTkLabel(
                content_frame,
                text=self._convert_markdown(new_text),
                wraplength=800,
                justify="left",
                text_color=self.TEXT_COLOR,
                font=("Arial", 24)
            )
            message_label.pack(anchor="w")

    def _convert_markdown(self, text):
        """Convert markdown to formatted text"""
        # Handle code blocks
        if "```" in text:
            # Extract code between backticks
            parts = text.split("```")
            result = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Outside code block
                    result.append(self._format_regular_text(part))
                else:  # Inside code block
                    result.append(part.strip())
            return "\n".join(result)
        else:
            return self._format_regular_text(text)

    def _format_regular_text(self, text):
        """Format regular text with markdown"""
        lines = []
        for line in text.split('\n'):
            # Headers
            if line.startswith('# '):
                line = f"\n{line[2:].upper()}\n"
            elif line.startswith('## '):
                line = f"\n{line[3:].title()}\n"
            
            # Bold
            while '**' in line:
                line = line.replace('**', '', 2)
            
            # Lists
            if line.strip().startswith('- '):
                line = '  • ' + line[2:]
            elif line.strip().startswith('* '):
                line = '  • ' + line[2:]
            
            # Numbered lists
            if line.strip() and line[0].isdigit() and line[1:].startswith('. '):
                line = f"  {line[0]}) {line[3:]}"
            
            lines.append(line)
        
        return '\n'.join(lines)

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def enable_input(self):
        self.message_input.configure(state="normal")
        self.send_button.configure(state="normal")
        self.message_input.focus()

    def go_back(self):
        if self.dashboard and hasattr(self.dashboard, 'master'):
            self.dashboard.master.deiconify()
        self.window.destroy()

    def new_chat(self):
        # Clear chat history
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Add initial message
        self.add_message("assistant", """Hello! I'm your Government Stall Rental System assistant. I can help you with:

1. Check-in procedures and requirements
2. Understanding your rental status
3. Using the face verification system
4. Navigating the rental management system
5. Understanding rental policies and regulations

What would you like to know about?""")

    def quick_access_topic(self, topic):
        topic_prompts = {
            "Check-in Guide": "Please explain the daily check-in process step by step.",
            "Face Verification Help": "How does the face verification system work and what should I do if it fails?",
            "Rental Status": "How can I check my current rental status and payment information?",
            "System Navigation": "Please explain how to navigate the main features of the rental system.",
            "Policies & Rules": "What are the key policies and rules I need to follow as a tenant?"
        }
        
        self.message_input.delete("1.0", "end")
        self.message_input.insert("1.0", topic_prompts[topic])
        self.send_button.invoke()  # Trigger the send button's command 