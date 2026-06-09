# docking_code.py - beacon homing + hall docking + LED indicator.
# Run this in Thonny (or rename to code.py to auto-run on boot).
# Movement convention is taken from the demo:
#   forward = OPPOSITE signs, spin-in-place = SAME sign (mirror-mounted motors).
import board, digitalio, analogio, asyncio
from motor import StepperMotor

# =================== TUNABLE CONSTANTS ===================
LIGHT_FOLLOW_TEST = True     # True = just drive toward light (no docking/hall/LED)

TRAVEL_RPM      = 8

# motion sign convention (flip a sign if a move goes the wrong way)
FWD_M1, FWD_M2   = 1, -1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = 1, 1      # spin in place = SAME sign
STEER_SIGN       = 1         # if homing steers AWAY from the beacon, set this to -1

# light homing
BRIGHTER_IS_HIGHER = True    # set False if covering a photodiode RAISES its reading
DEADBAND        = 1500       # |L-R| under this  -> "aimed at beacon", drive straight
TURN_STEP       = 80         # steps per steering pivot
FWD_STEP        = 200        # steps per forward advance
LOST_LEVEL      = 1500       # if L+R below this, beacon lost -> re-acquire

# initial search spin
SPIN_STEP       = 120        # steps per scan increment
FULL_TURN_STEPS = 4096       # steps for ~one full in-place turn (CALIBRATE this)

# docking
MAGNET_DETECTED = True       # hall.value when a magnet is present (measured)

# finishing
SETTLE_TIME     = 0.5        # seconds stopped before lighting the indicator
# =========================================================

# ---- hardware ----
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=TRAVEL_RPM)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=TRAVEL_RPM)

sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP8)
led.direction = digitalio.Direction.OUTPUT

# ---- helpers ----
def brightness(ai):
    v = ai.value
    return v if BRIGHTER_IS_HIGHER else (65535 - v)

def drive_forward(steps):
    motor1.move(FWD_M1 * steps)
    motor2.move(FWD_M2 * steps)

def spin(steps):
    motor1.move(SPIN_M1 * steps)
    motor2.move(SPIN_M2 * steps)

def docked():
    return hall.value == MAGNET_DETECTED

async def wait_until_stopped():
    while motor1.busy or motor2.busy:
        await asyncio.sleep(0)

# ---- states ----
async def acquire():
    # Spin ~one full turn, remember the heading with the strongest beacon
    # signal, then rotate back to face it. Handles the random start orientation.
    print("ACQUIRE: searching for beacon...")
    best = -1
    best1, best2 = motor1.position, motor2.position
    done = 0
    while done < FULL_TURN_STEPS:
        spin(SPIN_STEP)
        await wait_until_stopped()
        done += SPIN_STEP
        level = brightness(sensorL) + brightness(sensorR)
        if level > best:
            best = level
            best1, best2 = motor1.position, motor2.position
    motor1.move_to(best1)
    motor2.move_to(best2)
    await wait_until_stopped()
    print("ACQUIRE: facing beacon (level", best, ")")

async def home():
    # Steer toward the brighter sensor and advance, until the hall says docked.
    print("HOME: driving to dock...")
    while not docked():
        l = brightness(sensorL)
        r = brightness(sensorR)
        if (l + r) < LOST_LEVEL:
            await acquire()
            continue
        diff = l - r
        if abs(diff) > DEADBAND:
            # turn toward the brighter side
            spin(STEER_SIGN * (TURN_STEP if diff > 0 else -TURN_STEP))
            await wait_until_stopped()
        drive_forward(FWD_STEP)
        await wait_until_stopped()
    print("HOME: docked!")

async def docking():
    led.value = False                      # indicator OFF while moving
    await acquire()
    await home()
    # STOP: stop issuing moves and confirm we're stationary (known from .busy).
    await wait_until_stopped()
    await asyncio.sleep(SETTLE_TIME)
    if not motor1.busy and not motor2.busy:
        led.value = True                   # SIGNAL: only now, stopped on the dock
        print("DOCKED + STOPPED -> indicator ON")
    # Do not move again. Coils stay energized (holding torque); no release().

async def light_follow():
    # Drive toward the flashlight: first spin to FACE the brightest direction,
    # then steer-and-advance, re-scanning if the light is lost.
    print("SEEK LIGHT: facing the flashlight, then driving toward it.")
    await acquire()
    while True:
        l = brightness(sensorL)
        r = brightness(sensorR)
        if (l + r) < LOST_LEVEL:
            await acquire()        # lost the light - look around again
            continue
        diff = l - r
        if abs(diff) > DEADBAND:
            toward_left = diff > 0
            spin(STEER_SIGN * (TURN_STEP if toward_left else -TURN_STEP))
            print("L:", l, " R:", r, " -> turn", "LEFT" if toward_left else "RIGHT")
            await wait_until_stopped()
        else:
            print("L:", l, " R:", r, " -> straight")
        drive_forward(FWD_STEP)
        await wait_until_stopped()


async def main():
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    if LIGHT_FOLLOW_TEST:
        await light_follow()      # <-- the phone-flashlight test
    else:
        await docking()           # <-- full docking run
        while True:
            await asyncio.sleep(1)

asyncio.run(main())
