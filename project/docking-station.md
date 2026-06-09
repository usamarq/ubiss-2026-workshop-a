# Team Project — Docking Station Design 🔌

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Task: design a **docking station** for our CircuitPython robot.
> Goal: a *unique, minimal* approach using the **resources & sensors we already have**.
> Status: 🟠 gathering constraints & resource inventory

## Problem statement
Design a docking station the robot can reliably **reach → align with → connect to**.
_(Refine once the brief is in: what does "docking" actually achieve — charge? park? home? align for data?)_

## Constraints (to fill — from the session)
- [ ] What docking must accomplish (charge / park / align / …)
- [ ] Arena / environment (size, surface, lighting, walls, markers)
- [ ] What marks the station, and how the robot may perceive it
- [ ] Allowed modifications (may we add passive structures? funnels? markers? beacons?)
- [ ] Time / power / cost / build limits
- [ ] Success criteria (how is "docked" judged? reliability target? repeatable from any start?)
- [ ] What "unique" is expected to mean (novelty? minimal sensing? robustness? cost?)

## Available resources & sensors (to fill — ⚠️ CRITICAL)
_A minimal design depends **entirely** on what hardware we actually have._
- [ ] Robot board + CircuitPython version (`boot_out.txt`)
- [ ] Sensors — e.g. colour/reflectance, IR, distance/ToF, bump/contact switches, wheel encoders, IMU, light
- [ ] Actuators — motors/wheels (differential drive?), servos
- [ ] Onboard libraries (`lib/`) + what the current `code.py` already does
- [ ] Station-side parts available — LED/IR beacon, magnets, charging contacts, physical guides/rails

> 💡 I can inventory most of this **automatically** when the robot is plugged in
> (read `boot_out.txt`, `code.py`, and `lib/`) — see [`../robot/`](../robot/README.md).

## Minimalism lenses to apply (straight from the workshop)
When we design, deliberately ask **"how little is enough?"**:
- **Embodiment / passive alignment** — a physical **funnel / V-guide** so docking needs *no precise sensing* (the tray-tilting lesson: replace sensing with mechanics). The walls do the work.
- **Single-sensor homing** — can *one* cheap sensor + motion suffice? (Braitenberg-style "drive toward the beacon".)
- **Information-space view** — what is the **minimal information** the robot needs to *know* it's docked? Model the approach as a shrinking set of possible poses (predict / correct).
- **Resource trade-offs** (information invariants) — replace a sensor with a **wall-follow**, a **marker**, or a **mechanical guide**; trade sensing ⇄ computation ⇄ structure.

## Candidate approaches
_I'll draft 2–3 distinct options once constraints + inventory are in, then we compare and pick._

## Decision log
- _date — what we chose and why_

## Open questions
-
