import cv2
from deepface import DeepFace
import os
import time

# Paths for the stored images
image1_path = 'WIN_20240910_10_37_16_Pro.jpg'
captured_image_path = 'captured_image.jpg'

# Load the first image for verification (the reference image)
image1 = cv2.imread(image1_path)

# Convert the reference image to grayscale
gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

# Load a pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Detect face in the reference image
faces1 = face_cascade.detectMultiScale(gray_image1, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

# Ensure that at least one face is detected in the reference image
if len(faces1) == 0:
    print("No face detected in the reference image.")
    exit()

# Crop the face from the reference image
(x1, y1, w1, h1) = faces1[0]
face_image1 = image1[y1:y1 + h1, x1:x1 + w1]

# Open a connection to the webcam (0 is the default webcam)
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Error: Could not access the webcam.")
    exit()

while True:
    # Capture a frame from the webcam
    ret, frame = cam.read()

    if not ret:
        print("Failed to grab frame from webcam.")
        break

    # Save the captured frame as an image
    cv2.imwrite(captured_image_path, frame)

    # Convert the captured image to grayscale
    gray_image2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the captured image
    faces2 = face_cascade.detectMultiScale(gray_image2, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Ensure a face is detected in the captured image
    if len(faces2) == 0:
        print("No face detected in the captured image.")
        os.remove(captured_image_path)  # Delete the image if no face is detected
        time.sleep(0.5)  # Wait for 0.5 seconds before trying again
        continue

    # Crop the face from the captured image
    (x2, y2, w2, h2) = faces2[0]
    face_image2 = frame[y2:y2 + h2, x2:x2 + w2]

    # Use DeepFace to verify if the faces belong to the same person
    result = DeepFace.verify(face_image1, face_image2, enforce_detection=False)

    # Check if the faces are the same
    if result['verified']:
        print("Verification Success: Both images are of the same person.")
        os.remove(captured_image_path)  # Delete the captured image
        break  # Exit the loop after success
    else:
        print("Verification Failed: The images are of different people.")
        os.remove(captured_image_path)  # Delete the captured image
        time.sleep(0.5)  # Wait for 0.5 seconds before capturing a new image and trying again

# Release the webcam and close all OpenCV windows
cam.release()
cv2.destroyAllWindows()
    