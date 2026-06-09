# hall_test.py — open in Thonny and press Run.
# Hall sensor plugged into the GP10 connector (GND / 3.3V / I/O rows).
# Bring your magnet to the sensor's flat face; try BOTH poles. Reset to return to code.py.
import board, digitalio, time

hall = digitalio.DigitalInOut(board.GP10)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP        # internal pull-up — no external resistor needed

while True:
    detected = not hall.value        # active-low: line is pulled low when a magnet is present
    print("HALL:", "MAGNET" if detected else "(none)")
    time.sleep(0.2)
