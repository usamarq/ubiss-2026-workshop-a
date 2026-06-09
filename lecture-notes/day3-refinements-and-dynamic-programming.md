# Refinements & Dynamic Programming (approximate info spaces)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Lecture · Fort TS128
> Status: 🟡 basics pre-filled (lecture not yet attended — verify in class)

## TL;DR
Once a task lives in an information space, you can **plan** in it. Because *"the I-space is just another state space,"* standard tools like **dynamic programming** apply — but exact I-spaces are enormous, so you work in **approximate / derived** I-spaces and **refine** as needed.

## Key concepts
- **DP over I-states** — compute a **cost-to-go** (value) for I-states by **backward induction / value iteration**; act greedily w.r.t. it. A plan is `π : I → U`.
- **"I-space is just another state space"** — converting `X` (imperfect info) → I-space gives a space where the state (the I-state) is *always known*, at the cost of a **larger** space.
- **Curse of dimensionality** — the history I-space grows without bound; nondeterministic I-space is `pow(X)` (exponential). Exact DP is usually **intractable**.
- **Approximate information spaces** — use a coarser **derived I-map** (lossy compression) so DP is feasible; accept some loss of optimality.
- **Refinement** — selectively make the I-map **finer** where coarseness breaks the task (vs. `sensor-lattices` refinement of partitions).

## Why it matters for *minimalism*
The right approximate I-space is the **minimal representation** that still supports a good plan — the same "how coarse can I go?" question, now for *computation*.

## Connections
- Builds on `information-spaces`; pairs with `filters-plans-and-reduction-algorithms`.
- Source: `readings/reading-04` (and LaValle Ch.12 for continuous DP).

## 🎯 Likely exam points
- Explain DP / cost-to-go over I-states.
- Why is exact planning in the I-space intractable, and what does "approximate I-space" buy you?

## 📝 In-class notes (fill after lecture)
- _Algorithm(s) shown, notation, any worked example:_

## ❓ Open questions
-
