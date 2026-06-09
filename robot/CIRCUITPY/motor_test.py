# motor_test.py - bare motor check. Open in Thonny and Run.
# No sensors, no homing - just drive both motors forward, then spin.
import board, asyncio
from motor import StepperMotor

m1 = StepperMotor(board.GP15, board.GP16, board.GP17, board.GP18, rpm=8)
m2 = StepperMotor(board.GP19, board.GP20, board.GP21, board.GP22, rpm=8)


async def wait(*motors):
    while any(m.busy for m in motors):
        await asyncio.sleep(0)


async def main():
    asyncio.create_task(m1.run())
    asyncio.create_task(m2.run())

    print("forward...")
    m1.move(2048)
    m2.move(2048)
    await wait(m1, m2)

    print("spin...")
    m1.move(2048)
    m2.move(-2048)
    await wait(m1, m2)

    print("done - did the wheels move?")

asyncio.run(main())
