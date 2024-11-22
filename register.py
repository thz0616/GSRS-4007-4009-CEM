
import customtkinter
from customtkinter import *
from login tenant import loginWindow

Button = customtkinter.CTkButton
Frame = customtkinter.CTkFrame
Entry = customtkinter.CTkEntry
Label = customtkinter.CTkLabel

root=CTk()
root.geometry('1920x1080')
root.attributes("-fullscreen", True)

def closeApp():
    root.destroy()

buttonFrame = Frame(root,fg_color="black",width=1920,height=30)
buttonFrame.place(x=0,y=0)

closeButton = Button(root, text="X", command=closeApp,fg_color="black",hover_color="red",text_color="white",width=50,height=30)
closeButton.place(x=1870,y=0)

def registerWindow():
    registerFrame = Frame(root, fg_color="#474747",width=700,height=800)
    registerFrame.place(x=610,y=140)

    registerLabel = Label(registerFrame,text="Register", font=('Cooper Black',60))
    registerLabel.place(x=350,y=100,anchor=CENTER)

    usernameLabel = Label(registerFrame, text="Username: ", font= ("Verdana", 30, "bold"))
    usernameLabel.place(x=100, y=200)

    usernameEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    usernameEntry.place(x=300, y=200)

    fullnameLabel = Label(registerFrame, text="Fullname: ", font= ("Verdana", 30, "bold"))
    fullnameLabel.place(x=100, y=280)

    fullnameEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    fullnameEntry.place(x=300, y=280)

    ICLabel = Label(registerFrame, text="I/C: ", font= ("Verdana", 30, "bold"))
    ICLabel.place(x=100, y=360)

    ICEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    ICEntry.place(x=300, y=360)

    phoneNumberLabel = Label(registerFrame, text="H/P: ", font= ("Verdana", 30, "bold"))
    phoneNumberLabel.place(x=100, y=440)

    phoneNumberEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    phoneNumberEntry.place(x=300, y=440)

    passwordLabel = Label(registerFrame, text="Password: ", font= ("Verdana", 30, "bold"))
    passwordLabel.place(x=100, y=520)

    passwordEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    passwordEntry.place(x=300, y=520)

    passwordLabel = Label(registerFrame, text="Confirm Pw: ", font= ("Verdana", 28, "bold"))
    passwordLabel.place(x=100, y=600)

    passwordEntry = Entry(registerFrame, font= ("Verdana", 30),width=300)
    passwordEntry.place(x=300, y=600)

    loginButton = Button(registerFrame, text="Register", font= ("Verdana", 30, "bold"),text_color="white",width=200,height=50)
    loginButton.place(x=250,y=680)

    switchRegisterButton = Button(registerFrame, text="Already a user? Login now", command=loginWindow, fg_color="#474747",hover_color="#474747", font= ("Verdana", 20, "bold","underline"),text_color="#47b0d6")
    switchRegisterButton.place(x=350,y=760, anchor=CENTER)


root.mainloop()