import lgpio
import time

I2C_BUS = 1
I2C_ADDR = 0x3f

chip = lgpio.gpiochip_open(0)
i2c = lgpio.i2c_open(chip, I2C_BUS, I2C_ADDR, 0)

def lcd_toggle(bits):
    lgpio.i2c_write_byte(i2c, bits | 0x04)  # Enable
    time.sleep(0.001)
    lgpio.i2c_write_byte(i2c, bits & ~0x04)
    time.sleep(0.001)

def lcd_byte(bits, mode):
    high = mode | (bits & 0xF0)
    low = mode | ((bits << 4) & 0xF0)
    lgpio.i2c_write_byte(i2c, high)
    lcd_toggle(high)
    lgpio.i2c_write_byte(i2c, low)
    lcd_toggle(low)

def lcd_cmd(cmd):
    lcd_byte(cmd, 0)

def lcd_write_char(char):
    lcd_byte(ord(char), 1)

def lcd_init():
    lcd_cmd(0x33)
    lcd_cmd(0x32)
    lcd_cmd(0x28)
    lcd_cmd(0x0C)
    lcd_cmd(0x06)
    lcd_cmd(0x01)
    time.sleep(0.005)

def lcd_print(text, line=0):
    addr = 0x80 if line == 0 else 0xC0
    lcd_cmd(addr)
    for c in text.ljust(16):
        lcd_write_char(c)

lcd_init()
lcd_print("Hello LCD", 0)
lcd_print("Line 2", 1)
