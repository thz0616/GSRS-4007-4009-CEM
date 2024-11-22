import customtkinter
from customtkinter import *
from PIL import Image, ImageTk
import cv2
import os
import sqlite3  # To work with the SQLite database
from tkinter import filedialog
from deepface import DeepFace  # Import DeepFace for face comparison

Button = customtkinter.CTkButton
Frame = customtkinter.CTkFrame
Entry = customtkinter.CTkEntry
Label = customtkinter.CTkLabel
Scrollbar = customtkinter.CTkScrollbar
Textbox = customtkinter.CTkTextbox

captured_image_path = "captured_sample_image.jpg"
id_card_image_path = ""

# Connect to the tenants.db database
conn = sqlite3.connect('tenants.db')
cursor = conn.cursor()

# Function to update the database with image paths
def update_database(faceImagePath, ICImagepath):
    try:
        # Assuming there's a column for 'faceImagePath' and 'ICImagepath' in the 'tenants' table
        cursor.execute("""
            INSERT INTO tenants (faceImagePath, ICImagepath) 
            VALUES (?, ?)
        """, (faceImagePath, ICImagepath))
        conn.commit()  # Save the changes
    except sqlite3.Error as e:
        print(f"Error updating database: {e}")

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to detect faces using the Haar cascade
def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale for detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    return faces

# Function to capture the image
def capture_image():
    global frame, captured_image_path
    # Save the current frame as a temporary image
    cv2.imwrite(captured_image_path, frame)
    # Transition to the preview window within the main root window
    show_image_confirmation()

