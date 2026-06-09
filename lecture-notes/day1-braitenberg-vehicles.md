# Braitenberg Vehicles (hands-on, with rotations)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 1 · Mon Jun 8 · Activity · Fort TS128
> Status: 🟡 basics pre-filled

## TL;DR
Tiny robots with **sensors wired directly to motors** — no brain, no memory — that produce behaviour an observer reads as emotional/intentional. From Valentino Braitenberg's 1984 book *Vehicles*.

## The setup
Two light sensors on the front, two wheels. Wire each sensor straight to a motor. Two design choices give four "personalities":
- **Crossed vs. straight** — sensor drives the *opposite*-side or *same*-side wheel.
- **Excitatory vs. inhibitory** — more light *speeds up* or *slows down* the wheel.

| Wiring | Behaviour | Reads as… |
|---|---|---|
| straight + excitatory | turns away, speeds up | **Fear** 😨 |
| crossed + excitatory | turns toward, charges in | **Aggression** 😠 |
| straight + inhibitory | turns toward, slows, settles | **Love** 🥰 |
| crossed + inhibitory | drifts toward, then leaves | **Explorer** 🧭 |

## The big lesson
- **Law of uphill analysis & downhill synthesis** — it's *easy to build* complex-looking behaviour, but *hard to reverse-engineer* the mechanism from watching. Observers **over-attribute** intelligence/emotion.
- Maximum apparent behaviour from minimal mechanism → the minimalism thesis, on the **actuation/reactive** side.
- **"With rotations"** — the vehicles can turn/orient (differential-drive steering), which is what makes "turn toward/away" actually happen.

## Connections
- Sets up `illusions-observability-legibility` (Thu) directly.
- Historical antecedent of behaviour-based / reactive robotics.

## 🎯 Likely exam points
- Describe a Braitenberg vehicle and explain how wiring → behaviour.
- State the uphill-analysis/downhill-synthesis law and what it implies.

## 📝 In-class notes (fill after lecture)
- _What wiring did we try, on what hardware/sim? What emerged?_
- _Instructor's framing / extra examples:_

## ❓ Open questions
-
