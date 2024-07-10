# Importing OpenCV Library for basic image processing functions
import cv2
# Numpy for array-related functions
import numpy as np
# Dlib for deep learning based Modules and face landmark detection
import dlib
from pygame import mixer
# face_utils for basic operations of conversion
from imutils import face_utils

mixer.init()
mixer.music.load("music.wav")

# Initializing the camera and taking the instance
cap = cv2.VideoCapture(0)

# Initializing the face detector and landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Status marking for the current state
sleep = 0
drowsy = 0
active = 0
yawn_count = 0  # Initialize the yawn count
status = ""
color = (0, 0, 0)

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Checking if it is blinked
    if ratio > 0.25:
        return 2
    elif 0.10 < ratio <= 0.25:
        return 1
    else:
        return 0

while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    # Initialize face_frame before the loop
    face_frame = frame.copy()

    # Detected face in faces array
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # The numbers are actually the landmarks that will show the eye
        left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        leftEye = landmarks[36:42]
        rightEye = landmarks[42:48]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0

        if ear < 0.20:  # Adjust this threshold based on your observations
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "You Are Sleeping Take Rest !!!"
                color = (0, 0, 255)
                mixer.music.play()
                yawn_count += 1  # Increment yawn count when a yawn is detected

        elif 0.10 < left_blink <= 0.25 or 0.10 < right_blink <= 0.25:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = "Drowsy! There Is More To Achieve.."
                color = (255, 0, 0)

        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "You Are Active:)Keep Going"
                color = (0, 255, 0)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    cv2.putText(frame, f"Yawn Count: {yawn_count}", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Result of detector", face_frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Print the yawn count at the end
print("Yawn Count at the end:",yawn_count)
