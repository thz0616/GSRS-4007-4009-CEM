import customtkinter
from customtkinter import *
from PIL import Image
import sqlite3

# Connect to the database
conn = sqlite3.connect('stalls.db')
cursor = conn.cursor()

# Create the table with the new icProblem column
cursor.execute('''
CREATE TABLE IF NOT EXISTS stalls (
    StallID INTEGER PRIMARY KEY AUTOINCREMENT,
    longitude TEXT UNIQUE NOT NULL,
    latitude TEXT NOT NULL,
    status TEXT NOT NULL
    
)
''')
conn.commit()

root = CTk()
root.geometry('1920x1080')
root.attributes("-fullscreen", True)

image = Image.open("Official_portrait_of_Vice_President_Joe_Biden-818x1024.jpg")
background_image = customtkinter.CTkImage(image, size=(1920, 1080))

def closeApp():
    root.destroy()

bg_lbl = customtkinter.CTkLabel(root, text="", image=background_image)
bg_lbl.place(x=0, y=0)

buttonFrame = customtkinter.CTkFrame(root, fg_color="black", width=1920, height=30)
buttonFrame.place(x=0, y=0)

closeButton = customtkinter.CTkButton(root, text="X", command=closeApp, fg_color="black", hover_color="red", text_color="white", width=50, height=30)
closeButton.place(x=1870, y=0)

def upload_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, 'end')
    entry.insert(0, file_path)

def uploaded():
    uploadedLabel = customtkinter.CTkLabel(registerFrame, text="Uploaded!", font=("Verdana", 25, "bold"))
    uploadedLabel.place(x=350, y=400)

