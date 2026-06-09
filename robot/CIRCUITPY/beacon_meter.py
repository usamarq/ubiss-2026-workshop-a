# beacon_meter.py - measure the strobe's real blink rate with the robot.
# HOW TO USE (tethered):
#   1. Open this file in Thonny (board as interpreter) and press Run.
#   2. When it says GO, hold the blinking phone ~30-50 cm in front of the
#      robot, aimed at the light sensors, and keep it steady for ~6 s.
#   3. Read the result: blink frequency (Hz) and duty (% of cycle ON).
# Tell those numbers to set BEACON_HZ in code.py.
# No motors involved - the robot stays still.

import time
import board
import analogio

SAMPLE_SECONDS = 6.0
SMOOTH_MS = 8          # per-sample averaging (kills 100 Hz mains flicker)

sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

print("Beacon meter: point the BLINKING phone at the sensors...")
for i in (3, 2, 1):
    print("  starting in", i)
    time.sleep(1)
print("GO - hold steady for", SAMPLE_SECONDS, "s")

# ---- collect smoothed samples for both sensors ----
ts, ls, rs = [], [], []
t_end = time.monotonic() + SAMPLE_SECONDS
while time.monotonic() < t_end:
    sl = sr = n = 0
    t_smooth = time.monotonic() + SMOOTH_MS / 1000
    while time.monotonic() < t_smooth:
        sl += sensorL.value
        sr += sensorR.value
        n += 1
    ts.append(time.monotonic())
    ls.append(sl // n)
    rs.append(sr // n)

print("collected", len(ts), "samples")

# ---- pick the sensor that saw the stronger blink ----
def peak_to_peak(v):
    return max(v) - min(v)

vals = ls if peak_to_peak(ls) >= peak_to_peak(rs) else rs
name = "L" if vals is ls else "R"
pp = peak_to_peak(vals)
print("using sensor", name, "| wobble (max-min):", pp)

if pp < 1000:
    print("RESULT: no clear blink seen (wobble too small).")
    print("Is the strobe on and aimed at the sensors?")
else:
    # ---- count threshold crossings with hysteresis ----
    lo = min(vals) + pp * 0.35
    hi = min(vals) + pp * 0.65
    state = vals[0] > hi
    rises = []           # times of OFF->ON transitions
    time_on = 0.0
    for i in range(1, len(vals)):
        if state and vals[i] < lo:
            state = False
        elif not state and vals[i] > hi:
            state = True
            rises.append(ts[i])
        if state:
            time_on += ts[i] - ts[i - 1]

    if len(rises) < 2:
        print("RESULT: light seen but fewer than 2 blinks in",
              SAMPLE_SECONDS, "s -> blink is VERY slow (or steady).")
    else:
        span = rises[-1] - rises[0]
        cycles = len(rises) - 1
        hz = cycles / span
        duty = 100 * time_on / (ts[-1] - ts[0])
        print("RESULT: blink frequency = %.2f Hz" % hz)
        print("        period = %.0f ms, duty = %.0f%% ON" % (1000 / hz, duty))
        print("        -> set BEACON_HZ = %.1f in code.py" % hz)
        print("        -> homing look window would be %.2f s" % (1.2 / hz))
