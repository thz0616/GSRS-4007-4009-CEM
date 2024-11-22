import sqlite3
import requests
import json

class ChatModel:
    def __init__(self):
        self.API_BASE_URL = "https://api.dify.ai/v1"
        self.API_KEY = self.get_api_key_from_db()
        self.conversation_id = None

    def get_api_key_from_db(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM systemInformation ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
        except sqlite3.Error:
            return None
        finally:
            if conn:
                conn.close()

    def is_question_relevant(self, message):
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        
        relevance_check_prompt = f"""You are a filter for a Government Stall Rental System chatbot.
Your task is to determine if the user's question is related to:
1. Daily check-in procedures
2. Face verification system
3. Rental status
4. System navigation
5. Rental policies and rules
6. Any other aspects of the Government Stall Rental System

User Question: {message}

Respond with only 'YES' if the question is related to the system, or 'NO' if it's unrelated.
For example:
- "How do I check in?" -> YES
- "What's the weather today?" -> NO
- "Why did my face verification fail?" -> YES
- "Can you recommend a restaurant?" -> NO"""

        try:
            response = requests.post(
                f"{self.API_BASE_URL}/chat-messages",
                headers=headers,
                json={
                    "inputs": {},
                    "query": relevance_check_prompt,
                    "user": "system",
                    "response_mode": "blocking"  # Use blocking mode for immediate response
                }
            )
            
            if response.status_code == 200:
                answer = response.json().get('answer', '').strip().upper()
                return answer == 'YES'
            
            return True  # Default to True if API call fails
            
        except Exception as e:
            print(f"Error checking question relevance: {str(e)}")
            return True  # Default to True if there's an error

    def send_message_to_api(self, message):
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a helpful assistant for tenants using the Government Stall Rental System. Always respond in a friendly and helpful manner, as if you're having a conversation with the tenant. Use the following knowledge to answer the tenant's question accurately. If the question cannot be answered using this knowledge, politely say so and stick to what you know about the system.

SYSTEM KNOWLEDGE:

Daily Check-in System:
- Tenants need to perform one check-in per day at their rental property
- For check-in, you need:
  • A device with a working camera
  • Internet connection
  • Location services enabled
- The system verifies:
  • Your identity through face verification
  • Your location at the rental property
- You'll get one of these status messages:
  • "Check-in Successfully" - All verifications passed
  • "Partially Check-in (Camera verification passed)" - Only face verified
  • "Partially Check-in (Location verification passed)" - Only location verified
  • "Check-in Failed" - No verifications failed

Payment System:
- Payment Rules:
  • First Month: You must pay the full amount even if starting mid-month
  • Last Month: You don't need to pay for your final partial month to avoid overlap
  • Regular months: Pay your full monthly rental amount
- Payment Options:
  • Credit/Debit Card: Make direct payments with immediate confirmation
  • Online Banking: Transfer to our bank account and upload your receipt
  • Touch 'n Go: Pay with your eWallet and upload your receipt

Feedback System:
- Types of Feedback:
  • Complaints: Report issues with your rental property
  • System Issues: Report technical problems with the rental system
  • Payment Issues: Report problems with payment processing
  • Feature Requests: Suggest improvements or new features
- How to Submit:
  • Choose a feedback category
  • Provide a clear subject
  • Write detailed comments about your concern
  • Submit using the SEND button

TENANT QUESTION: {message}

Please provide a clear, helpful response using the above knowledge. Format your response in a conversational way and use bullet points or numbers when listing steps or options."""
        
        data = {
            "inputs": {},
            "query": prompt,
            "user": "tenant",
            "response_mode": "streaming",
            "conversation_id": self.conversation_id
        }

        try:
            response = requests.post(
                f"{self.API_BASE_URL}/chat-messages",
                headers=headers,
                json=data,
                stream=True
            )
            return response if response.status_code == 200 else None
        except Exception:
            return None 