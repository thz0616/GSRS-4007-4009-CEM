import cv2
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from deepface import DeepFace
import time


# Function to detect faces in an image
def detect_face(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    # Crop the first detected face
    (x, y, w, h) = faces[0]
    face_image = image[y:y + h, x:x + w]

    return face_image


# Load image 2 (from the stored path)
image2_path = 'WIN_20240829_13_36_59_Pro.jpg'
image2 = cv2.imread(image2_path)

# Check if the image was loaded properly
if image2 is None:
    print("Error: Could not load the second image from the database.")
    exit()

# Detect the face in the stored image (image 2)
face_image2 = detect_face(image2)
if face_image2 is None:
    print("No face detected in the second image from the database.")
    exit()


# Main window class using customtkinter
class FaceVerificationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Verification App")
        self.geometry("800x600")

        # Create label to display webcam feed
        self.label = ctk.CTkLabel(self, text="")
        self.label.pack(padx=20, pady=20)

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)

        # Timestamp for rate-limiting verification (1 second)
        self.last_verification_time = time.time()

        # Start displaying the webcam feed
        self.update_webcam()

    # Function to display the webcam feed
    def update_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert the frame to a format that Tkinter can display
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

        # Detect face and verify if it matches with stored image2 (every 1 second)
        current_time = time.time()
        if current_time - self.last_verification_time >= 1:
            self.last_verification_time = current_time  # Update the last verification time
            self.verify_face(frame)

        # Update the webcam feed every 10 milliseconds
        self.after(10, self.update_webcam)

    # Function to verify if the captured face matches the stored face
    def verify_face(self, frame):
        face_image1 = detect_face(frame)

        if face_image1 is not None:
            print("Face detected, attempting to verify...")

            try:
                # Use a stricter model and set a custom, lower distance threshold for more accurate results
                result = DeepFace.verify(
                    face_image1,
                    face_image2,
                    model_name="ArcFace",  # Using a more accurate model
                    distance_metric="euclidean_l2",  # Stricter distance metric
                    enforce_detection=False
                )

                # Print distance value and threshold for debugging
                print(f"Distance: {result['distance']} | Threshold: {result['threshold']}")

                # Use a lower custom threshold to make the comparison stricter
                custom_threshold = 0.6  # Stricter threshold (reduce from default ~0.68)

                # The match is valid only if the distance is less than the custom threshold
                if result['verified'] and result['distance'] <= custom_threshold:
                    print("Match found: The captured face matches the stored image.")
                    self.cap.release()
                    messagebox.showinfo("Verification Successful", "Both images are of the same person!")
                    self.quit()
                else:
                    print("Face mismatch: The captured face does not match the stored image.")
                    print(f"Custom Threshold used: {custom_threshold} | Actual distance: {result['distance']}")

            except Exception as e:
                print(f"Error during face verification: {e}")
        else:
            print("No face detected in the current frame.")


# Initialize the customtkinter app and run it
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Optional: Change appearance mode
    app = FaceVerificationApp()
    app.mainloop()
