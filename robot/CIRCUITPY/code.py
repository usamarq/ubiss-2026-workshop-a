import board
import digitalio
import time
import asyncio
import analogio

from motor import StepperMotor

#Setup motors
motor1 = StepperMotor(
    board.GP15,
    board.GP16,
    board.GP17,
    board.GP18,
    rpm=6
)

motor2 = StepperMotor(
    board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
    rpm=6
)

sensorL = analogio.AnalogIn(board.GP28)
sensorR = analogio.AnalogIn(board.GP26)

async def wait_for_motors(*motors):
    #Wait for the motors to finish rotating
    while any(m.busy for m in motors):
        await asyncio.sleep(0)

#Example code for running a sequence of movements
async def demo():
    while True:
        motor1.move(2048)
        motor2.move(2048)
        
        await wait_for_motors(motor1, motor2)
        
        motor1.move(2048)
        motor2.move(-2048)
        await wait_for_motors(motor1,motor2)
        
        await asyncio.sleep(1) #Wait for one second


#def calibrate():

    
#Loop for reading sensor values
async def read_sensors():
    while True:
        #Read some sensor values here
        valueL = sensorL.value
        valueR = sensorR.value
        print(valueL, valueR)
        await asyncio.sleep(0.01)


async def main():
    asyncio.create_task(motor1.run())
    asyncio.create_task(motor2.run())
    asyncio.create_task(read_sensors())
    await demo()

asyncio.run(main())
        
