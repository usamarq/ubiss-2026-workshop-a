# Gridbots (live-coding demo)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 1 · Mon Jun 8 · Live coding demonstration · Fort TS128
> Status: 🟡 basics pre-filled

## TL;DR
A minimal robot living on a **discrete grid** — the simplest possible world that makes the information-space ideas concrete and codeable in an afternoon. Likely the scaffold the team project grows from.

## Key concepts
- **Grid world** — the environment is a finite set of square **cells** (like graph paper / a tile-based game).
- **State** `x` — which cell the robot is in (maybe + orientation). A **finite** set.
- **Actions** `u` — step to a neighbouring cell / turn. Finite.
- **Observations** `y` — simple discrete sensor readings ("wall ahead?", tile colour). Finite.

## Why a grid?
Everything is **finite**, so the abstract theory becomes something you can *watch on screen*:
- The robot's **belief** = a **set of highlighted cells** ("I'm somewhere in this clump") — a **nondeterministic I-state**.
- **Move** → the clump **spreads** (less certain). **Sense** → cells that don't match are **erased**, clump **shrinks**.
- That's the **predict/correct loop** made visible. ← this is the heart of `information-spaces`.

## Why it matters for *minimalism*
A grid strips a robot to its bones, so you can ask precisely *how little sensing/computation* solves a task — and measure it.

## Connections
- Discrete case of `readings/reading-04` (LaValle Ch.11, §11.1–11.2 are all discrete state spaces).
- Foundation for `information-spaces`, `filters-plans-and-reduction-algorithms`.

## 🎯 Likely exam points
- Map a gridbot to the formal pieces: state space `X`, action space `U`, observation space `Y`.
- Show how a set of possible cells updates under move (union) then sense (intersection).

## 📝 In-class notes (fill after lecture)
- _What did the demo actually build? API / functions / file structure:_
- _Did the team project build on this? How:_

## ❓ Open questions
-