# Function to display the confirmation within the same window
def show_image_confirmation():
    # Hide the selfie components (webcam feed)
    cameraFrame.place_forget()
    instructionFrame.place_forget()
    titleFrame.place_forget()
    statusFrame.place_forget()

    # Create a new frame for image confirmation
    confirm_frame = Frame(root, width=1920, height=1050)
    confirm_frame.place(x=0, y=30)

    # Load and display the captured image
    img = Image.open(captured_image_path)
    img = img.resize((300, 225), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    img_label = Label(confirm_frame, text="", image=img_tk)
    img_label.image = img_tk  # Keep reference to avoid garbage collection
    img_label.place(relx=0.5, rely=0.4, anchor=CENTER)

    # Save and Discard buttons
    saveButton = Button(confirm_frame, text="Save", command=lambda: save_image(confirm_frame))
    discardButton = Button(confirm_frame, text="Discard", command=lambda: discard_image(confirm_frame))

    saveButton.place(relx=0.4, rely=0.7, anchor=CENTER)
    discardButton.place(relx=0.6, rely=0.7, anchor=CENTER)

# Function to save the image and move to ID card upload page
def save_image(confirm_frame):
    # Close the image confirmation frame
    confirm_frame.place_forget()
    # Update status label to indicate the image was saved
    statusLabel.configure(text=f"Image saved at {captured_image_path}")
    statusLabel.update_idletasks()  # Ensure immediate UI update
    # Open the ID card upload window after saving the image
    show_id_card_upload()

# Function to discard the image and go back to the selfie page
def discard_image(confirm_frame):
    global captured_image_path
    # Close the image confirmation frame
    confirm_frame.place_forget()
    # Delete the temporarily saved image
    if os.path.exists(captured_image_path):
        os.remove(captured_image_path)
    # Update status label to indicate the image was discarded
    statusLabel.configure(text="Image discarded.")
    statusLabel.update_idletasks()  # Ensure immediate UI update
    # Return to the selfie capture page
    show_selfie_page()

# Function to display ID card upload page
def show_id_card_upload():
    global idStatusLabel
    # Destroy the current frame components (selfie page)
    cameraFrame.place_forget()
    titleFrame.place_forget()
    instructionFrame.place_forget()
    statusLabel.place_forget()

    # Show ID card upload frame
    upload_frame = Frame(root, width=1920, height=1050)
    upload_frame.place(x=0, y=30)

    # show the frame of status
    idStatusFrame = Frame(root, width=1000, height=50)
    idStatusFrame.place(x=960, y=1000, anchor=CENTER)

    instruction_label = Label(upload_frame, text="Please upload your ID card", font=("Arial", 40, "bold"))
    instruction_label.place(x=960, y=200, anchor=CENTER)

    upload_button = Button(upload_frame, text="Upload ID Card", font=("Arial", 20), command=lambda: upload_id_card(upload_frame))
    upload_button.place(x=960, y=300, anchor=CENTER)

    idStatusLabel = Label(idStatusFrame, text="Please upload the picture of I/C", font=('Arial', 15))
    idStatusLabel.place(x=500, y=30, anchor=CENTER)

# Function to allow the user to upload their ID card
def upload_id_card(frame):
    global id_card_image_path

    # Ask the user to select an image file
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])

    if file_path:
        id_card_image_path = file_path
        # Load and display the uploaded ID card image
        img = Image.open(id_card_image_path)
        img = img.resize((500, 315), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        # Create a new label to display the image
        img_label = Label(frame, text="", image=img_tk)
        img_label.image = img_tk  # Keep reference to avoid garbage collection
        img_label.place(x=960, y=500, anchor=CENTER)

        # Update status label to indicate the ID card was uploaded
        idStatusLabel.configure(text=f"ID card uploaded: {id_card_image_path}")
        idStatusLabel.update_idletasks()  # Ensure immediate UI update

        # After uploading, compare the images
        compare_faces()

# Function to compare the face in the selfie with the ID card image using DeepFace
def compare_faces():
    # Use DeepFace to verify if the faces match
    try:
        # Specify the model and distance metric
        model_name = "VGG-Face"  # You can use other models like "Facenet", "OpenFace", etc.
        distance_metric = "cosine"  # Options: 'cosine', 'euclidean', 'euclidean_l2'
        custom_threshold = 0.60  # Adjust this value according to your needs

        # Use DeepFace to verify if the faces match
        result = DeepFace.verify(
            img1_path=captured_image_path,
            img2_path=id_card_image_path,
            model_name=model_name,
            distance_metric=distance_metric,
            enforce_detection=False,  # Set to False if you don't want errors when no face is detected
            threshold=custom_threshold  # Custom threshold value
        )

        if result["verified"]:
            # Update the database with the paths of the selfie and ID card images
            update_database(captured_image_path, id_card_image_path)
            idStatusLabel.configure(text="Face match successful! Data saved to database.")
        else:
            idStatusLabel.configure(text="Face match failed! Please try again.")
    except Exception as e:
        idStatusLabel.configure(text=f"Error in face comparison: {e}")

# Function to continuously display the webcam feed
def update_frame():
    global frame
    ret, frame = video_capture.read()

    if ret:
        # Convert the frame to RGB (for PIL to handle it properly)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        # Detect faces in the current frame
        faces = detect_faces(frame)

        # If faces are detected, enable the capture button, otherwise disable it
        if len(faces) > 0:
            captureButton.configure(state=NORMAL)
            statusLabel.configure(text="Face detected. Ready to capture.")
            statusLabel.update_idletasks()  # Ensure immediate UI update
        else:
            captureButton.configure(state=DISABLED)
            statusLabel.configure(text="No face detected. Please position your face properly.")
            statusLabel.update_idletasks()  # Ensure immediate UI update

        cameraLabel.imgtk = imgtk  # Keep reference to avoid garbage collection
        cameraLabel.configure(image=imgtk)
        cameraLabel.after(10, update_frame)

# Initialize the main window
root = customtkinter.CTk()
root.geometry("1920x1080")

# Create the title frame for the app
titleFrame = Frame(root, width=1920, height=200)
titleFrame.place(x=960, y=20, anchor=CENTER)

titleLabel = Label(titleFrame, text="Welcome to the Image Registration System", font=('Arial', 40, "bold"))
titleLabel.place(x=500, y=30, anchor=CENTER)

# Create the frame for the webcam feed
cameraFrame = Frame(root, width=640, height=480)
cameraFrame.place(x=960, y=500, anchor=CENTER)

# Add a label to display the webcam feed
cameraLabel = Label(cameraFrame)
cameraLabel.place(x=320, y=240, anchor=CENTER)

# Create a button for capturing the image
captureButton = Button(root, text="Capture", font=('Arial', 20), state=DISABLED, command=capture_image)
captureButton.place(x=960, y=900, anchor=CENTER)

# Create a frame for the instructions
instructionFrame = Frame(root, width=640, height=100)
instructionFrame.place(x=960, y=850, anchor=CENTER)

instructionLabel = Label(instructionFrame, text="Please position your face in front of the camera", font=('Arial', 15))
instructionLabel.place(x=500, y=30, anchor=CENTER)

# Create a frame for the status label
statusFrame = Frame(root, width=1000, height=50)
statusFrame.place(x=960, y=1000, anchor=CENTER)

statusLabel = Label(statusFrame, text="Initializing...", font=('Arial', 15))
statusLabel.place(x=500, y=30, anchor=CENTER)

# Open the webcam
video_capture = cv2.VideoCapture(0)

# Start the webcam feed update loop
update_frame()

root.mainloop()

# Close the database connection when the program ends
conn.close()
