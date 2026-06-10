# Team Task 2 — Environment "Mapping" (disk vs triangle) 🟠🔺

> **Workshop A — Minimalism in Robotics** · UBISS 2026 · brief received Day 3 (Jun 10)
> Status: 🟢 analysis drafted — examine the physical shapes before locking a plan

## The brief
- Barricaded square arena **~120 × 120 cm**; robot starts **in a corner**; runs **autonomously for 5 minutes**.
- Exactly **one obstacle**: a **circular disk** OR a **triangle** (randomly selected for evaluation).
- At termination the robot **reports which case** via LEDs, sound, **wifi**, etc.
- The robot **may modify the environment non-destructively**; humans may NOT modify/affix anything to the **interior** (note: exterior not prohibited — clarify).
- The **shapes are available for examination** during development.
- **Scoring:** 5 points for correct identification; **bonus for elegant software/hardware design**.

## Information-space framing (use this language in the report — it IS the lecture)
- This is (in today's lecture's terms) a task whose **minimal sufficient I-space is tiny**: `{undecided, disk, triangle}` — but reaching a verdict requires **active information gathering** (move to sense).
- The two worlds differ by **one robust bit**: **corners / flat edges exist ⇔ triangle**; **smooth constant curvature everywhere ⇔ disk**.
- So the solution is a small **combinatorial filter** fed by geometric evidence, plus a motion strategy that generates that evidence. Frame it exactly like that for the elegance bonus.

## Our assets already in hand
- **Dead-reckoning odometry** (steppers count their own steps) → we can measure *how much we've turned and driven* with no added sensor.
- **Telemetry over WiFi** (allowed reporting channel!) + **LED on GP8** → reporting is done.
- **Magnet + hall** (from docking) → a clever **loop-closure trick**: the robot *drops the magnet* where it first touches the obstacle (a legal, non-destructive robot-made modification!), circumnavigates, and the hall sensor pinging again = "completed exactly one lap."
- Async motor framework, watchdog patterns, tested codebase.

## Plan A (recommended) — tactile circumnavigation + turn statistics 🐜
**Sensors: one contact bit + odometry. Maximally minimal, instructor-bait.**
1. **Find the obstacle.** From the corner, sweep the arena (e.g. boustrophedon / diagonal passes). Dead reckoning from the known corner start + known 120 cm walls ⇒ any contact at a pose where no wall should be = **the obstacle**. (Wall contacts also re-zero odometry drift — free recalibration.)
2. **Hug its boundary one lap** (bug-algorithm style: nudge–turn–advance with gentle contacts), optionally dropping the **magnet** at first contact for loop closure (or close the loop by odometry: returned to ~same x,y).
3. **Classify from the turning record** (pure odometry):
   - Going around any convex obstacle = **360° of total turning**, but its *distribution* differs:
   - **Triangle** → long straight stretches + **~3 concentrated turn bursts** (the corners).
   - **Disk** → turning **spread continuously** around the lap, no straight stretches.
   - Simple statistic: fraction of lap distance spent turning, or "number of turn bursts ≥ N steps". Threshold between the two is huge — robust.
4. At 5:00 (or earlier once confident): stop, **report** — LED pattern (e.g. solid = disk, blinking = triangle) + telemetry page banner.
- **Hardware ask:** a **microswitch bumper** (1 bit). Alternative with zero new parts: detect contact as an **IMU acceleration spike** (IMU is in the inventory) — or even photodiode-shadow at contact. Bumper is simplest and most reliable.
- **Risks:** wall-vs-obstacle confusion (mitigated by corner start + dead reckoning), odometry drift (mitigated by wall re-zeroing + magnet loop closure), pushing the obstacle accidentally (keep contact gentle; ask how heavy the shapes are).

## Plan B — ultrasonic sweep (non-contact) 📡
**Sensors: one ultrasonic ranger + odometry.**
- From 2–3 known poses, **rotate in place and record echo distance vs angle**.
- Physics does the classification: a **disk always presents a perpendicular patch** → strong echo from *every* direction. A **triangle's flat faces are specular** → strong echo only when a face is roughly perpendicular to the beam → **sparse, directional echoes**.
- Statistic: fraction of sweep angles with a valid echo (high → disk; sparse → triangle), or smooth vs kinked range profile.
- Faster (less driving), but ultrasonic multipath inside a small barricaded box can be noisy — bench-test against the real shapes first.

## Exploit-the-rules checklist (do these in the fort!)
1. **Examine the shapes** (explicitly allowed): do disk and triangle differ in **height, color/albedo, size, material, weight**? A cheap one-bit discriminator (e.g. "triangle is taller than the ultrasonic beam, disk is not", or different reflectivity to a photodiode+LED at close range) could make the solution almost trivial — *measure before engineering*.
2. **Exterior modification** — the ban is on the *interior*; ask whether mounting anything on/outside the walls is legal (e.g. a beacon for localization).
3. **Robot-made modifications are legal** — magnet-drop loop closure; could also lay **colored tape** as breadcrumbs.
4. Ask: is the obstacle's **position/orientation random**? Always the **same physical shapes**? Can it **touch a wall** (a triangle flush against a wall hides an edge)?
5. Clarify "non-destructive": is **gently pushing** the obstacle allowed? (A disk slides/rotates differently than a triangle — pushing is itself a sensor!)

## Report-out framing (for the elegance bonus)
> "We reduced the task to its minimal sufficient information space — three I-states — and built the coarsest filter that fills it: one contact bit + the robot's own step counts. The body and the motion strategy do the sensing; the classifier is a turn-distribution statistic. No camera, no ranging, no map."
(If Plan B: "ultrasonic specularity makes the *physics* classify the shape.")

## Open questions / to confirm
- Shape dimensions, heights, materials, weights (examine!).
- Obstacle placement rules (random? touching walls?).
- Exterior-modification legality; pushing legality.
- Wall height/material (matters for ultrasonic + any external beacon idea).

## Decision log
- **Jun 10** — brief analyzed; Plan A (tactile + odometry statistics, magnet loop-closure) recommended; Plan B (ultrasonic specularity) as the non-contact alternative; examine-the-shapes checklist drafted.
