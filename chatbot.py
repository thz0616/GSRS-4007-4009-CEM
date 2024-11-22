import customtkinter as ctk
import requests
import json

# Initialize the main application window
app = ctk.CTk()
app.geometry("500x600")
app.title("Chatbot with GPT-4o Model")


# Function to handle sending the message to the NotDiamond API
def send_message():
    user_message = entry.get()
    if user_message.strip() == '':
        return  # Ignore empty messages

    # Display user message in the chatbox
    add_message('User', user_message)

    # Call the NotDiamond API using GPT-4o model
    response = call_notdiamond_api(user_message)

    # Display bot response in the chatbox
    add_message('Bot', response)

    # Clear the entry field
    entry.delete(0, ctk.END)


def call_notdiamond_api(message):
    url = "https://api.notdiamond.com/chat/completions"  # Replace with actual NotDiamond API endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'sk-82d5fd00fbbc370c066ca28b88f7db8e873e56edb7a1ee93'  # Add your NotDiamond API Key here
    }

    payload = {
        "messages": [{"role": "user", "content": message}],
        "model": ["openai/gpt-4o"],
        "tradeoff": "cost"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()

        # Extract the chatbot's response
        if 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            return "No valid response from the model."
    except Exception as e:
        return f"Error: {e}"


# Function to add messages to the chatbox
def add_message(sender, message):
    chatbox.configure(state='normal')
    chatbox.insert(ctk.END, f"{sender}: {message}\n\n")
    chatbox.configure(state='disabled')
    chatbox.see(ctk.END)


# Create the GUI layout
chatbox = ctk.CTkTextbox(app, width=450, height=400, state='disabled')
chatbox.pack(pady=10)

entry = ctk.CTkEntry(app, width=350)
entry.pack(side=ctk.LEFT, padx=10, pady=10)

send_button = ctk.CTkButton(app, text="Send", command=send_message)
send_button.pack(side=ctk.LEFT, padx=10, pady=10)

# Run the main loop
app.mainloop()
