from machine import Pin, SoftI2C
import esp32
import sh1106
import time

# --- Піни ESP32-C3 SuperMini з OLED 0.42" ---
SDA_PIN = 5
SCL_PIN = 6
LED_PIN = 8    # вбудований синій LED (на SuperMini горить при LOW)
BTN_PIN = 9    # кнопка BOOT (натиснута = LOW)

# Видима область екрана 72x40 у буфері 128x64
OX, OY = 13, 14

i2c = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c)

led = Pin(LED_PIN, Pin.OUT)
btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

led_on = False
last_temp_update = 0


def set_led(state):
    # інвертовано: LOW = світиться
    led.value(0 if state else 1)


def draw(temp=None):
    oled.fill(0)
    oled.text("Hi!", OX + 2, OY + 4)
    oled.text("LED:" + ("ON" if led_on else "OFF"), OX + 2, OY + 16)
    if temp is not None:
        oled.text("T:{:.1f}C".format(temp), OX + 2, OY + 28)
    oled.show()


set_led(led_on)
draw()

last = btn.value()
while True:
    cur = btn.value()
    if last == 1 and cur == 0:      # натиснули BOOT
        led_on = not led_on
        set_led(led_on)
        draw(esp32.mcu_temperature())
        time.sleep_ms(200)          # антидребезг
    last = cur

    now = time.ticks_ms()
    if time.ticks_diff(now, last_temp_update) >= 1000:
        last_temp_update = now
        draw(esp32.mcu_temperature())

    time.sleep_ms(10)