import cv2
import os
import time
from deepface import DeepFace
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

# Paths
reference_image_path = 'WIN_20240910_10_37_16_Pro.jpg'  # Reference image path
captured_image_path = r'C:\Users\tanho\PycharmProjects\all project 2\captured_image.jpg'  # Captured image path


# Load reference face (we'll crop and verify against it)
def detect_and_crop_face(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        print("No face detected in:", image_path)
        return None
    (x, y, w, h) = faces[0]
    return image[y:y + h, x:x + w]  # Cropped face


# Load the reference face at startup
reference_face = detect_and_crop_face(reference_image_path)


# Function to perform verification using DeepFace
def verify_face(live_face, threshold=0.33):
    try:
        result = DeepFace.verify(reference_face, live_face, enforce_detection=False)
        distance = result['distance']
        return distance < threshold  # Return True if faces are the same person
    except Exception as e:
        print("Verification error:", e)
        return False


# Main App using CustomTkinter
class FaceVerificationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Real-Time Face Verification")
        self.geometry("800x600")

        # Webcam feed on the GUI
        self.webcam_label = ctk.CTkLabel(self)
        self.webcam_label.pack(pady=20)

        # Verification result label
        self.result_label = ctk.CTkLabel(self, text="Verification Status", font=("Arial", 20))
        self.result_label.pack(pady=20)

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)

        # Start updating the GUI with webcam feed and verification result
        self.update_webcam()

    def update_webcam(self):
        ret, frame = self.cap.read()  # Read the current frame from webcam
        if ret:
            face_image = self.detect_face(frame)  # Detect face in the current frame

            if face_image is not None:
                verified = verify_face(face_image)  # Perform verification

                # Update result label based on verification
                if verified:
                    self.result_label.configure(text="Verification Success", fg_color="green")
                    self.show_success_message()  # Show messagebox on verification success
                else:
                    self.result_label.configure(text="Verification Failed", fg_color="red")
            else:
                self.result_label.configure(text="No Face Detected", fg_color="orange")

            # Convert frame to ImageTk for displaying on GUI
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)

            # Update the webcam label with the new image
            self.webcam_label.imgtk = img_tk
            self.webcam_label.configure(image=img_tk)

        # Call the update function again after 10ms (for real-time update)
        self.after(10, self.update_webcam)

    def detect_face(self, frame):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]  # Use the first detected face
            return frame[y:y + h, x:x + w]  # Return the cropped face
        return None

    def show_success_message(self):
        # Show a messagebox when verification is successful
        messagebox.showinfo("Verification Passed", "Face verification passed successfully!")

        # Close the GUI and release the camera after showing the message
        self.cap.release()
        self.destroy()

    def on_closing(self):
        self.cap.release()  # Release webcam when closing
        self.destroy()


# Create the app and run the main loop
if __name__ == "__main__":
    app = FaceVerificationApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # Ensure the webcam is released on exit
    app.mainloop()
