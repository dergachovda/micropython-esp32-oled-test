# micropython-esp32-oled-test

Тестовий проєкт MicroPython для ESP32-C3 SuperMini з вбудованим OLED-дисплеєм 0.42" (контролер SH1106). Кнопка BOOT перемикає синій LED на платі, а на екрані відображаються привітання, стан LED і температура чіпа.

## Апаратна частина

- ESP32-C3 SuperMini (4 МБ флешу, USB-C)
- Вбудований OLED 0.42" на контролері SH1106, I2C-адреса `0x3C`
- Синій LED на GPIO8 (горить при LOW)
- Кнопка BOOT на GPIO9 (натиснута = LOW)

| Функція     | GPIO |
|-------------|------|
| I2C SDA     | 5    |
| I2C SCL     | 6    |
| LED         | 8    |
| Кнопка BOOT | 9    |

Видима область дисплея 72×40 пікселів у буфері 128×64 починається з координат `(28, 11)`. Це параметри конкретної плати.

> **Увага:** 0.42" дисплеї бувають різні. Одні мають SSD1306 і зсув `(28, 24)`, інші SH1106 з іншим зсувом. Не замінюйте модуль на інший без перевірки. Спочатку запустіть тест розмітки (див. нижче).

## Програмне забезпечення

- MicroPython 1.29.0 для ESP32-C3 (`ESP32_GENERIC_C3`) з [micropython.org/download/ESP32_GENERIC_C3](https://micropython.org/download/ESP32_GENERIC_C3)
- Драйвер `sh1106.py` з [robert-hh/SH1106](https://github.com/robert-hh/SH1106) (у `micropython-lib` його немає)
- [Thonny](https://thonny.org/) або `mpremote` та `esptool` через [uv](https://docs.astral.sh/uv/)

## Структура репозиторію

```
.
├── main.py     # основний проєкт: LED, кнопка, текст і температура на екрані
├── test.py     # тест розмітки: рамка і текст для перевірки зсуву дисплея
├── sh1106.py   # драйвер SH1106 (копіюється на плату в /lib)
└── README.md
```

## Встановлення

### 1. Прошивка MicroPython

Затисніть BOOT, підключіть плату по USB-C, відпустіть BOOT, далі:

```bash
uv run esptool --chip esp32c3 erase-flash
uv run esptool --chip esp32c3 --baud 460800 write-flash 0x0 ESP32_GENERIC_C3-20260824-v1.29.0.bin
```

Після запису натисніть RST.

### 2. Драйвер SH1106

```bash
uv run mpremote connect COM3 mkdir :lib
uv run mpremote connect COM3 cp sh1106.py :lib/sh1106.py
```

Помилка `mkdir`, що папка вже існує, не є проблемою.

### 3. Заливка коду

```bash
uv run mpremote connect COM3 cp main.py :main.py
uv run mpremote connect COM3 reset
```

Або в Thonny: **Ctrl+S → MicroPython device → main.py**.

## Код `main.py`

```python
from machine import I2C, Pin
import esp32
import sh1106
import time

# --- Піни ESP32-C3 SuperMini з OLED 0.42" ---
SDA_PIN = 5
SCL_PIN = 6
LED_PIN = 8    # вбудований синій LED (на SuperMini горить при LOW)
BTN_PIN = 9    # кнопка BOOT (натиснута = LOW)

# Видима область 72x40 у буфері 128x64 (параметри саме цієї плати)
OX, OY = 28, 11
W, H = 72, 40

i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3C)

led = Pin(LED_PIN, Pin.OUT)
btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

led_on = False
last_temp_update = 0


def set_led(state):
    # інвертовано: LOW = світиться
    led.value(0 if state else 1)


def text(s, x, y):
    oled.text(s, OX + x, OY + y, 1)


def draw(temp=None):
    oled.fill(0)
    text("Hi!", 4, 4)
    text("LED:" + ("ON" if led_on else "OFF"), 4, 16)
    if temp is not None:
        text("T:{:.1f}C".format(temp), 4, 28)
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
```

## Перевірка розмітки дисплея

Запустіть `test.py`, щоб побачити рамку 72×40 у видимій області та текст усередині:

```python
from machine import I2C, Pin
import sh1106

i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3C)

OX, OY = 28, 11
W, H = 72, 40

oled.fill(0)
oled.rect(OX, OY, W, H, 1)
oled.text("Hello", OX + 4, OY + 4, 1)
oled.show()
```

Рамка має лежати рівно по краях видимої області. Якщо ні, змініть `OX, OY` у `main.py`.

## Поведінка

- Після старту на екрані з'являються `Hi!`, `LED:OFF` і `T:xx.xC`.
- Натискання BOOT перемикає LED і оновлює рядок стану.
- Температура оновлюється раз на секунду.

Температура є значенням внутрішнього датчика чіпа `esp32.mcu_temperature()`. Вона показує нагрів кристала, а не температуру повітря, тому завищена і залежить від навантаження.

## Налагодження

- **`[60]` у `i2c.scan()`**: дисплей на шині, адреса `0x3C`.
- **Порт COM3 зайнятий**: закрийте Thonny (Stop) або інші програми, що використовують порт.
- **Екран шумить**: перевірте, що використовується драйвер SH1106, а не SSD1306.
- **Текст обрізаний**: змініть `OX, OY` за результатами `test.py`.
- **Thonny не бачить пристрій**: Run → Stop/Restart backend.
