import cv2
from deepface import DeepFace
import os

# Path to the reference image
reference_img_path = "WIN_20240829_13_36_59_Pro.jpg"

# Check if the reference image exists
if not os.path.exists(reference_img_path):
    print(f"Error: Reference image not found at {reference_img_path}")
    exit()

# Load the reference image
ref_img = cv2.imread(reference_img_path)
if ref_img is None:
    print("Error: Reference image could not be loaded.")
    exit()

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit the program.")

while True:
    # Capture a single frame from the webcam
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Error: Failed to capture image.")
        break

    # Convert the frame from BGR (OpenCV default) to RGB (required by DeepFace)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform face verification
    try:
        verification_result = DeepFace.verify(frame_rgb, reference_img_path)
    except Exception as e:
        print("Error during face verification:", str(e))
        break

    # Check if the faces match
    if verification_result['verified']:
        print("Access Granted")
        cv2.putText(frame, "Access Granted", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        print("Access Denied")
        cv2.putText(frame, "Access Denied", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Display the captured frame
    cv2.imshow('Face Recognition', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
