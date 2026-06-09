import time
import board
import asyncio
import analogio
import digitalio

from motor import StepperMotor
import telemetry
from telemetry import log

# ---- motors (differential drive) ----
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=8)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=8)

# ---- light sensors (photodiodes) ----
sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

# ---- docking hardware ----
hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False            # indicator stays OFF until docked AND stationary

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = 1, -1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = 1, 1      # spin in place = SAME sign
STEER_SIGN       = 1         # set -1 if it steers AWAY from the light
BRIGHTER_IS_HIGHER = True    # set False if covering a sensor RAISES its number
                             # (only matters when USE_FLICKER = False)

# -- blinking-beacon detection (phone strobe app) --
USE_FLICKER = True           # True = home on the BLINKING light only; steady room light cancels
BEACON_HZ   = 9.3            # strobe blink rate, MEASURED with beacon_meter.py (9.28 Hz, 56% duty)
                             # -> each "look" now takes only ~0.13 s
SMOOTH_MS   = 10             # per-sample averaging window; >=10 ms cancels mains (100 Hz) flicker

DEADBAND_FRAC = 0.20         # turn only if |L-R| exceeds this fraction of the mean signal
                             # (relative, so it works at any distance/brightness)
# steering: turn size scales with how off-centre the light is (proportional)
TURN_GAIN = 900              # turn steps = TURN_GAIN * |L-R| / (L+R), clamped:
TURN_MIN  = 60               #   barely off-centre -> small trim
TURN_MAX  = 500              #   strongly off-centre -> one big correction (~15 deg)

# stride: cover ground when far, fine-tune when near (levels from live telemetry)
NEAR_LEVEL = 20000           # L+R above this = close to the beacon
FWD_FAR    = 1200            # ~6 cm per advance when far
FWD_NEAR   = 400             # ~2 cm per advance when near

# 360 light-seek
SPIN_STEP       = 360        # steps per scan step (~11 deg; smaller = finer but slower scan)
FULL_TURN_STEPS = 12000      # steps for ONE full 360 in-place turn (CALIBRATE - see notes)
SEEK_EXIT_LEVEL = 6000       # during the scan, a heading at least this strong = the beacon:
                             # stop scanning and start driving (skip the rest of the circle)
LOST_LEVEL      = 500 if USE_FLICKER else 1500   # a look with L+R below this is "weak"
MISS_LIMIT      = 3          # re-seek only after this many consecutive weak looks
                             # (single weak looks happen when a look lands in the
                             #  strobe's pause - don't restart the whole scan for one)

# docking (hall sensor GP27, indicator LED GP8)
DOCKING_ENABLED = True       # False = pure light-follow test (hall/LED ignored)
MAGNET_DETECTED = True       # hall.value when the magnet is present
                             # (team-measured; if docking misfires, verify with hall_test.py)
SETTLE_TIME     = 0.5        # seconds fully stopped before the indicator turns on
                             # (the -5 rule: NEVER signal while moving)
# ====================================================


def brightness(ai):
    v = ai.value
    return v if BRIGHTER_IS_HIGHER else (65535 - v)


async def read_lr():
    # One "look" with both sensors at once.
    # USE_FLICKER mode: watch for ~1.2 blink periods and return how much each
    # sensor WOBBLES (max - min). Steady room light doesn't wobble, so it
    # cancels out -- only the blinking torch registers. Each sample is itself
    # averaged over SMOOTH_MS, which erases the 100 Hz flicker of mains-powered
    # room lights. (BRIGHTER_IS_HIGHER is irrelevant here: blinking wobbles
    # the reading either way.)
    if not USE_FLICKER:
        return brightness(sensorL), brightness(sensorR)
    min_l = min_r = 65535
    max_l = max_r = 0
    t_end = time.monotonic() + 1.2 / BEACON_HZ
    while time.monotonic() < t_end:
        sum_l = sum_r = n = 0
        t_smooth = time.monotonic() + SMOOTH_MS / 1000
        while time.monotonic() < t_smooth:
            sum_l += sensorL.value
            sum_r += sensorR.value
            n += 1
        l = sum_l // n
        r = sum_r // n
        if l < min_l: min_l = l
        if l > max_l: max_l = l
        if r < min_r: min_r = r
        if r > max_r: max_r = r
        await asyncio.sleep(0)
    return max_l - min_l, max_r - min_r


