# Co-Design

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 4 · Thu Jun 11 · Lecture · Fort TS128
> Status: 🟡 basics pre-filled (lecture not yet attended — verify in class)

## TL;DR
Design the robot's **body and its sensing/controller together (jointly)**, not one after the other — because a choice in one changes what the other needs.

## Key concepts
- **Sequential design** (pick body → then design brain) is usually **suboptimal**; the body constrains/enables the controller and vice-versa.
- **Body ⇄ brain trade-off** (from `embodiment-x-minimalism`): a cleverer body needs simpler sensing/control, and conversely.
- **Monotone co-design (Andrea Censi)** — a formal framework: design components have **functionality provided** vs **resources required**, composed into a network; solving it yields the **Pareto-optimal** trade-off frontier (no single best — a frontier of non-dominated designs).
- Sensor choice itself is a co-design decision (which sensor to include ↔ what the controller must do) — links to `sensor-lattices`.

## Why it matters for *minimalism*
Minimal robots usually come from **co-design**: you reach the simplest overall system only by trading body against brain *together*, not optimizing each alone.

## Connections
- `embodiment-x-minimalism`, `sensor-lattices`, `information-invariants`.

## 🎯 Likely exam points
- Define co-design; explain why **joint** design beats **sequential**.
- Mention monotone co-design / a **Pareto frontier** of designs.

## 📝 In-class notes (fill after lecture)
- _Framework/notation shown, examples, the team-project link:_

## ❓ Open questions
-
