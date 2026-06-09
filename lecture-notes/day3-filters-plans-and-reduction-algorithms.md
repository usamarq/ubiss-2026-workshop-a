# Filters, Plans & Reduction Algorithms

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Lecture · Fort TS128
> Status: 🟡 basics pre-filled (lecture not yet attended — verify in class)

## TL;DR
A **filter** keeps track of what's known (maps observations → a derived I-state); a **plan** decides actions from I-states; **reduction algorithms** shrink a filter to the **fewest states** that still do the job — often a **computationally hard** problem. This lecture is the crux of objectives #4 (filtering vs planning) and #5 (intractable reductions).

## Key concepts
- **Filter** — updates a derived I-state from each new observation/action. Flavours:
  - **Probabilistic** (Bayes / **Kalman**) — distribution over states.
  - **Nondeterministic** — set of possible states.
  - **Combinatorial filter** — a **finite automaton** over discrete I-states (edges = observations). Minimal memory, no probabilities.
- **Plan** — `π : I → U`, a mapping from I-states to actions.
- **Filtering vs planning** ⚖️
  - *Filtering* = **passive**: maintain knowledge from incoming data (estimation-like).
  - *Planning* = **active**: choose actions to reach a goal.
  - Both live over the I-space; a plan typically consumes a filter's output.
- **Reduction / minimization** — find the **smallest** filter with the same behaviour. **Combinatorial filter minimization is NP-hard** (O'Kane & Shell). Less memory = more minimal robot.

## Why it matters for *minimalism*
The smallest sufficient filter = the **least memory/computation** a robot needs to act correctly. Reduction algorithms are *literally* "make the robot simpler."

## Connections
- `information-spaces` (filters compute I-states), `refinements-and-dynamic-programming`, `sensor-lattices`.

## 🎯 Likely exam points
- **Contrast filtering and planning** (passive vs active; both over the I-space).
- Define a combinatorial filter; explain why minimizing it is hard (NP-hard).

## 📝 In-class notes (fill after lecture)
- _Filter example(s), the reduction algorithm shown, complexity claims:_

## ❓ Open questions
-
