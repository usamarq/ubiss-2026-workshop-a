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
sensorL = analogio.AnalogIn(board.GP26)
sensorR = analogio.AnalogIn(board.GP28)

# ---- docking hardware ----
hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT
led.value = False            # indicator stays OFF until docked AND stationary

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = -1, 1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = -1, -1    # spin in place = SAME sign
STEER_SIGN       = 1         # set -1 if it steers AWAY from the light
BRIGHTER_IS_HIGHER = True    # set False if covering a sensor RAISES its number
                             # (only matters when USE_FLICKER = False)

# -- blinking-beacon detection (phone strobe app) --
USE_FLICKER = True           # True = home on the BLINKING light only; steady room light cancels
BEACON_HZ   = 9.4            # strobe blink rate, re-MEASURED with beacon_meter.py
                             # 2026-06-10 bright room: 9.38 Hz, 53% duty
LOOK_PERIODS = 2.4           # blink periods per look (~0.26 s). Was 1.2: at 1 m
                             # the beacon wobble is only ~900 over a ~40k ambient
                             # floor; one period gave +/-30% look noise -> false
                             # weak looks. Two+ full cycles steadies the estimate
SMOOTH_MS   = 10             # per-sample averaging window; >=10 ms cancels mains (100 Hz) flicker

DEADBAND_FRAC = 0.20         # turn only if |L-R| exceeds this fraction of the mean signal
                             # (relative, so it works at any distance/brightness)
# steering: turn size scales with how off-centre the light is (proportional)
TURN_GAIN = 1400             # turn steps = TURN_GAIN * |L-R| / (L+R), clamped:
                             # (900 gave 3-5 deg nudges that never cancelled the
                             #  leftward drift -> persistent RIGHT-arc in telemetry)
TURN_MIN  = 60               #   barely off-centre -> small trim
TURN_MAX  = 500              #   strongly off-centre -> one big correction (~15 deg)

# stride: cover ground when far, fine-tune when near (levels from live telemetry)
NEAR_LEVEL = 7000            # L+R above this = close to the beacon. One-eyed sum
                             # is 2L; mat-edge L measured ~5000 (beacon_meter
                             # 2026-06-10) -> fires just before the mat, switches
                             # to 2 cm strides for the magnet crossing.
                             # (Old 35000 was a two-eyed darker-room number.)
FWD_FAR    = 1200            # ~6 cm per advance when far
FWD_NEAR   = 400             # ~2 cm per advance when near

# 360 light-seek
SPIN_STEP       = 360        # steps per scan step (~11 deg; smaller = finer but slower scan)
FULL_TURN_STEPS = 12000      # steps for ONE full 360 in-place turn (CALIBRATE - see notes)
SEEK_EXIT_LEVEL = 1400       # scan early-exit, two-eyed again (R replaced).
                             # Bright room, L alone: facing at 1 m ~929, off-axis
                             # noise 300-420 -> two-eyed facing sum ~1900, noise
                             # ceiling ~840. 1400 sits between. If the new R is
                             # weak, the full-circle best-pick still recovers.
RAIL_LEVEL      = 64000      # raw MIN above this = diode pegged by ambient the
                             # whole look: it is BLIND (wobble ~0), not in the
                             # dark. Seen on R in the bright-room run: raw
                             # (25133, 25549, 65056, 65058) -> R yanked steering
R_DISABLED      = False      # R photodiode REPLACED 2026-06-10 (old one was
                             # stuck at ~65.3k = electrically dead). New diode
                             # untested - if it also rails, the blind-guard
                             # below auto-mirrors L, so this stays False
AIM_EVERY       = 4          # forward strides between 5-point re-aims: one-eyed
                             # straight legs drift off the beacon line; a quick
                             # +/-2-step scan every ~24 cm keeps the line honest
LOST_LEVEL      = 1000 if USE_FLICKER else 1500  # a look with L+R below this is
                             # "weak". With R mirrored from L the sum is 2L, and
                             # off-axis L noise runs 300-420 -> weak below L~500
MISS_LIMIT      = 3          # re-seek only after this many consecutive weak looks
                             # (single weak looks happen when a look lands in the
                             #  strobe's pause - don't restart the whole scan for one)

# docking (hall sensor GP27, indicator LED GP8)
DOCKING_ENABLED = True       # hall VERIFIED with neodymium magnet (hall_watch
                             # 2026-06-10: 4/4 clean detect/release cycles on GP27;
                             # GP10 dead - hall_test.py's old pin comment was stale)
MAGNET_DETECTED = True       # hall.value while the magnet is present; idles False.
                             # ONE pole only (unipolar) - mount the dock magnet
                             # working-face toward the sensor. NOTE: an unplugged
                             # hall floats HIGH = false "docked" (pull-up), and the
                             # boot self-check only catches that at boot - keep the
                             # hall connector seated.
SETTLE_TIME     = 0.5        # seconds fully stopped before the indicator turns on
                             # (the -5 rule: NEVER signal while moving)

# mat rake: no funnel built yet + the hall's trigger zone is small, so a
# straight approach can pass the magnet a few cm to one side and never fire.
# Once beacon-close, zigzag-creep so the sensor rakes the whole mat area.
RAKE_ENABLED = False         # OFF: ambient/app conditions shifted between runs
                             # and the rake fired at the start line -> robot
                             # wagged in place. Re-enable only after re-running
                             # beacon_meter in the FINAL room and re-setting
                             # SWEEP_LEVEL from that measurement.
SWEEP_LEVEL = 3000           # single-sensor wobble that starts the rake.
                             # CALIBRATED (beacon_meter 2026-06-10): mat distance
                             # ~15-20 cm reads 5020 on L, 1 m reads 929 -> 60% of
                             # mat = fires on arrival, silent on approach. L's 40k
                             # ambient baseline leaves only ~21k headroom, so the
                             # old 30000 was physically unreachable.
