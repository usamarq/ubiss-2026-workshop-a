# Information Invariants

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 4 · Thu Jun 11 · Lecture · Fort TS128
> Status: 🟡 basics pre-filled (lecture not yet attended — verify in class)

## TL;DR
A framework (Bruce **Donald**, *"Information Invariants in Robotics,"* 1995) for the **information requirements of tasks** and how you can **trade off** and **reduce** sensing, computation, and communication against one another.

## Key concepts
- Every task has an inherent **information requirement**; different robots/sensor suites can meet it in different ways.
- **Reductions between resources** — like complexity-theory reductions, you can **simulate** one sensor using another sensor + **computation** or **motion** or **communication**. This defines a notion of relative "sensor power" (links to `sensor-lattices`).
- **Trade-offs:** sensing ⇄ computation ⇄ communication ⇄ motion. Examples:
  - add **memory/computation** to replace a richer sensor;
  - add a **beacon / communication** to replace onboard sensing;
  - **move** the robot to gather info a static sensor couldn't.
- Goal: a principled measure of the **minimum information** a task needs — and proofs that one robot is *at least as powerful* as another.

## Why it matters for *minimalism*
This is the theoretical backbone of the whole workshop: it makes "how little is enough, and what can replace what?" a **formal, provable** question.

## Connections
- `sensor-lattices` (ordering sensors), `filters-plans-and-reduction-algorithms` (reductions), `information-spaces`.

## 🎯 Likely exam points
- State what an **information invariant** is.
- Give a concrete **sensing ⇄ computation/communication** trade-off.
- Explain "reduction between sensors" by analogy to complexity reductions.

## 📝 In-class notes (fill after lecture)
- _Donald's formalism as presented, examples, any hierarchy/diagram:_

## ❓ Open questions
-
