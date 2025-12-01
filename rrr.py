import time
import cv2
import lgpio
from smbus2 import SMBus

# -------------------------
# Настройки
# -------------------------
BUTTON_GPIO = 24          # GPIO номер, НЕ физический пин
GPIO_CHIP = 0             # /dev/gpiochip0
I2C_ADDR = 0x3f           # Адрес вашего LCD1602
I2C_BUS = 1               # Обычно 1 на Raspberry Pi

# -------------------------
# LCD1602 I2C Функции
# -------------------------
LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100

bus = SMBus(I2C_BUS)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_byte(bits, mode):
    high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    low  = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(I2C_ADDR, high)
    lcd_toggle_enable(high)
    bus.write_byte(I2C_ADDR, low)
    lcd_toggle_enable(low)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def lcd_print(line, text):
    lcd_byte(line, LCD_CMD)
    for char in text.ljust(16):
        lcd_byte(ord(char), LCD_CHR)

# -------------------------
# Инициализация LCD
# -------------------------
lcd_init()
lcd_print(LCD_LINE_1, "Gesture Ready")

# -------------------------
# Инициализация GPIO с lgpio
# -------------------------
chip = lgpio.gpiochip_open(GPIO_CHIP)
lgpio.gpio_claim_input(chip, BUTTON_GPIO)

# -------------------------
# Инициализация камеры
# -------------------------
cam = cv2.VideoCapture(0)

def recognize_gesture(image):
    """Здесь вставь свою модель."""
    return "YourGesture"

# -------------------------
# Основной цикл
# -------------------------
print("Ожидание нажатия кнопки...")

while True:
    val = lgpio.gpio_read(chip, BUTTON_GPIO)

    if val == 0:
        print("Кнопка нажата!")

        # ---- Снимок ----
        ret, frame = cam.read()
        if not ret:
            print("Ошибка камеры")
            continue

        cv2.imwrite("frame.jpg", frame)
        print("Снимок сохранён frame.jpg")

        # ---- Распознавание ----
        gesture = recognize_gesture(frame)
        print("Распознан жест:", gesture)

        # ---- Вывод на LCD ----
        lcd_print(LCD_LINE_1, "Gesture:")
        lcd_print(LCD_LINE_2, gesture[:16])

        # Антидребезг
        time.sleep(0.5)

    time.sleep(0.05)
