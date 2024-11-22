from .controllers.chat_controller import ChatController

class TenantSupportChatbot:
    def __init__(self, parent_window=None, dashboard=None):
        self.controller = ChatController(parent_window, dashboard)
        
        if not parent_window:
            self.controller.view.window.mainloop() 