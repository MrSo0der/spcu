import cv2
import mediapipe as mp
import numpy as np
import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lcd = CharLCD('PCF8574', 0x27)   # если не работает — поменяй на 0x3F

def cosine(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def is_finger_folded(pts, tip, mid):
    return np.linalg.norm(pts[tip] - pts[0]) < np.linalg.norm(pts[mid] - pts[0])

def recognize_gesture(landmarks):
    pts = np.array([(lm.x, lm.y) for lm in landmarks])

    thumb_folded = cosine(pts[1] - pts[0], pts[4] - pts[3]) < 0
    index_folded = is_finger_folded(pts, 8, 6)
    middle_folded = is_finger_folded(pts, 12, 10)
    ring_folded = is_finger_folded(pts, 16, 14)
    pinky_folded = is_finger_folded(pts, 20, 18)

    fingers = [index_folded, middle_folded, ring_folded, pinky_folded]

    if all(fingers):
        v1, v2 = pts[4] - pts[0], np.array([0, -1])
        c = cosine(v1, v2)
        if thumb_folded:
            return "FIST"
        if .95 < c <= 1:
            return "THUMBS UP"
        if -1 <= c < -.95:
            return "THUMBS DOWN"

    if not any(fingers):
        return "PALM"

    if np.linalg.norm(pts[8] - pts[4]) < 0.04 and not any(fingers[1:]):
        return "OK"

    if pinky_folded and ring_folded and not middle_folded and not index_folded and thumb_folded:
        return "V SIGN"

    v1, v2 = pts[4] - pts[3], pts[20] - pts[19]
    if abs(cosine(v1, v2)) < 0.3 and all(fingers[:-1]) and not pinky_folded:
        return "CALL"

    return "UNKNOWN"

lcd.clear()
lcd.write_string("Gesture Ready")

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            lcd.clear()
            lcd.write_string("Processing...")
            time.sleep(0.3)

            gesture = "NO HAND"

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                gesture = recognize_gesture(hand.landmark)

            lcd.clear()
            lcd.write_string(gesture[:16])

            time.sleep(0.5)

        cv2.imshow("Raspberry Gesture", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
