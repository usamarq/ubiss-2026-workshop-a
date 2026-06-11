# mapping_code.py — Task 2: disk vs triangle
# "Lighthouse + Specularity Probe"
#
# PHASE 1 — LIGHTHOUSE: 360° scan from the starting corner, no driving.
#   Near readings (< 25 cm) = the two adjacent walls; everything else is
#   the arena interior.  The shortest interior cluster = the obstacle.
#   The known corner start gives free wall rejection with zero odometry.
#
# PHASE 2 — APPROACH: turn toward the obstacle, drive to ~22 cm away.
#
# PHASE 3 — SPECULARITY PROBE: 360° fine scan measuring echo RELIABILITY.
#   At each angle fire 5 pings and record the hit rate.
#     Disk  (curved, diffuse) : high hit rate from every angle.
#     Triangle (flat, specular): hit rate drops where faces deflect the beam.
#   Classify by counting echo-dropout zones + distance spikes as backup.
#
# HC-SR04 wiring (I/O block, lower-left on the carrier board):
#   VCC  → 3.3V row (pin 11)    GND  → GND row (pin 10)
#   Trig → GP12 (I/O row)       Echo → GP13 (I/O row)
#
# Deploy: copy onto the board AS code.py for mapping runs.

import time
import math
import board
import asyncio
import digitalio

from motor import StepperMotor
import telemetry
from telemetry import log

motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=10)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=10)

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False

us_trig = digitalio.DigitalInOut(board.GP12)
us_trig.direction = digitalio.Direction.OUTPUT
us_trig.value = False

us_echo = digitalio.DigitalInOut(board.GP13)
us_echo.direction = digitalio.Direction.INPUT

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = -1, 1
SPIN_M1, SPIN_M2 = -1, -1
STEPS_PER_DEG     = 12000 / 360
STEPS_PER_CM      = 200.0

# ultrasonic timing
PING_DELAY   = 0.035
ECHO_TIMEOUT = 0.04
MIN_RANGE_CM = 3
MAX_RANGE_CM = 200

# phase 1: lighthouse
LIGHT_DEG    = 8              # coarse scan step (45 readings — objects are big)
NEAR_WALL_CM = 25             # below this = adjacent wall, ignore

# phase 2: approach
TARGET_CM    = 40             # standoff for the probe — far enough back to see
                              # the full shape, not just one face

# phase 3: specularity probe
PROBE_DEG    = 5              # fine scan step (72 readings — objects are big)
PROBE_PINGS  = 5              # pings per angle for hit-rate
HIT_THRESH   = 0.4            # below this = echo dropout
DROPOUT_MIN  = 2              # dropout zones needed → triangle
SPIKE_CM     = 4              # distance-jump threshold (vertex transitions)
SPIKE_MIN    = 2              # spike count needed → triangle
OBS_FRAC     = 0.65           # obstacle sector = readings < this × median

# flat-face detection (the key triangle signal for large objects)
FLAT_CM      = 3              # consecutive readings within this = same face
MIN_FACE_LEN = 3              # at least this many readings to count as a face
FACE_MIN     = 2              # >= this many flat faces → triangle

RUN_SECONDS  = 300
# ====================================================


# ---- ultrasonic primitives ----

def ping_cm():
    us_trig.value = False
    time.sleep(0.000005)
    us_trig.value = True
    time.sleep(0.00001)
    us_trig.value = False
    deadline = time.monotonic() + ECHO_TIMEOUT
    while not us_echo.value:
        if time.monotonic() > deadline:
            return -1.0
    t0 = time.monotonic()
    while us_echo.value:
        if time.monotonic() > deadline:
            return -1.0
    return (time.monotonic() - t0) * 17150.0


