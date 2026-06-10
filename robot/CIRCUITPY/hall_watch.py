# hall_watch.py - open in Thonny and press Run (or exec via tools/serial_exec.py).
# Watches GP10 AND GP27 (the two candidate hall pins: hall_test.py says the
# sensor is on the GP10 connector, code.py/HANDOVER said GP27) and prints
# every transition. One magnet session answers: which pin, which level means
# "magnet present", which pole works, and whether the signal is clean.
# Bring the magnet to the sensor's flat face; try BOTH poles, vary distance.
import board
import digitalio
import time

try:
    DURATION
except NameError:
    DURATION = 60

pins = {}
for name in ("GP10", "GP27"):
    p = digitalio.DigitalInOut(getattr(board, name))
    p.direction = digitalio.Direction.INPUT
    p.pull = digitalio.Pull.UP
    pins[name] = p

print("HALLWATCH start, %ds. idle levels:" % DURATION,
      " ".join("%s=%d" % (n, p.value) for n, p in sorted(pins.items())))
last = {n: p.value for n, p in pins.items()}
count = {n: 0 for n in pins}
t0 = time.monotonic()
while time.monotonic() - t0 < DURATION:
    for n, p in pins.items():
        v = p.value
        if v != last[n]:
            count[n] += 1
            print("t=%6.2f  %s -> %d" % (time.monotonic() - t0, n, v))
            last[n] = v
    time.sleep(0.005)

print("HALLWATCH end:",
      " ".join("%s: now=%d transitions=%d" % (n, pins[n].value, count[n])
               for n in sorted(pins)))
for p in pins.values():
    p.deinit()
