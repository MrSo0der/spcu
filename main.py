import argparse
import cv2
import lgpio
from LCD import LCD

def main():
    parser = argparse.ArgumentParser(description="Script for gesture recognition from a camera")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-mdp', action='store_true', help="For mediapipe usage")
    group.add_argument('-mbn', action='store_true', help="For MobileNetV2 usage")
    
    args = parser.parse_args()
    
    if args.mdp:
        from gestures_mediapipe import process_image
    elif args.mbn:
        from gestures_mobilenet import process_image

    # GPIO
    BUTTON_GPIO = 24
    GPIO_CHIP = 0

    chip = lgpio.gpiochip_open(GPIO_CHIP)
    lgpio.gpio_claim_input(chip, BUTTON_GPIO)

    # Main Program
    lcd = LCD()
    lcd.clear()
    lcd.message("Gesture Ready", 1)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if lgpio.gpio_read(chip, BUTTON_GPIO) or not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        lcd.clear()
        lcd.message("Processing...", 1)
        gesture = process_image(rgb)

        lcd.clear()
        lcd.message(gesture[:16], 1)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
