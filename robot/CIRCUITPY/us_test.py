# us_test.py - quick HC-SR04 wiring test
# Run in Thonny (F5) or copy as code.py to auto-run.
# Prints distance every 0.5 s. Point at a wall/object and check the numbers.
# Expected: 3-200 cm range. "-1" = no echo (check wiring).

import time
import board
import digitalio

trig = digitalio.DigitalInOut(board.GP12)
trig.direction = digitalio.Direction.OUTPUT
trig.value = False

echo = digitalio.DigitalInOut(board.GP13)
echo.direction = digitalio.Direction.INPUT


def ping_cm():
    trig.value = False
    time.sleep(0.000005)
    trig.value = True
    time.sleep(0.00001)
    trig.value = False

    deadline = time.monotonic() + 0.04
    while not echo.value:
        if time.monotonic() > deadline:
            return -1.0
    t0 = time.monotonic()
    while echo.value:
        if time.monotonic() > deadline:
            return -1.0
    return (time.monotonic() - t0) * 17150.0


print("HC-SR04 test on GP12 (Trig) + GP13 (Echo)")
print("Move your hand in front of the sensor...")
print()

while True:
    d = ping_cm()
    if d > 0:
        print("distance: %.1f cm" % d)
    else:
        print("distance: NO ECHO (-1)")
    time.sleep(0.5)
