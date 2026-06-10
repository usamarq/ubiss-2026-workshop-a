# mapping_code.py - Task 2: disk vs triangle (project/environment-mapping.md, Plan A).
# Sensors: ONE contact bit + the steppers' own step counts. Find the obstacle,
# hug its boundary one lap, classify by how the turning is DISTRIBUTED around
# the lap: a triangle turns in ~3 concentrated bursts (the corners), a disk
# turns a little on every stride. Report = LED + telemetry banner.
#
# Deploy: copy onto the board AS code.py for mapping runs; docking keeps the
# repo's code.py. (HANDOVER.md "suggested structure".)
#
# STATUS: SCAFFOLD. Runs end-to-end in structure, but:
#   - CONTACT_PIN is None -> boot guard refuses to start (no bumper wired yet).
#     Stepper stall is NOT software-detectable (open-loop, stalls silently),
#     so we need a real contact bit: microswitch (best) or IMU spike.
#   - All *_CM / *_DEG marked TODO are guesses pending shape measurements.
import time
import math
import board
import asyncio
import digitalio

from motor import StepperMotor
import telemetry
from telemetry import log

# ---- motors (same wiring + conventions as code.py) ----
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=8)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=8)

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = 1, -1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = 1, 1      # spin in place = SAME sign
# positive spin steps = LEFT turn (code.py's STEER_SIGN=1 was verified live)

CONTACT_PIN     = None       # TODO: wire microswitch, set e.g. board.GP9
CONTACT_PRESSED = False      # pull-up wiring: pressed pulls the pin LOW

# odometry calibration (from code.py's measured constants)
STEPS_PER_DEG = 12000 / 360  # FULL_TURN_STEPS = 12000 per 360 in-place turn
STEPS_PER_CM  = 200.0        # FWD_FAR comment: 1200 steps ~ 6 cm. TODO verify
                             # with a tape measure before scoring runs.

ARENA_CM      = 120          # barricaded square, robot starts in a corner
NOSE_CM       = 5            # robot centre -> bumper tip. TODO measure
WALL_MARGIN_CM = 15          # contact within this of a predicted wall = wall,
                             # not obstacle (absorbs odometry drift)

# find-the-obstacle sweep (boustrophedon lanes from the corner)
LANE_CM       = 25           # lane spacing; MUST be < smallest shape footprint.
                             # TODO set after measuring the shapes
SWEEP_STRIDE  = 1200         # steps per advance while sweeping (~6 cm)

# boundary hug (bug-style: one contact bit)
BACK_CM       = 3            # reverse this far after each contact
TURN_AWAY_DEG  = 25          # turn away from the obstacle after contact
TURN_TOWARD_DEG = 10         # drift back toward it per contact-less stride
HUG_STRIDE_CM = 5            # advance per hug step
MIN_LAP_CM    = 40           # don't test loop closure before this much hugging
CLOSE_RADIUS_CM = 12         # back within this of first contact = lap closed
MAX_LAP_CM    = 450          # drift runaway guard (~ perimeter upper bound)

# classifier: a "corner" = toward-turning accumulated between two contacts
BURST_DEG     = 45           # >= this between contacts = corner burst.
                             # Disk of R>=15cm with 5cm strides needs ~<20deg
                             # per stride -> threshold gap is huge.
TRIANGLE_MIN_BURSTS = 2      # 3 corners expected; 2 tolerates one merged/missed

RUN_SECONDS   = 300          # brief: autonomous for 5 minutes
REPORT_AT     = 280          # force best-guess report by here
# ====================================================

if CONTACT_PIN is not None:
    _contact = digitalio.DigitalInOut(CONTACT_PIN)
    _contact.direction = digitalio.Direction.INPUT
    _contact.pull = digitalio.Pull.UP
else:
    _contact = None


def contact():
    # The single sensing bit of Plan A.
    return _contact is not None and _contact.value == CONTACT_PRESSED


# ---- dead-reckoning pose (x, y in cm from the start corner; heading deg, 0 = +x) ----
pose = {"x": 0.0, "y": 0.0, "h": 0.0}


def _advance_pose(steps):
    d = steps / STEPS_PER_CM
    pose["x"] += d * math.cos(math.radians(pose["h"]))
    pose["y"] += d * math.sin(math.radians(pose["h"]))


def _turn_pose(steps):
    pose["h"] = (pose["h"] + steps / STEPS_PER_DEG) % 360


def dist_to(x, y):
    return math.sqrt((pose["x"] - x) ** 2 + (pose["y"] - y) ** 2)


async def wait_for_motors(*motors):
    while any(m.busy for m in motors):
        await asyncio.sleep(0)


async def advance(steps):
    # Drive forward (negative = reverse) watching the bumper. Returns True on
    # contact; pose is credited only for the steps actually taken.
    start = motor1.position
    motor1.move(FWD_M1 * steps)
    motor2.move(FWD_M2 * steps)
    hit = False
    while motor1.busy or motor2.busy:
        if steps > 0 and contact():
            motor1.move_to(motor1.position)
            motor2.move_to(motor2.position)
            hit = True
            break
        await asyncio.sleep(0)
    _advance_pose((motor1.position - start) * FWD_M1)
    return hit


async def turn_deg(deg):
    # In-place turn, positive = LEFT. Blind (no contact watch: turning in
    # place can chatter the bumper against the obstacle - that's fine).
    steps = int(deg * STEPS_PER_DEG)
    motor1.move(SPIN_M1 * steps)
    motor2.move(SPIN_M2 * steps)
    await wait_for_motors(motor1, motor2)
    _turn_pose(steps)


