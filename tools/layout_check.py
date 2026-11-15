from machine import I2C, Pin
import sh1106

i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3C)

OX, OY = 28, 11   # visible window origin on this unit
W, H = 72, 40

def text(s, x, y, c=1):
    oled.text(s, OX + x, OY + y, c)

def clear():
    oled.fill(0)

oled.fill(0)
oled.rect(OX, OY, W, H, 1)
text("Hello", 4, 4)       # 9 chars max per line (72 / 8)
text("0.42", 4, 16)
text("SH1106", 4, 28)
oled.show()