def drive_forward(steps):
    motor1.move(FWD_M1 * steps)
    motor2.move(FWD_M2 * steps)


def spin(steps):
    motor1.move(SPIN_M1 * steps)
    motor2.move(SPIN_M2 * steps)


def docked():
    return DOCKING_ENABLED and hall.value == MAGNET_DETECTED


async def wait_for_motors(*motors):
    while any(m.busy for m in motors):
        await asyncio.sleep(0)


async def wait_or_dock(*motors):
    # Like wait_for_motors, but watches the hall sensor DURING the move:
    # the instant we make dock contact, cancel any remaining motion.
    while any(m.busy for m in motors):
        if docked():
            for m in motors:
                m.move_to(m.position)
            return True
        await asyncio.sleep(0)
    return docked()


async def seek_light():
    # Rotate one full turn, remember the heading with the most light,
    # then turn back to face it ("lock on").
    log("SEEK: rotating to find the light...")
    best = -1
    best1, best2 = motor1.position, motor2.position
    done = 0
    while done < FULL_TURN_STEPS:
        spin(SPIN_STEP)
        await wait_for_motors(motor1, motor2)
        done += SPIN_STEP
        l, r = await read_lr()
        level = l + r
        if level >= SEEK_EXIT_LEVEL:
            log("SEEK: strong signal (", level, ") - early lock, driving now")
            return
        if level > best:
            best = level
            best1, best2 = motor1.position, motor2.position
    motor1.move_to(best1)
    motor2.move_to(best2)
    await wait_for_motors(motor1, motor2)
    log("SEEK: locked on (level", best, ")")


async def light_follow():
    # 1) spin 360 to find & lock onto the beacon, 2) home in on it.
    # Exits as soon as the hall sensor reports dock contact.
    # (With DOCKING_ENABLED = False this never exits - pure homing test.)
    await seek_light()
    misses = 0
    while not docked():
        l, r = await read_lr()
        if (l + r) < LOST_LEVEL:
            misses += 1
            log("weak look", misses, "of", MISS_LIMIT, "- L:", l, " R:", r)
            if misses >= MISS_LIMIT:
                log("LOST -> re-seek")
                await seek_light()
                misses = 0
            continue                    # hold position, just look again
        misses = 0
        diff = l - r
        if abs(diff) > DEADBAND_FRAC * (l + r) / 2:
            toward_left = diff > 0
            turn = min(TURN_MAX, max(TURN_MIN, int(TURN_GAIN * abs(diff) / (l + r))))
            spin(STEER_SIGN * (turn if toward_left else -turn))
            log("L:", l, " R:", r, " -> turn", "LEFT" if toward_left else "RIGHT", turn)
            if await wait_or_dock(motor1, motor2):
                break
        else:
            log("L:", l, " R:", r, " -> straight")
        steps = FWD_NEAR if (l + r) > NEAR_LEVEL else FWD_FAR
        drive_forward(steps)
        if await wait_or_dock(motor1, motor2):
            break

    log("HALL: dock contact detected")


async def dock_sequence():
    # We just stopped on the dock. Settle, verify we are STILL docked and
    # fully stationary, and only then turn the indicator on (-5 rule).
    await wait_for_motors(motor1, motor2)
    await asyncio.sleep(SETTLE_TIME)
    if docked() and not (motor1.busy or motor2.busy):
        led.value = True
        log("DOCKED + STATIONARY -> indicator ON. Holding position.")
        return True
    log("dock contact lost during settle -> resume homing")
    return False


async def main():
    global DOCKING_ENABLED
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if telemetry.start():
        asyncio.create_task(telemetry.serve())

    # Boot self-check: an unwired/mispolarized hall would read "docked" here
    # and freeze the robot at the start line. Detect that and fall back to a
    # pure homing run instead.
    if DOCKING_ENABLED and hall.value == MAGNET_DETECTED:
        log("WARNING: hall reads 'docked' at boot - check wiring / MAGNET_DETECTED.")
        log("Docking checks DISABLED for this run (pure light-follow).")
        DOCKING_ENABLED = False

    while True:
        await light_follow()            # returns only on dock contact
        if await dock_sequence():
            break                       # docked, stationary, indicator on
    while True:
        await asyncio.sleep(1)          # hold forever: coils + magnet keep us put,
                                        # telemetry stays up


asyncio.run(main())
