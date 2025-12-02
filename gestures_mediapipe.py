import mediapipe as mp
import numpy as np


def cosine(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0
    return np.dot(v1, v2) / (n1 * n2)

def is_finger_folded(pts, tip, mid):
    return np.linalg.norm(pts[tip] - pts[0]) < np.linalg.norm(pts[mid] - pts[0])

def recognize_gesture(landmarks):
    pts = np.array([(lm.x, lm.y) for lm in landmarks])

    thumb_f = cosine(pts[1] - pts[0], pts[4] - pts[3]) < 0

    folded = [
        is_finger_folded(pts, 8, 6),   # index
        is_finger_folded(pts, 12, 10), # middle
        is_finger_folded(pts, 16, 14), # ring
        is_finger_folded(pts, 20, 18)  # pinky
    ]

    index_f, middle_f, ring_f, pinky_f = folded

    if all(folded):
        v1 = pts[4] - pts[0]
        c = cosine(v1, np.array([0, -1]))

        if thumb_f:
            return "FIST"
        if c > 0.95:
            return "THUMBS UP"
        if c < -0.95:
            return "THUMBS DOWN"

    # Palm
    if not any(folded):
        return "PALM"

    # OK
    if np.linalg.norm(pts[8] - pts[4]) < 0.04 and not any(folded[1:]):
        return "OK"

    # V-Sign
    if pinky_f and ring_f and not middle_f and not index_f and thumb_f:
        return "V SIGN"

    # Call
    v1 = pts[4] - pts[3]
    v2 = pts[20] - pts[19]
    if abs(cosine(v1, v2)) < 0.3 and all(folded[:-1]) and not pinky_f:
        return "CALL"

    return "UNKNOWN"

def process_image(image):
    with mp.solutions.hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:
        results = hands.process(image)
        gesture = "NO HAND"
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            gesture = recognize_gesture(hand.landmark)
    
    return gesture