def near_wall():
    # Is the CONTACT point (nose, not centre) at a predicted wall?
    nx = pose["x"] + NOSE_CM * math.cos(math.radians(pose["h"]))
    ny = pose["y"] + NOSE_CM * math.sin(math.radians(pose["h"]))
    return (nx < WALL_MARGIN_CM or nx > ARENA_CM - WALL_MARGIN_CM
            or ny < WALL_MARGIN_CM or ny > ARENA_CM - WALL_MARGIN_CM)


def snap_to_wall():
    # Free odometry re-zero: we KNOW where the wall we just touched is.
    # Snap whichever coordinate the heading says we drove into. (Heading
    # itself can't be fixed from one contact - left as is.)
    h = pose["h"] % 360
    if h < 45 or h >= 315:
        pose["x"] = ARENA_CM - NOSE_CM
    elif h < 135:
        pose["y"] = ARENA_CM - NOSE_CM
    elif h < 225:
        pose["x"] = NOSE_CM
    else:
        pose["y"] = NOSE_CM


async def find_obstacle(deadline):
    # Boustrophedon lanes from the corner. A contact NOT at a predicted wall
    # is the obstacle. Wall contacts re-zero odometry for free.
    lane_dir = 1                       # +x first, alternate each lane
    while time.monotonic() < deadline:
        hit = await advance(SWEEP_STRIDE)
        if not hit:
            continue
        if not near_wall():
            log("OBSTACLE at x", int(pose["x"]), "y", int(pose["y"]))
            return True
        snap_to_wall()
        log("wall contact -> re-zeroed: x", int(pose["x"]), "y", int(pose["y"]))
        # lane end: back off, step one lane over (+y), come back the other way
        await advance(-int(BACK_CM * STEPS_PER_CM))
        await turn_deg(90 * lane_dir)
        if await advance(int(LANE_CM * STEPS_PER_CM)):
            if not near_wall():
                log("OBSTACLE (during lane step) x", int(pose["x"]), "y", int(pose["y"]))
                return True
            snap_to_wall()           # top wall: sweep done without finding it
            log("swept to far wall without obstacle contact - re-sweeping")
        await turn_deg(90 * lane_dir)
        lane_dir = -lane_dir
    return False


async def hug_lap(deadline):
    # Bug-style boundary follow, obstacle kept on the LEFT: on contact back
    # off and turn RIGHT (away); while contact-less drift LEFT (toward).
    # Record the toward-turning accumulated between consecutive contacts -
    # that's the corner detector.
    first = (pose["x"], pose["y"])
    samples = []                       # turn_deg accumulated before each contact
    turn_since = 0.0
    travelled = 0.0
    await advance(-int(BACK_CM * STEPS_PER_CM))
    await turn_deg(-TURN_AWAY_DEG)
    while time.monotonic() < deadline and travelled < MAX_LAP_CM:
        hit = await advance(int(HUG_STRIDE_CM * STEPS_PER_CM))
        travelled += HUG_STRIDE_CM
        if hit:
            if near_wall():
                log("WARNING: wall contact during hug - shape may sit near a wall")
            samples.append(turn_since)
            log("contact: turn-since-last", int(turn_since),
                "x", int(pose["x"]), "y", int(pose["y"]))
            turn_since = 0.0
            await advance(-int(BACK_CM * STEPS_PER_CM))
            await turn_deg(-TURN_AWAY_DEG)
        else:
            await turn_deg(TURN_TOWARD_DEG)
            turn_since += TURN_TOWARD_DEG
        if travelled > MIN_LAP_CM and dist_to(*first) < CLOSE_RADIUS_CM:
            log("loop closed after", int(travelled), "cm,", len(samples), "contacts")
            break
    return samples


def classify(samples):
    # Corner bursts: contacts where the contact-less toward-turning before
    # them accumulated >= BURST_DEG. Triangle -> ~3 (its corners); disk ->
    # ~0 (turning arrives in ~TURN_TOWARD_DEG dribbles every stride).
    bursts = sum(1 for t in samples if t >= BURST_DEG)
    verdict = "triangle" if bursts >= TRIANGLE_MIN_BURSTS else "disk"
    log("classify:", len(samples), "contacts,", bursts, "bursts ->", verdict)
    return verdict


async def report(verdict):
    # LED: solid = disk, blinking = triangle. Telemetry banner repeats too.
    log("RESULT:", verdict.upper())
    while True:
        led.value = True
        await asyncio.sleep(0.4 if verdict == "triangle" else 3600)
        if verdict == "triangle":
            led.value = False
            await asyncio.sleep(0.4)


async def main():
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if telemetry.start():
        asyncio.create_task(telemetry.serve())

    if _contact is None:
        log("NO CONTACT SENSOR (CONTACT_PIN is None) - refusing to drive.")
        log("Wire the bumper, set CONTACT_PIN, redeploy.")
        while True:
            await asyncio.sleep(1)

    t0 = time.monotonic()
    deadline = t0 + REPORT_AT
    samples = []
    if await find_obstacle(deadline):
        samples = await hug_lap(deadline)
    else:
        log("WARNING: no obstacle found before deadline")
    verdict = classify(samples)
    log("elapsed", int(time.monotonic() - t0), "s of", RUN_SECONDS)
    await report(verdict)


asyncio.run(main())
