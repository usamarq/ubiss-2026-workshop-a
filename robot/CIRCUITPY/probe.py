# probe.py — open in Thonny and press Run.
# Trigger each sensor and watch which number reacts; that tells you
# which pin it's actually wired to. Reset the board to go back to code.py.
import board, analogio, time

L = analogio.AnalogIn(board.GP28)   # left photodiode
R = analogio.AnalogIn(board.GP26)   # right photodiode
H = analogio.AnalogIn(board.GP27)   # hall sensor (where we planned it)

while True:
    print("L(GP28):", L.value, "  R(GP26):", R.value, "  HALL(GP27):", H.value)
    time.sleep(0.2)

