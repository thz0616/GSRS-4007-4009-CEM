import cv2
from deepface import DeepFace
import numpy as np
import traceback

# Load reference image
reference_img_path = r"C:\Users\tanho\PycharmProjects\all project 2\WIN_20240829_13_36_59_Pro.jpg"
reference_img = cv2.imread(reference_img_path)
if reference_img is None:
    raise ValueError("Reference image not found at the specified path.")
reference_img_rgb = cv2.cvtColor(reference_img, cv2.COLOR_BGR2RGB)


def check_face(frame):
    global face_match

    try:
        if frame is None or not isinstance(frame, np.ndarray):
            raise ValueError("Captured frame is not a valid image")
        if frame.shape[-1] != 3:
            raise ValueError(f"Frame shape invalid: {frame.shape}")
        if np.sum(frame) == 0:
            raise ValueError("Captured frame is empty or black")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            result = DeepFace.verify(frame_rgb, reference_img_rgb)
            print("Verification result:", result)
            face_match = result['verified']
        except Exception as e:
            print(f"Exception encountered during face verification: {e}")
            traceback.print_exc()  # Log detailed traceback
            face_match = False

    except Exception as e:
        print(f"Error in processing the frame: {e}")
        traceback.print_exc()  # Log detailed traceback
        face_match = False


# Initialize webcam
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False

while True:
    ret, frame = cap.read()

    if ret:
        if counter % 30 == 0:
            # Check face without threading
            check_face(frame.copy())

        counter += 1

        if face_match:
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow("video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
