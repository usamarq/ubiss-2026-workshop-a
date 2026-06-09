# Sensor Lattices & Comparing Robots

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture · Fort TS128
> Status: 🟡 basics pre-filled

## TL;DR
A formal way to ask *"which robot senses more?"* Sensors are ordered by how finely they **partition** the state space (their preimage resolution); that ordering forms a **lattice**, letting you compare robots and hunt for the **minimal sufficient sensor**.

## Key concepts
- A sensor induces a **partition** of `X` via its preimages `H(y)` (see `information-spaces`).
- **Refinement order:** sensor A **dominates** B if A's partition is *finer* (A distinguishes everything B does, and more). This is a **partial order**.
- The set of partitions/sensors under refinement forms a **lattice** (with meet/join):
  - **Top** = finest = perfect information (bijective/identity sensor).
  - **Bottom** = coarsest = no information (null sensor).
- Comparing robots = locating their sensors in this lattice. "More powerful" = higher in the lattice.
- **Minimal sufficient sensor** = the *coarsest* sensor still high enough to solve the task.

## Why it matters for *minimalism*
This turns "use a simpler sensor" into a precise, comparable claim — and gives **metrics** for the complexity-dimensions objective. You can prove one robot needs *at least* as much sensing as another.

## Connections
- Built directly on **preimages/partitions** from `information-spaces`.
- Feeds `information-invariants` (reductions between sensing resources).

## 🎯 Likely exam points
- Define the refinement (dominance) order on sensors; give finest/coarsest extremes.
- Explain how a sensor lattice lets you compare two robots and find a minimal sensor.

## 📝 In-class notes (fill after lecture)
- _Formal definitions / lattice diagrams from class:_
- _Worked comparison example:_

## ❓ Open questions
-
