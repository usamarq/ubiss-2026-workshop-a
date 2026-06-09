import board
import asyncio
import analogio

from motor import StepperMotor

# ---- motors (differential drive) ----
motor1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=8)
motor2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=8)

# ---- light sensors (photodiodes) ----
sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

# ================= TUNABLE CONSTANTS =================
FWD_M1, FWD_M2   = 1, -1     # forward = OPPOSITE signs (mirror-mounted motors)
SPIN_M1, SPIN_M2 = 1, 1      # spin in place = SAME sign
STEER_SIGN       = 1         # set -1 if it steers AWAY from the light
BRIGHTER_IS_HIGHER = True    # set False if covering a sensor RAISES its number
DEADBAND  = 1500             # |L-R| under this = drive straight
TURN_STEP = 80               # steps per steering pivot
FWD_STEP  = 200              # steps per forward advance

# 360 light-seek
SPIN_STEP       = 120        # steps per scan step (smaller = finer scan)
FULL_TURN_STEPS = 12000      # steps for ONE full 360 in-place turn (CALIBRATE - see notes)
LOST_LEVEL      = 1500       # if L+R drops below this, seek again
# ====================================================


def brightness(ai):
    v = ai.value
    return v if BRIGHTER_IS_HIGHER else (65535 - v)


def drive_forward(steps):
    motor1.move(FWD_M1 * steps)
    motor2.move(FWD_M2 * steps)


def spin(steps):
    motor1.move(SPIN_M1 * steps)
    motor2.move(SPIN_M2 * steps)


async def wait_for_motors(*motors):
    while any(m.busy for m in motors):
        await asyncio.sleep(0)


async def seek_light():
    # Rotate one full turn, remember the heading with the most light,
    # then turn back to face it ("lock on").
    print("SEEK: rotating to find the light...")
    best = -1
    best1, best2 = motor1.position, motor2.position
    done = 0
    while done < FULL_TURN_STEPS:
        spin(SPIN_STEP)
        await wait_for_motors(motor1, motor2)
        done += SPIN_STEP
        level = brightness(sensorL) + brightness(sensorR)
        if level > best:
            best = level
            best1, best2 = motor1.position, motor2.position
    motor1.move_to(best1)
    motor2.move_to(best2)
    await wait_for_motors(motor1, motor2)
    print("SEEK: locked on (level", best, ")")


async def light_follow():
    # 1) spin 360 to find & lock onto the light, then 2) follow it.
    await seek_light()
    while True:
        l = brightness(sensorL)
        r = brightness(sensorR)
        if (l + r) < LOST_LEVEL:
            await seek_light()          # lost it -> seek again
            continue
        diff = l - r
        if abs(diff) > DEADBAND:
            toward_left = diff > 0
            spin(STEER_SIGN * (TURN_STEP if toward_left else -TURN_STEP))
            print("L:", l, " R:", r, " -> turn", "LEFT" if toward_left else "RIGHT")
            await wait_for_motors(motor1, motor2)
        else:
            print("L:", l, " R:", r, " -> straight")
        drive_forward(FWD_STEP)
        await wait_for_motors(motor1, motor2)


async def main():
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    await light_follow()


asyncio.run(main())