def ping_median(n=3):
    vals = []
    for _ in range(n):
        d = ping_cm()
        if d > MIN_RANGE_CM:
            vals.append(d)
        time.sleep(PING_DELAY)
    if not vals:
        return -1.0
    vals.sort()
    return vals[len(vals) // 2]


def ping_probe():
    vals = []
    for _ in range(PROBE_PINGS):
        d = ping_cm()
        if MIN_RANGE_CM < d < MAX_RANGE_CM:
            vals.append(d)
        time.sleep(PING_DELAY)
    hr = len(vals) / PROBE_PINGS
    md = -1.0
    if vals:
        vals.sort()
        md = vals[len(vals) // 2]
    return hr, md


# ---- motor helpers ----

async def wait_motors():
    while motor1.busy or motor2.busy:
        await asyncio.sleep(0)


async def drive(cm):
    motor1.move(FWD_M1 * int(cm * STEPS_PER_CM))
    motor2.move(FWD_M2 * int(cm * STEPS_PER_CM))
    await wait_motors()


async def turn(deg):
    motor1.move(SPIN_M1 * int(deg * STEPS_PER_DEG))
    motor2.move(SPIN_M2 * int(deg * STEPS_PER_DEG))
    await wait_motors()


# ===========================================================
#  PHASE 1 — LIGHTHOUSE (scan from the corner, zero driving)
# ===========================================================

async def lighthouse():
    log("PHASE 1  LIGHTHOUSE — scanning from corner")
    readings = []
    step_n = int(LIGHT_DEG * STEPS_PER_DEG)
    angle = 0.0
    done = 0
    total = int(360 * STEPS_PER_DEG)

    while done < total:
        d = ping_median()
        readings.append((angle, d))
        motor1.move(SPIN_M1 * step_n)
        motor2.move(SPIN_M2 * step_n)
        await wait_motors()
        done += step_n
        angle += LIGHT_DEG

    # separate near-wall from interior
    interior = [(a, d) for a, d in readings if d > NEAR_WALL_CM]
    log("lighthouse: ", len(interior), "/", len(readings), " interior readings")

    if len(interior) < 3:
        log("lighthouse: cannot see interior — try repositioning")
        return None

    # obstacle = shortest cluster in the interior
    dists = sorted(d for _, d in interior)
    median_d = dists[len(dists) // 2]
    threshold = median_d * OBS_FRAC
    cluster = [(a, d) for a, d in interior if d < threshold]

    if not cluster:
        cluster = sorted(interior, key=lambda x: x[1])[:3]
        log("lighthouse: no clear cluster, using 3 shortest")

    mid = cluster[len(cluster) // 2]
    log("lighthouse: obstacle ~", int(mid[1]), "cm at ",
        int(mid[0]), "deg  (", len(cluster), " readings)")

    for i in range(0, len(readings), 12):
        ch = readings[i:i + 12]
        log("  ", " ".join("%d:%d" % (int(a), int(d)) for a, d in ch if d > 0))

    return mid[0], mid[1]


# ===========================================================
#  PHASE 2 — APPROACH (drive to ~TARGET_CM from the obstacle)
# ===========================================================

async def approach(angle, dist):
    log("PHASE 2  APPROACH — turning ", int(angle), " deg")
    await turn(angle)

    to_go = dist - TARGET_CM
    while to_go > 5:
        step = min(to_go, 15)
        await drive(step)
        to_go -= step
        d = ping_median()
        if 0 < d <= TARGET_CM + 8:
            log("approach: in range (", int(d), " cm)")
            break
        if d > 0:
            to_go = d - TARGET_CM

    d = ping_median()
    log("approach: stopped ~", int(d) if d > 0 else "?", "cm from obstacle")


# ===========================================================
#  PHASE 3 — SPECULARITY PROBE (hit-rate fine scan)
# ===========================================================

async def probe():
    log("PHASE 3  SPECULARITY PROBE — ", PROBE_DEG, " deg steps, ",
        PROBE_PINGS, " pings each")

    # turn 180° so the obstacle ends up mid-scan (avoids 0/360 wrap)
    await turn(180)

    readings = []
    step_n = int(PROBE_DEG * STEPS_PER_DEG)
    angle = 0.0
    done = 0
    total = int(360 * STEPS_PER_DEG)

    while done < total:
        hr, md = ping_probe()
        readings.append((angle, hr, md))
        motor1.move(SPIN_M1 * step_n)
        motor2.move(SPIN_M2 * step_n)
        await wait_motors()
        done += step_n
        angle += PROBE_DEG

    log("probe: ", len(readings), " readings collected")
    return readings


# ---- classification ----

def count_faces(dists):
    run = 0
    faces = 0
    for i in range(1, len(dists)):
        if abs(dists[i] - dists[i - 1]) <= FLAT_CM:
            run += 1
        else:
            if run >= MIN_FACE_LEN:
                faces += 1
            run = 0
    if run >= MIN_FACE_LEN:
        faces += 1
    return faces


def classify(readings):
    # ---- identify obstacle sector from echoes that returned ----
    got_echo = [(a, hr, d) for a, hr, d in readings if d > MIN_RANGE_CM]
    if len(got_echo) < 5:
        log("classify: too few echoes (", len(got_echo), ")")
        return "disk"

    dists = sorted(d for _, _, d in got_echo)
    median_d = dists[len(dists) // 2]
    threshold = median_d * OBS_FRAC

    obs_hits = [(a, hr, d) for a, hr, d in got_echo if d < threshold]
    if len(obs_hits) < 2:
        log("classify: obstacle sector too narrow")
        return "disk"

    # angular bounds of obstacle (wide margin to catch edges + vertices)
    margin = PROBE_DEG * 5
    lo = min(a for a, _, _ in obs_hits) - margin
    hi = max(a for a, _, _ in obs_hits) + margin
    sector = [(a, hr, d) for a, hr, d in readings if lo <= a <= hi]

    log("classify: sector ", int(lo), "-", int(hi), " deg, ",
        len(sector), " readings, threshold ", int(threshold), " cm")

    sd = [d for _, _, d in sector if d > MIN_RANGE_CM]

    # ---- SIGNAL 1: echo-dropout zones (specular misses) ----
    dropouts = 0
    in_drop = False
    for _, hr, _ in sector:
        if hr < HIT_THRESH:
            if not in_drop:
                dropouts += 1
                in_drop = True
        else:
            in_drop = False

    # ---- SIGNAL 2: distance spikes (vertex transitions) ----
    spikes = 0
    for i in range(1, len(sd)):
        if abs(sd[i] - sd[i - 1]) >= SPIKE_CM:
            spikes += 1

    # ---- SIGNAL 3: flat-face plateaus ----
    # triangle = 2-3 runs of constant distance (flat faces)
    # cylinder = 0 (distance always changing on a curve)
    faces = count_faces(sd)

    # ---- roughness for the log ----
    if sd:
        mean = sum(sd) / len(sd)
        std = math.sqrt(sum((x - mean) ** 2 for x in sd) / len(sd))
    else:
        std = 0.0

    # any signal is enough
    is_tri = (dropouts >= DROPOUT_MIN
              or spikes >= SPIKE_MIN
              or faces >= FACE_MIN)
    verdict = "triangle" if is_tri else "disk"

    log("classify: dropouts=", dropouts, "  spikes=", spikes,
        "  faces=", faces, "  std=", round(std, 1),
        " -> ", verdict.upper())

    for a, hr, d in sector:
        tag = ""
        if hr < HIT_THRESH:
            tag = " <<<DROP"
        log("  %3d deg  hit %3d%%  %s cm%s"
            % (int(a), int(hr * 100),
               ("%3d" % int(d)) if d > 0 else "---", tag))

    return verdict


# ---- reporting ----

async def report(verdict):
    log("========================================")
    log("  RESULT:  ", verdict.upper())
    log("========================================")
    while True:
        led.value = True
        await asyncio.sleep(0.4 if verdict == "triangle" else 3600)
        if verdict == "triangle":
            led.value = False
            await asyncio.sleep(0.4)


# ---- main ----

async def main():
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if telemetry.start():
        asyncio.create_task(telemetry.serve())

    d = ping_cm()
    log("boot: ultrasonic =", round(d, 1) if d > 0 else "NO ECHO", "cm")
    if d < 0:
        log("HC-SR04 not responding — check Trig->GP12, Echo->GP13, VCC->3V3")

    t0 = time.monotonic()

    result = await lighthouse()

    if result is None:
        log("FALLBACK: driving toward center, retrying")
        await turn(45)
        await drive(45)
        result = await lighthouse()

    if result:
        await approach(result[0], result[1])
    else:
        log("FALLBACK: no obstacle found, probing from here")

    data = await probe()
    verdict = classify(data)

    log("total elapsed ", int(time.monotonic() - t0), " s")
    await report(verdict)


asyncio.run(main())
