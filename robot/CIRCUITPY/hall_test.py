# hall_test.py - open in Thonny and press Run. Quick live readout of the hall.
# VERIFIED 2026-06-10 (hall_watch.py magnet session): the sensor is on GP27,
# idles LOW, reads HIGH while a magnet is present. Only ONE magnet face
# triggers it (unipolar) - mark the working face. GP10 has nothing on it;
# this file previously said GP10/active-low, which was stale.
# For transition timestamps / both-pin logging use hall_watch.py instead.
import board, digitalio, time

hall = digitalio.DigitalInOut(board.GP27)
hall.direction = digitalio.Direction.INPUT
hall.pull = digitalio.Pull.UP        # note: unplugged sensor floats HIGH = "MAGNET"

while True:
    print("HALL:", "MAGNET" if hall.value else "(none)")
    time.sleep(0.2)
