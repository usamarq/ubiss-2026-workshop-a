# Team Project — Docking Station Design 🔌

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Goal: a *unique, minimal* docking approach using the resources & sensors we have.
> Status: 🟢 brief + sensor inventory in hand (Jun 9) — analysis drafted

## The brief (from the activity doc)
**You need to:**
1. Design a docking station that includes a **"target mat"**.
2. Target dimensions: **no larger than 9×9 cm, no smaller than 1×1 cm**.
3. The robot starts **≥ 1 m away** from the target (measured on the plane), at a **random orientation**.
4. The robot must have a **termination indicator** it triggers when docked (e.g. sound, LED).

**Scoring** — from **3 distinct start locations**; a run lasts until the first moment the indicator shows *and the robot is stationary*, **or 3 minutes, whichever is longer**:
- **+10** — successfully docked: target **100% obscured** by the gridbot's base.
- **+2½** — covered a non-zero area of the target, but **< 100%**, at termination.
- **+1** — not covering at termination, but covered *some* part at *some* point during the run.
- **−5** — indicator displayed **while the robot was moving**. ⚠️

**Round 1:** *no constraints on modifying the environment or robot*; we provide six starting locations.
**Meta:** instructors floated **"pricing" resources** (raising prices once a solution is found) → fewer/cheaper resources is rewarded. **Prizes:** most creative / minimal / maximal / most robust / most adaptable / best failure.

## Available resources & sensors (confirmed)
`photodiode` · `colour sensor (gesture)` · `IMU` · `camera` · `ultrasonic` · `colored tape` · `magnets + hall-effect sensors` · `speaker + microphones`
_(Assumed: a differential-drive wheeled gridbot with a flat base — **confirm actuators / base size**.)_

## Strategy — where the points actually are
- 🎯 **Make the target the MINIMUM size, 1×1 cm.** *You* design the mat. A tiny target is trivial to obscure 100% with the robot's base → maximizes the +10; a 9×9 cm target would demand near-perfect alignment. Do the **homing with a larger structure** that funnels down to the tiny target.
- 🛑 **Never signal while moving (−5).** Trigger only after the robot is *verifiably* stationary. A magnetic latch makes "stationary" automatic; confirm with the **IMU** (≈0 motion) before signaling.
- 🔒 **Dock and HOLD.** The run lasts ≥ 3 min ("whichever is longer"), so the robot must *stay* docked and still with the indicator on — no drift, no re-trigger. A **magnet** keeps it put.
- 🌀 **Random far start → need orientation-independent *coarse* homing** + **mechanical *fine* alignment** so no precise sensing is required at the end.

## ⭐ Recommended approach — "Beacon-homed magnetic funnel dock"  *(minimal · robust · creative)*
A 4-stage pipeline that replaces precise sensing/computation with **physical structure** — the tray-tilting lesson applied to docking:

1. **Coarse homing — Braitenberg light-seek.** Put an **LED beacon** on the dock and two **photodiodes** on the robot wired "steer toward the brighter side." From any orientation ≥1 m out, the robot turns toward and approaches the dock with almost no computation. *(Audio variant: dock plays a tone, home in with the **microphones**.)*
2. **Capture — physical funnel.** A V-shaped **funnel / guide rails** (built from **colored tape** walls or low strips — allowed in Round 1) at the dock mechanically channels the robot into the throat, absorbing approach-angle error. **The walls do the aligning — zero sensing.**
3. **Align + hold — magnet.** A **magnet** on the robot base mates a magnet at the funnel throat → snaps to the exact docked pose and **holds it stationary**.
4. **Detect + terminate — hall-effect + IMU.** The **hall-effect sensor** detects magnet engagement (a clean 1-bit "docked"); confirm the **IMU** reads ≈0 motion; then fire the **speaker/LED**. The **1×1 cm target** at the throat is now 100% under the base → **+10**, and the magnet keeps it docked & still for the whole run.

**Why it fits the workshop:** minimal *information* (one hall-effect bit to know you're done), minimal *computation* (reactive light-seek — no map, no planner), and **embodiment doing the work** (funnel + magnet = sensorless final alignment). Targets the **"minimal," "most robust,"** and **"most creative"** prizes, and stays cheap if resources get "priced."

## Alternative approaches (comparison / fallback)
- **B · Colour-trail line-follow (single sensor).** Lay **colored tape** from a wide catchment down to the tiny target; the robot spiral-searches until the **colour sensor** hits the tape, then follows it in; a distinct target colour = "arrived." Simpler, but final coverage is less guaranteed → pair with a small funnel. Good fallback if **magnets are banned** in a later round.
- **C · Vision homing — the "maximal" entry.** Use the **camera** to detect a marker and servo precisely onto the target. Heavy compute/precision (opposite of minimal) but could win the **"maximal"** prize — higher risk (lighting, compute, the −5 trap).
- **Cross-round robustness:** keep **photodiode beacon-homing** as the orientation-independent core; if later rounds forbid modifying env/robot, degrade gracefully to B (tape) or C (camera).

## Open questions / to confirm
- Robot **actuators** (differential drive?) + **base shape/size**, and whether we may mount a magnet + photodiodes.
- Are **active dock emitters** (LED / audio beacon) allowed, or only *passive* marks? (Decides the coarse-homing method.)
- **Round 2+ constraints** — the brief image cut off after "Round 1"; how much modification gets restricted later?
- The "**six starting locations**" we must provide — choose ones that showcase orientation-independence.

## Decision log
- **Jun 9** — drafted strategy + 3 approaches; leaning **"beacon-homed magnetic funnel"** (minimal + robust). Tiny 1×1 cm target chosen to guarantee 100% coverage.
