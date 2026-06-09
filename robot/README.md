# Robot — CircuitPython code (backup & study)

The Workshop A robots are **Raspberry Pi (RP2040 / Pico-class) microcontrollers running CircuitPython**.
When connected via USB they mount as a drive named **`CIRCUITPY`** holding `code.py` + a `lib/` folder.

## Purpose of this folder
A version-controlled **backup and study copy** of the code that lives on the robot, so that:
- the work survives a flash wipe / firmware reflash,
- every change is tracked across the week,
- the code can be read and annotated off-robot.

## Planned layout (filled once the robot is connected)
```
robot/
├── CIRCUITPY/        # mirror of the board's drive (code.py, lib/, boot_out.txt, ...)
├── boot_out.txt      # board + CircuitPython version — identifies the exact hardware
└── notes.md          # what the code does, pin map, gotchas
```

## Backup workflow (run when the robot is plugged in)
1. Confirm the drive name: `ls /Volumes/CIRCUITPY`
2. Mirror it here (excluding macOS cruft):
   ```bash
   rsync -av --exclude '.Trashes' --exclude '.fseventsd' --exclude '.metadata_never_index' \
     /Volumes/CIRCUITPY/ robot/CIRCUITPY/
   ```
3. Copy `boot_out.txt` up a level and commit the snapshot.

> ⚠️ The robot runs **CircuitPython**, not the desktop `.venv`. Libraries go in the board's
> `lib/` (manage with `circup`), **not** via `pip`. Editing `code.py` on the drive and saving
> auto-restarts the program. Eject the drive before unplugging.

_Status: 🟡 scaffold only — actual code import pending robot connection._
