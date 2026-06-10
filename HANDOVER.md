# HANDOVER — robot/code thread ↔ notes/planning thread

> Read this fully before touching anything. You (the agent reading this) are the
> **hands-on thread**: CircuitPython code, the docking + mapping tasks, deploying
> to the robot, and syncing this repo. A separate Claude Code thread owns
> lecture notes, exam prep, and planning. **Keep this file updated** as state
> changes — it is the contract between threads.

## Context
UBISS 2026 Workshop A ("Minimalism in Robotics"), University of Oulu, June 8–13.
Team project = two scored tasks built on a small robot:
1. **Docking** — see [`project/docking-station.md`](project/docking-station.md) (brief, scoring, the "beacon-homed magnetic funnel" design).
2. **Environment mapping** (disk vs triangle classification) — see [`project/environment-mapping.md`](project/environment-mapping.md) (analysis, Plan A tactile + Plan B ultrasonic).

## Paths
- **Repo (this folder):** `/Users/usamaraheel/Desktop/UBISS 2026 workshop A reading package and pre summer school assignments/ubiss-2026-workshop-a/`
- **Robot mirror in repo:** `robot/CIRCUITPY/` ← the source of truth that gets committed
- **Live robot drive:** `/Volumes/CIRCUITPY` (mounts when the Pico is plugged in via USB)
- **Desktop venv (for syntax checks):** `../.venv/bin/python` (Python 3.14, relative to repo root)

## Hardware truth (verified)
- **Board:** Raspberry Pi Pico 2 W (RP2350A), CircuitPython 10.2.1, serial REPL `/dev/cu.usbmodem101`.
- **Motors:** 2× 28BYJ-48-class steppers via custom `motor.py` (FULLSTEP, 4096 steps/rev).
  `motor1` = GP15–18, `motor2` = GP19–22. Differential drive, **mirror-mounted**:
  forward = OPPOSITE signs (`1, -1`), spin-in-place = SAME signs.
