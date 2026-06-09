# Robot — hardware & code notes

_Backed up from the live `CIRCUITPY` drive on Jun 9. Code mirror in [`CIRCUITPY/`](CIRCUITPY/)._

## Board
- **Raspberry Pi Pico 2 W** (RP2350A), **CircuitPython 10.2.1** (board ID `raspberry_pi_pico2_w`).
- Has **Wi-Fi** — a communication resource, if we ever want it.
- Serial REPL port (this Mac): `/dev/cu.usbmodem101`.

## Drivetrain — TWO stepper motors (differential drive)
- `motor1` → GP15, GP16, GP17, GP18
- `motor2` → GP19, GP20, GP21, GP22
- Driver: custom `motor.py` `StepperMotor` class — FULLSTEP, **4096 steps/rev**, default `rpm=6` (slow, precise).
- ⇒ **Differential drive**: both motors forward = straight; opposite directions = turn in place (see `demo()` in `code.py`).
- ⇒ 🧭 **Dead-reckoning for free:** steppers are open-loop precise, so *step counts act as odometry*. The robot can estimate its own pose without encoders — a cheap proprioceptive information-state (and a tidy info-space example for the exam).

## Sensors wired in code
- `sensorL = AnalogIn(GP28)`, `sensorR = AnalogIn(GP26)` — two **analog** inputs, left & right.
- Almost certainly the **photodiodes** (analog light) → the robot is already a **Braitenberg light-seek platform**. _(Confirm what's physically on GP26 / GP28.)_

## Libraries on board (`lib/`)
- `adafruit_motor`, `adafruit_ticks`, `asyncio`

## What `code.py` does today
- Async app: `motor1.run()` + `motor2.run()` (step schedulers) + `read_sensors()` (prints L/R every 10 ms) + `demo()` (drive forward, then turn, looping). A movement + sensor-print skeleton.

## Implications for the docking project
- ✅ **Braitenberg light-homing (Stage 1) is directly supported** — 2 analog light sensors + differential drive already wired.
- ✅ **Dead reckoning** (step counting) is a bonus homing / fine-positioning resource.
- The `read_sensors()` print loop is exactly the tool for the **ambient-light field test** (watch L/R, beacon off vs on at 1 m).
