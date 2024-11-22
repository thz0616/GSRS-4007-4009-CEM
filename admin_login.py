import customtkinter
from customtkinter import *
from PIL import Image
import PIL

Button = customtkinter.CTkButton
Frame = customtkinter.CTkFrame
Entry = customtkinter.CTkEntry
Label = customtkinter.CTkLabel

root=CTk()

root.geometry('1920x1080')
root.attributes("-fullscreen", True)

image = PIL.Image.open(r"C:\Users\tanho\PycharmProjects\all project 2\malaysia_skyscrapers_houses_megapolis_night_kuala_lumpur_cities_1920x10801.jpg")
background_image = customtkinter.CTkImage(image, size=(1920, 1080))

def closeApp():
    root.destroy()

def bg_resizer(e):
    if e.widget is root:
        i = customtkinter.CTkImage(image, size=(e.width, e.height))
        bg_lbl.configure(text="", image=i)

bg_lbl = customtkinter.CTkLabel(root, text="", image=background_image)
bg_lbl.place(x=0, y=0)

buttonFrame = Frame(root,fg_color="black",width=1920,height=30)
buttonFrame.place(x=0,y=0)

closeButton = Button(root, text="X", command=closeApp,fg_color="black",hover_color="red",text_color="white",width=50,height=30)
closeButton.place(x=1870,y=0)

def loginWindow():
    global loginFrame
    try:
        registerFrame.destroy()
    except:
        pass
    loginFrame = Frame(root, fg_color="#474747",width=700,height=600)
    loginFrame.place(x=610,y=240)

    loginLabel = Label(loginFrame,text="Login", font=('Cooper Black',60))
    loginLabel.place(x=350,y=100,anchor=CENTER)

    usernameLabel = Label(loginFrame, text="Username: ", font= ("Verdana", 30, "bold"))
    usernameLabel.place(x=100, y=200)

    usernameEntry = Entry(loginFrame, font= ("Verdana", 30),width=300)
    usernameEntry.place(x=300, y=200)

    passwordLabel = Label(loginFrame, text="Password: ", font= ("Verdana", 30, "bold"))
    passwordLabel.place(x=100, y=300)

    passwordEntry = Entry(loginFrame, font= ("Verdana", 30),width=300)
    passwordEntry.place(x=300, y=300)

    loginButton = Button(loginFrame, text="Login", font= ("Verdana", 30, "bold"),text_color="white",width=200,height=50)
    loginButton.place(x=250,y=400)

    switchRegisterButton = Button(loginFrame, text="Not a user? Register now", command=registerWindow, fg_color="#474747",hover_color="#474747", font= ("Verdana", 20, "bold","underline"),text_color="#47b0d6")
    switchRegisterButton.place(x=350,y=500, anchor=CENTER)

def registerWindow():
    global registerFrame
    loginFrame.destroy()
    registerFrame = Frame(root, fg_color="#474747",width=700,height=800)
    registerFrame.place(x=610,y=140)

    registerLabel = Label(registerFrame,text="Register", font=('Cooper Black',60))
    registerLabel.place(x=350,y=90,anchor=CENTER)

    usernameLabel = Label(registerFrame, text="Username: ", font= ("Verdana", 25, "bold"))
    usernameLabel.place(x=100, y=190)

    usernameEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    usernameEntry.place(x=300, y=190)

    fullnameLabel = Label(registerFrame, text="Fullname: ", font= ("Verdana", 25, "bold"))
    fullnameLabel.place(x=100, y=260)

    fullnameEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    fullnameEntry.place(x=300, y=260)

    passCodeLabel = Label(registerFrame, text="PassCode: ", font= ("Verdana", 25, "bold"))
    passCodeLabel.place(x=100, y=330)

    passCodeEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    passCodeEntry.place(x=300, y=330)

    phoneNumberLabel = Label(registerFrame, text="H/P: ", font= ("Verdana", 25, "bold"))
    phoneNumberLabel.place(x=100, y=400)

    phoneNumberEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    phoneNumberEntry.place(x=300, y=400)

    emailLabel = Label(registerFrame, text="Email: ", font=("Verdana", 25, "bold"))
    emailLabel.place(x=100, y=470)

    emailEntry = Entry(registerFrame, font=("Verdana", 25), width=300)
    emailEntry.place(x=300, y=470)

    passwordLabel = Label(registerFrame, text="Password: ", font= ("Verdana", 25, "bold"))
    passwordLabel.place(x=100, y=540)

    passwordEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    passwordEntry.place(x=300, y=540)

    passwordLabel = Label(registerFrame, text="Confirm Pw: ", font= ("Verdana", 25, "bold"))
    passwordLabel.place(x=100, y=610)

    passwordEntry = Entry(registerFrame, font= ("Verdana", 25),width=300)
    passwordEntry.place(x=300, y=610)

    loginButton = Button(registerFrame, text="Register", font= ("Verdana", 30, "bold"),text_color="white",width=200,height=50)
    loginButton.place(x=250,y=680)

    switchRegisterButton = Button(registerFrame, text="Already a user? Login now", command=loginWindow, fg_color="#474747",hover_color="#474747", font= ("Verdana", 20, "bold","underline"),text_color="#47b0d6")
    switchRegisterButton.place(x=350,y=760, anchor=CENTER)

loginWindow()

root.mainloop()