- **rpm 8 = safe. 12 = stalls** (silently: driver LEDs blink, shaft doesn't move). 10 untested.
- **Light sensors (photodiodes):** `sensorL` = GP28, `sensorR` = GP26 (analog).
- **Hall sensor:** GP27 (pull-up) — **VERIFIED 2026-06-10** with neodymium magnet via
  `hall_watch.py`: idles LOW, reads HIGH while magnet present (`MAGNET_DETECTED = True`
  correct), 4/4 clean detect/release cycles, no bounce. **Unipolar: only ONE magnet face
  triggers** — mark the working face; it must point at the robot's sensor in the dock.
  GP10 has nothing on it (old hall_test.py comment was stale, since fixed).
  ⚠️ Unplugged hall floats HIGH = false "docked"; boot self-check only catches boot-time —
  keep the connector seated.
- **Indicator LED:** GP8 (existence on the physical robot unconfirmed).
- **Dead reckoning:** stepper step counts = free odometry (positions in `motor.position`).

## Software state (all in `robot/CIRCUITPY/`, mirrored on the board)
- **`code.py` = THE program** (auto-runs on boot). Complete pipeline:
  flicker-beacon homing → (when enabled) docking endgame. Key tunables at top,
  **each calibrated from live telemetry — don't regress them**:
  - `BEACON_HZ = 9.3` — MEASURED strobe rate of the user's phone app (9.28 Hz, 56% duty).
    If the app setting changes, re-measure with `beacon_meter.py`. The look window is
    `1.2 / BEACON_HZ`; a mismatch (esp. BEACON_HZ > real rate) breaks detection.
  - `SEEK_EXIT_LEVEL = 2400` (facing-beacon-at-1m reads ~3050; early-exits the 360° scan)
  - `NEAR_LEVEL = 35000` (dock-adjacent sums ~50k; switches 6 cm strides → 2 cm)
  - `TURN_GAIN = 1400`, `TURN_MIN/MAX = 60/500` (proportional steering)
  - `DEADBAND_FRAC = 0.20` (relative deadband), `LOST_LEVEL = 500`, `MISS_LIMIT = 3` (3-strike)
  - `SPIN_STEP = 360`, `FULL_TURN_STEPS = 12000` (calibrated full robot turn)
  - **`DOCKING_ENABLED = True`** (since 2026-06-10: magnet + hall verified)
  - `MAGNET_DETECTED = True` (VERIFIED — idle False, True while magnet present), `SETTLE_TIME = 0.5`
- **`motor.py`** — StepperMotor. ⚠️ Contains a critical fix: the idle branch re-pins
  `next_step` to now; without it, any pause (sensor reads) causes a catch-up step
  burst that silently stalls the motor. **Never revert this.**
- **`telemetry.py`** — robot makes its own WiFi AP `UBISS-Robot`, serves a live log page
  at `http://192.168.4.1/` (auto-refresh 1 s). Use `from telemetry import log; log(...)`
  instead of print in robot code (it does both). Wired into code.py's main().
- **`mapping_code.py`** — Task 2 scaffold (Plan A: contact bit + odometry turn bursts).
  Full state machine (boustrophedon sweep → wall-vs-obstacle by pose → bug-style hug
  lap → turn-burst classifier → LED/telemetry report, 5-min watchdog). Classifier
  desktop-tested on synthetic laps (clean + noisy: all 4 correct). **Not runnable yet:**
  `CONTACT_PIN = None` boot-guards until a bumper is wired; `STEPS_PER_CM`, `LANE_CM`,
  `NOSE_CM` are TODO pending tape-measure + shape exam. Deploys by copying onto the
  board AS code.py for mapping runs.
- **`beacon_meter.py`** — run in Thonny: measures real strobe Hz/duty via the photodiodes.
- **`hall_test.py`, `motor_test.py`, `probe.py`** — team test scripts (motor_test = bare
  motion check, used to isolate power vs code issues).
- **`settings.toml`** — ON THE BOARD ONLY (gitignored): `AP_SSID`/`AP_PASSWORD` for the AP.
  Template: `settings.toml.example`. **Never commit credentials** (repo is PUBLIC;
  history was already scrubbed once — don't reintroduce).
- **`wifi_control.py`** — repo-only (not on board): manual WiFi drive page. Sanitized.

## Workflows
- **Deploy:** edit in `robot/CIRCUITPY/`, syntax-check, copy, verify, commit, push:
  ```bash
  REPO=".../ubiss-2026-workshop-a"   # full path above
  "$REPO/../.venv/bin/python" -c "import ast; ast.parse(open('$REPO/robot/CIRCUITPY/code.py').read())"
  cp "$REPO/robot/CIRCUITPY/code.py" /Volumes/CIRCUITPY/code.py && sync
  cmp -s "$REPO/robot/CIRCUITPY/code.py" /Volumes/CIRCUITPY/code.py && echo OK
  ```
  The board **auto-reloads and RUNS code.py on every file save** (motors may move!).
  If `/Volumes/CIRCUITPY` isn't mounted, say so and wait — don't queue blind edits.
- **Observe:** tethered = Thonny serial REPL (only one app may hold the port);
  untethered = join WiFi `UBISS-Robot` (password is in the board's settings.toml,
  the team default), open http://192.168.4.1/.
- **Board → repo sync (new team files):** `rsync` from `/Volumes/CIRCUITPY/` into
  `robot/CIRCUITPY/` **excluding `settings.toml`** and dotfiles, then scan new files
  for secrets before committing.
- **Calibration discipline:** thresholds come from telemetry/measurement, not guesses.
  When you change one, note the evidence in a comment (existing comments show the style).

## Git rules (IMPORTANT)
- Remote: `https://github.com/usamarq/ubiss-2026-workshop-a.git`, branch `main`, **public repo**.
- Identity is a **local override**: `Usama Raheel <usamarq@users.noreply.github.com>`
  (personal account). The global gitconfig is the user's company identity — never use it
  here, never edit global config.
- **Do NOT add `Co-Authored-By: Claude` (or any Claude attribution) to commits.**
- Commit style: short imperative subject, evidence in body when tuning ("from telemetry run N").
- **Pull before you start each session** (`git pull --rebase`): the notes thread pushes to the
  same repo (different files: `lecture-notes/`, `readings/`, `exam-prep.md`).
- **File ownership:** you own `robot/`, `project/` implementation details, this file.
  Do not edit `lecture-notes/`, `readings/`, `exam-prep.md` (notes thread owns those).

## Task status & next steps
### Docking (Task 1) — homing DONE, endgame pending hardware
- Homing tested end-to-end: seek → early-lock → approach → reaches the phone. Fast.
- The docking state machine is already in code.py (hall watched during moves → stop →
  0.5 s settle → re-verify → LED → hold; boot self-check vs miswired hall).
- ~~get magnet~~ ✓ ~~verify hall~~ ✓ (GP27, MAGNET_DETECTED=True, one pole — see
  hardware truth) ~~flip DOCKING_ENABLED~~ ✓ deployed 2026-06-10.
- **TODO:** full-routine test (beacon at 9.28 Hz preset + magnet working-face-up at its
  base) → confirm LED on GP8 physically exists → measure hall trigger range for the
  funnel throat → build funnel + 1×1 cm target → full rehearsal from 3 starts.
  Scored: +10 full target coverage, −5 if indicator shown while moving (the settle
  logic guards this — don't weaken it). Run lasts ≥3 min: dock and HOLD.
### Environment mapping (Task 2) — scaffold written, blocked on contact sensor + shape exam
- Read `project/environment-mapping.md` first. Plan A implemented as `mapping_code.py`
  (see software state above): contact at a pose where no wall should be = obstacle;
  hug one lap; classify by turn distribution (≥2 bursts of ≥45° = triangle, dribbles =
  disk — classifier already passes synthetic-lap tests); report LED solid=disk /
  blink=triangle + telemetry.
- **Blocked on:** (1) a contact sensor — microswitch bumper preferred (stall is NOT
  software-detectable; IMU would need a driver, none in lib/); wire it, set
  `CONTACT_PIN`; (2) examining the physical shapes (sizes → `LANE_CM`; height/color may
  yield a cheaper discriminator); (3) instructor clarifications (wall-touching obstacle?
  exterior mods? pushing legal?). Magnet-drop loop closure is a noted option but
  odometry closure is the scaffold default.
- Deploy structure: code.py stays docking; copy mapping_code.py onto the board as
  code.py for mapping runs.

## Known pitfalls (learned the hard way)
1. Any motion code with pauses MUST keep the motor.py idle-resync fix.
2. rpm > 8 untested under load; 12 definitely stalls. Test with motor_test on battery first.
3. CircuitPython auto-reload runs code on save — robot moves immediately; wheels-up on desk.
4. Eject (`diskutil eject /Volumes/CIRCUITPY` or Finder) before unplugging.
5. The phone strobe app's preset must stay at the measured 9.28 Hz setting, or re-measure.
6. Public repo: no credentials, no instructor slide PDFs (they live outside the repo in
   `../reading_material/lecture_slides/`).

## Handover log (append entries here)
- **2026-06-10 (notes thread):** file created. Homing calibrated & working; docking awaits
  magnet; mapping analyzed, no code yet. Repo clean & pushed at this commit.
- **2026-06-10 (robot thread):** session start. Pulled (already up to date), repo verified
  against this file — all code.py tunables match, settings.toml untracked, identity correct.
  Board NOT mounted, so no deploy/board-sync this session. Added `mapping_code.py` scaffold
  (Plan A); classifier desktop-tested (4/4 synthetic laps). Docking unchanged, still awaiting
  magnet + hall_test. Note: `docking_code.py` (tracked) is the earlier standalone
  Thonny-runnable variant, superseded by code.py — kept as a fallback.
- **2026-06-10 (robot thread, board session):** board mounted, all 8 board files verified
  identical to repo. Neodymium magnets acquired. ⚠️ **Hall pin discrepancy found:**
  `hall_test.py` says the sensor is on the **GP10** connector (active-low), but code.py +
  this file said **GP27** / `MAGNET_DETECTED=True`. Serial baseline (motors stopped, both
  pins pulled up): **GP10 idles 1, GP27 idles 0** — something actively pulls GP27 low, so
  the two stories conflict; magnet watch will decide. Added `robot/tools/serial_exec.py`
  (drive the REPL from the desktop: interrupt code.py, exec a payload, stream prints —
  Thonny must NOT hold the port) + `robot/tools/payload_hall_watch.py` (watches GP10+GP27,
  prints transitions; also Thonny-runnable, DURATION defaults 60 s). User testing via
  Thonny. code.py NOT yet changed — awaiting magnet-watch verdict.
- **2026-06-10 (robot thread, hall verified):** user's Thonny hall_watch run settled it:
  **GP27 is the hall** (8 transitions, 4 clean magnet cycles, idle 0 → 1 on magnet,
  held solid, no bounce); **GP10 dead** (0 transitions). First ~29 s silent = first
  magnet face is the non-triggering pole (unipolar). Actions: `DOCKING_ENABLED = True`
  + verified-evidence comments in code.py; hall_test.py rewritten (was stale GP10/
  active-low); both deployed to board + cmp-verified; HANDOVER hardware truth updated.
  Next: full-routine test with beacon + magnet, confirm GP8 LED, measure trigger range.
