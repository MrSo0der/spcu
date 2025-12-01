import cv2
import mediapipe as mp
import numpy as np
import time
import lgpio
from LCD import LCD

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

BUTTON_GPIO = 24
GPIO_CHIP = 0

chip = lgpio.gpiochip_open(GPIO_CHIP)
lgpio.gpio_claim_input(chip, BUTTON_GPIO)


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
lcd = LCD()
lcd.clear()
lcd.message("Gesture Ready", 1)

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    while True:
        val = lgpio.gpio_read(chip, BUTTON_GPIO)
        cap.read()
        if val == 1:
            continue
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if 1:
            lcd.clear()
            lcd.message("Processing...",1)

            gesture = "NO HAND"

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                gesture = recognize_gesture(hand.landmark)

            lcd.clear()
            lcd.message(gesture[:16], 1)


        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
