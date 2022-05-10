from utime import sleep, time
from machine import Pin

BLINK_TIME = 10
BLINK_INTERVAL = 0.5
SLEEP_TIME = 50

def blink():
    # Blink LED pin for BLINK_TIME secs
    led = Pin(2, Pin.OUT)
    start = time()
    while time() < start + BLINK_TIME:
        led.value(not led.value())
        sleep(BLINK_INTERVAL)
    led.value(True)

def main():
    blink()
    return SLEEP_TIME
