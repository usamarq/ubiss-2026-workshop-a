# Tray Tilting (sensorless manipulation)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Activity · Fort TS128
> Status: 🟡 basics pre-filled

## TL;DR
Tilt a tray in a **sequence of directions** and gravity slides a part into a **known orientation/position** — **with no sensors at all**. A classic, beautiful minimalism result: replace *sensing* with *mechanics*.

## Core ideas
- A part starts in an **unknown** pose → the I-state is the **set of all possible poses**.
- Each **tilt** is an *action* that maps that set forward (parts in many poses funnel toward the same resting configuration against a wall/corner).
- A well-chosen sequence of tilts **collapses the set to a single pose** — the part is now oriented, and you never measured anything.
- This is the **predict step** of an information space made physical, used as a **plan that needs no observations**.
- Historical antecedent: **Erdmann & Mason, "An exploration of sensorless manipulation" (1988)**; relates to part-feeders and "the power of mechanics."

## Why it matters for *minimalism*
The purest example of the thesis: a task that *seems* to need sensing (know the part's pose) is solved with **zero sensing** — just clever actuation + the geometry of the world.

## Connections
- Direct application of `information-spaces` (set of poses + predict step).
- Embodiment angle in `embodiment-x-minimalism` (the tray's walls do the "computation").

## 🎯 Likely exam points
- Explain how a tilt sequence reduces pose uncertainty without sensors.
- Frame tray tilting as an information-space plan (which step: predict, not correct).

## 📝 In-class notes (fill after lecture)
- _The specific activity / part / tilt sequence we worked through:_
- _Any formal model or assumptions stated:_

## ❓ Open questions
-
