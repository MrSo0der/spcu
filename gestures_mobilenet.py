import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("gesture_model.keras")

gesture_dict = {
    0: "closedFist",
    1: "fingerCircle",
    2: "fingerSymbols",
    3: "multiFingerBend",
    4: "openPalm",
    5: "semiOpenFist",
    6: "semiOpenPalm",
    7: "singleFingerBend"
}

def process_image(image):
    # Предобработка для MobileNet
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 160))
    img = img / 127.5  # нормализация
    img = np.expand_dims(img, axis=0)

    # Предсказание жеста
    preds = model.predict(img, verbose=0)
    class_id = np.argmax(preds[0])
    return gesture_dict.get(class_id, "UNKNOWN")