RAKE_STEPS  = 990            # half-swing ~30 deg: front sensor arcs ~+/-2.5 cm
                             # (was 20 deg - lateral wander dominated the misses)
RAKE_CREEP  = 160            # ~0.8 cm forward between swings: the rake mesh
                             # must be finer than the hall trigger radius
                             # (first run missed the magnet with 1.5 cm mesh)
RAKE_CYCLES = 18             # swings before giving up (~12 cm of mat depth)
RAKE_BACKUP = 2000           # ~10 cm reverse after an empty rake, re-approach
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
    global raw_extremes
    if not USE_FLICKER:
        return brightness(sensorL), brightness(sensorR)
    min_l = min_r = 65535
    max_l = max_r = 0
    t_end = time.monotonic() + LOOK_PERIODS / BEACON_HZ
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
    # raw levels for saturation diagnosis: max near 65535 = diode railed by
    # ambient light -> wobble collapses no matter how bright the strobe is
    raw_extremes = (min_l, max_l, min_r, max_r)
    return max_l - min_l, max_r - min_r


raw_extremes = (0, 0, 0, 0)


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


async def rake_for_magnet():
    # Endgame coverage: zigzag-creep over the mat, hall watched during every
    # move (incl. the recentre + backup - reversing onto the magnet is still
    # a dock). spin(+) = LEFT. True = contact; False = swept through clean,
    # caller backs onto the beacon line and re-approaches.
    log("RAKE: beacon-close - sweeping the mat for the magnet")
    net = RAKE_STEPS
    spin(RAKE_STEPS)                  # half-swing left off the centerline
    if await wait_or_dock(motor1, motor2):
        return True
    sign = -1
    for _ in range(RAKE_CYCLES):
        drive_forward(RAKE_CREEP)
        if await wait_or_dock(motor1, motor2):
            return True
        net += sign * 2 * RAKE_STEPS
        spin(sign * 2 * RAKE_STEPS)   # full swing across the centerline
        if await wait_or_dock(motor1, motor2):
            return True
        sign = -sign
    log("RAKE: no magnet - recentre, back up", RAKE_BACKUP, "steps, re-approach")
    spin(-net)                        # undo the leftover heading offset
    if await wait_or_dock(motor1, motor2):
        return True
    drive_forward(-RAKE_BACKUP)
    return await wait_or_dock(motor1, motor2)


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


async def fine_aim():
    # One-eyed steering: straight legs drift off the beacon line, so every
    # AIM_EVERY strides nudge across 5 headings (+/-2 scan steps ~ +/-21 deg)
    # and keep the strongest. Hall watched during every nudge. Returns True
    # on dock contact.
    best, best_at = -1, 2
    spin(-2 * SPIN_STEP)
    if await wait_or_dock(motor1, motor2):
        return True
    for k in range(5):                  # headings -2..+2 SPIN_STEPs
        if k:
            spin(SPIN_STEP)
            if await wait_or_dock(motor1, motor2):
                return True
        l, r = await read_lr()
        if max(l, r) > best:
            best, best_at = max(l, r), k
    spin((best_at - 4) * SPIN_STEP)     # from +2 back to the best heading
    if await wait_or_dock(motor1, motor2):
        return True
    log("AIM: best", best, "at offset", best_at - 2)
    return False


async def light_follow():
    # 1) spin 360 to find & lock onto the beacon, 2) home in on it.
    # Exits as soon as the hall sensor reports dock contact.
    # (With DOCKING_ENABLED = False this never exits - pure homing test.)
    await seek_light()
    misses = 0
    strides = 0
    while not docked():
        l, r = await read_lr()
        if (l + r) < LOST_LEVEL:
            misses += 1
            log("weak look", misses, "of", MISS_LIMIT, "- L:", l, " R:", r,
                " raw", raw_extremes)
            if misses >= MISS_LIMIT:
                log("LOST -> re-seek")
                await seek_light()
                misses = 0
            continue                    # hold position, just look again
        misses = 0
        # a railed diode reads "dark" while actually blinded by ambient -
        # don't let it yank the steering; mirror the seeing side instead
        lmin, _, rmin, _ = raw_extremes
        tag = ""
        if R_DISABLED or (rmin > RAIL_LEVEL and lmin <= RAIL_LEVEL):
            r = l
            tag = "[R off]"
        elif lmin > RAIL_LEVEL and rmin <= RAIL_LEVEL:
            l = r
            tag = "[L blind]"
        diff = l - r
        if abs(diff) > DEADBAND_FRAC * (l + r) / 2:
            toward_left = diff > 0
            turn = min(TURN_MAX, max(TURN_MIN, int(TURN_GAIN * abs(diff) / (l + r))))
            spin(STEER_SIGN * (turn if toward_left else -turn))
            log("L:", l, " R:", r, " -> turn", "LEFT" if toward_left else "RIGHT", turn, tag)
            if await wait_or_dock(motor1, motor2):
                break
        else:
            log("L:", l, " R:", r, " -> straight", tag)
        if RAKE_ENABLED and max(l, r) >= SWEEP_LEVEL:
            log("NEAR DOCK (L", l, " R", r, " raw", raw_extremes, ") -> rake")
            if await rake_for_magnet():
                break
            continue                # empty rake: backed off, approach again
        steps = FWD_NEAR if (l + r) > NEAR_LEVEL else FWD_FAR
        drive_forward(steps)
        if await wait_or_dock(motor1, motor2):
            break
        strides += 1
        if strides % AIM_EVERY == 0:
            if await fine_aim():
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