def loginWindow():
    global loginFrame
    try:
        registerFrame.destroy()
    except:
        pass
    loginFrame = customtkinter.CTkFrame(root, fg_color=None, width=1000, height=1050)
    loginFrame.place(x=1000, y=30)

    loginLabel = customtkinter.CTkLabel(loginFrame, text="Login", font=('Cooper Black', 60))
    loginLabel.place(x=350, y=300, anchor=CENTER)

    usernameLabel = customtkinter.CTkLabel(loginFrame, text="Username: ", font=("Verdana", 30, "bold"))
    usernameLabel.place(x=100, y=400)

    usernameEntry = customtkinter.CTkEntry(loginFrame, font=("Verdana", 30), width=300)
    usernameEntry.place(x=300, y=400)

    passwordLabel = customtkinter.CTkLabel(loginFrame, text="Password: ", font=("Verdana", 30, "bold"))
    passwordLabel.place(x=100, y=500)

    passwordEntry = customtkinter.CTkEntry(loginFrame, font=("Verdana", 30), width=300, show='*')
    passwordEntry.place(x=300, y=500)

    def login():
        username = usernameEntry.get()
        password = passwordEntry.get()
        cursor.execute("SELECT * FROM tenants WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        if result:
            customtkinter.CTkLabel(loginFrame, text="Login Successful!", font=("Verdana", 20), fg_color="green").place(x=250, y=400)
        else:
            customtkinter.CTkLabel(loginFrame, text="Invalid Username or Password", font=("Verdana", 20), fg_color="red").place(x=250, y=400)

    loginButton = customtkinter.CTkButton(loginFrame, text="Login", font=("Verdana", 30, "bold"), text_color="white", fg_color=None, width=200, height=50, command=login)
    loginButton.place(x=250, y=600)

    switchRegisterButton = customtkinter.CTkButton(loginFrame, text="Not a user? Register now", command=registerWindow, fg_color=None, hover_color=None, font=("Verdana", 20, "bold", "underline"), text_color="#47b0d6")
    switchRegisterButton.place(x=350, y=700, anchor=CENTER)

def registerWindow():
    global registerFrame
    try:
        loginFrame.destroy()
    except:
        pass
    registerFrame = customtkinter.CTkFrame(root, fg_color=None, width=1000, height=1050)
    registerFrame.place(x=1000, y=30)

    registerLabel = customtkinter.CTkLabel(registerFrame, text="Register", font=('Cooper Black', 60))
    registerLabel.place(x=350, y=160, anchor=CENTER)

    usernameLabel = customtkinter.CTkLabel(registerFrame, text="Username: ", font=("Verdana", 25, "bold"))
    usernameLabel.place(x=60, y=250)

    usernameEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300)
    usernameEntry.place(x=350, y=250)

    fullnameLabel = customtkinter.CTkLabel(registerFrame, text="Fullname: ", font=("Verdana", 25, "bold"))
    fullnameLabel.place(x=60, y=290)

    fullnameEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300)
    fullnameEntry.place(x=350, y=290)

    icNumberLabel = customtkinter.CTkLabel(registerFrame, text="IC Number: ", font=("Verdana", 25, "bold"))
    icNumberLabel.place(x=60, y=330)

    icNumberEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300)
    icNumberEntry.place(x=350, y=330)

    emailLabel = customtkinter.CTkLabel(registerFrame, text="Email: ", font=("Verdana", 25, "bold"))
    emailLabel.place(x=60, y=370)

    emailEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300)
    emailEntry.place(x=350, y=370)

    phoneLabel = customtkinter.CTkLabel(registerFrame, text="Phone Number: ", font=("Verdana", 25, "bold"))
    phoneLabel.place(x=60, y=410)

    phoneEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300)
    phoneEntry.place(x=350, y=410)

    passwordLabel = customtkinter.CTkLabel(registerFrame, text="Password: ", font=("Verdana", 25, "bold"))
    passwordLabel.place(x=60, y=450)

    passwordEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300, show='*')
    passwordEntry.place(x=350, y=450)

    confirmPasswordLabel = customtkinter.CTkLabel(registerFrame, text="Confirm Password: ", font=("Verdana", 25, "bold"))
    confirmPasswordLabel.place(x=60, y=490)

    confirmPasswordEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 25), width=300, show='*')
    confirmPasswordEntry.place(x=350, y=490)

    icImageLabel = customtkinter.CTkLabel(registerFrame, text="IC Image: ", font=("Verdana", 25, "bold"))
    icImageLabel.place(x=60, y=530)

    icImageEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 15), width=250)
    icImageEntry.place(x=350, y=530)

    icUploadButton = customtkinter.CTkButton(registerFrame, text="Upload", command=lambda: upload_file(icImageEntry))
    icUploadButton.place(x=350, y=530)

    faceImageLabel = customtkinter.CTkLabel(registerFrame, text="Face Image: ", font=("Verdana", 25, "bold"))
    faceImageLabel.place(x=60, y=570)

    faceImageEntry = customtkinter.CTkEntry(registerFrame, font=("Verdana", 15), width=250)
    faceImageEntry.place(x=350, y=570)

    faceUploadButton = customtkinter.CTkButton(registerFrame, text="Upload", command=lambda: upload_file(faceImageEntry))
    faceUploadButton.place(x=350, y=570)

    def register():
        username = usernameEntry.get()
        fullName = fullnameEntry.get()
        ICNumber = icNumberEntry.get()
        email = emailEntry.get()
        phone = phoneEntry.get()
        password = passwordEntry.get()
        confirmPassword = confirmPasswordEntry.get()
        ICImagePath = icImageEntry.get()
        faceImagePath = faceImageEntry.get()

        if password != confirmPassword:
            customtkinter.CTkLabel(registerFrame, text="Passwords do not match", font=("Verdana", 20), fg_color="red").place(x=250, y=670)
            return
        try:
            cursor.execute("INSERT INTO tenants (username, fullName, ICNumber, emailAddress, phoneNumber, password, ICImagePath, faceImagePath) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (username, fullName, ICNumber, email, phone, password, ICImagePath, faceImagePath))
            conn.commit()
            customtkinter.CTkLabel(registerFrame, text="Registration Successful!", font=("Verdana", 20), fg_color="green").place(x=250, y=670)
        except sqlite3.IntegrityError:
            customtkinter.CTkLabel(registerFrame, text="Username already taken", font=("Verdana", 20), fg_color="red").place(x=250, y=670)

    registerButton = customtkinter.CTkButton(registerFrame, text="Register", font=("Verdana", 30, "bold"), text_color="white", width=200, height=50, command=register)
    registerButton.place(x=250, y=700)

    switchLoginButton = customtkinter.CTkButton(registerFrame, text="Already a user? Login", command=loginWindow, fg_color="#474747", hover_color="#474747", font=("Verdana", 20, "bold", "underline"), text_color="#47b0d6")
    switchLoginButton.place(x=350, y=800, anchor=CENTER)

loginWindow()
root.mainloop()
