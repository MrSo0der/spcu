# spcu

Данный набор скриптов разработан для распознавания жестов с камеры, подключенной к Raspberry Pi 5, и вывода названия жеста на экран LCD1602 по нажатию кнопки.

Модуль `LCD.py` взят из [данного репозитория](github.com/sterlingbeason/LCD-1602-I2C.git).

Для обучения MobileNetV2 был разработан [блокнот в Google Colab](https://colab.research.google.com/drive/1EI-H3IAU0FL_Vi79XL1-SvLszzMbDpq8?usp=sharing) на основе [статьи](https://blog.roboflow.com/how-to-train-mobilenetv2-on-a-custom-dataset/) и [датасета](https://www.kaggle.com/datasets/ritikagiridhar/2000-hand-gestures?resource=download).

## Требования

1. Python 3.11
2. Включенный i2c на Raspberry Pi 5

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Подключение переферии

LCD1602 (с переходником на i2c):
* VCC -> PIN2 (5V power)
* SDA -> PIN3 (GPIO 2 (SDA))
* SCL -> PIN5 (GPIO 3 (SCL))
* GND -> PIN9 (Ground)
Модуль кнопок:
* VCC -> PIN17 (3V3 power)
* GND -> PIN20 (Ground)
* 1   -> PIN18 (GPIO 24)
Камера:
* Любой свободный USB-порт

## Запуск

Для использования mediapipe для распознавания жестов:

```bash
python main.py -mdp
```

Для использования MobileNetV2 для распознавания жестов:

```bash
python main.py -mbn
```

## Использование

Поднесите руку к камере, нажмите на кнопку и на экране появится название распознанного жеста.