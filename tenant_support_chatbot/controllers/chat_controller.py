import threading
import json
from ..models.chat_model import ChatModel
from ..views.chat_view import ChatView

class ChatController:
    def __init__(self, parent_window=None, dashboard=None):
        self.model = ChatModel()
        self.view = ChatView(parent_window, dashboard)
        
        if not self.model.API_KEY:
            self.view.show_error("No API key available. Chat functionality will be limited.")
            return

        # Bind events
        self.setup_event_handlers()
        
        # Initialize conversation
        self.view.add_message("assistant", """Hello! I'm your Government Stall Rental System assistant...""")

    def setup_event_handlers(self):
        self.view.message_input.bind("<Return>", self.send_message)
        self.view.send_button.configure(command=lambda: self.send_message())

    def send_message(self, event=None):
        message = self.view.message_input.get("1.0", "end-1c").strip()
        if message:
            # Clear input
            self.view.message_input.delete("1.0", "end")
            
            # Add user message to chat
            self.view.add_message("user", message)
            
            # Disable input while processing
            self.view.message_input.configure(state="disabled")
            self.view.send_button.configure(state="disabled")
            
            # Check relevance
            if not self.model.is_question_relevant(message):
                self.view.add_message("assistant", """I can only assist with questions related to the Government Stall Rental System...""")
                self.view.enable_input()
                return

            # Start API request in separate thread
            threading.Thread(target=self.process_message, args=(message,), daemon=True).start()

        if event:
            return "break"

    def process_message(self, message):
        response = self.model.send_message_to_api(message)
        if not response:
            self.view.window.after(0, self.view.add_message, "assistant", 
                                 "Sorry, I encountered an error. Please try again later.")
            return

        # Create initial empty message
        self.view.window.after(0, self.view.add_message, "assistant", "")
        accumulated_answer = ""

        try:
            for line in response.iter_lines():
                if line:
                    try:
                        json_str = line.decode('utf-8').replace('data: ', '')
                        data = json.loads(json_str)
                        
                        if data.get("event") == "message":
                            new_text = data.get("answer", "")
                            accumulated_answer += new_text
                            self.view.window.after(0, self.view.update_last_message, 
                                                 accumulated_answer)
                        elif data.get("event") == "message_end":
                            self.model.conversation_id = data.get("conversation_id")
                            break
                    except json.JSONDecodeError:
                        continue
        finally:
            self.view.window.after(0, self.view.enable_input) 