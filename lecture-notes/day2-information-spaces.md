# Information Spaces ⭐

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture + "Information space practice" activity · Fort TS128
> Status: 🟡 basics pre-filled — **the central topic of the workshop**

## TL;DR
A robot usually **can't know its exact state** — only noisy sensor readings + the actions it took. Instead of estimating the state, you reformulate the whole task in terms of **what the robot can *know***. That arena of knowability is the **information space (I-space)**. Many tasks can be solved *without ever knowing the exact state* — which is what lets you use a simpler, cheaper robot.

## Key concepts
- **State `x ∈ X`** — the (hidden) truth.
- **Sensor mapping `y = h(x)`** and the **preimage** `H(y) = { x : h(x)=y }` — the set of states consistent with reading `y`. Preimages **partition** `X` = the sensor's **resolution**. (Identity sensor → singletons; null sensor → all of `X`.)
- **History I-state** `η_k = (η₀, actions u₁…u_{k-1}, observations y₁…y_k)` — everything known so far. Always known, but **grows without bound**.
- **Plan** is a function of the I-state, `π : I → U` (you can't act on `x` — you don't have it).
- **Derived I-spaces** (compress the unwieldy history via an **I-map**):
  - **Nondeterministic I-state** = a **set** `X_k ⊆ X` ("all states I could be in"; no probabilities).
  - **Probabilistic I-state** = a **distribution** `P(x)` (a belief — same as a Bayes filter / POMDP belief).
- **Sufficient I-map** — a compression you can update from *only* the current derived I-state + last action + new observation (a "sufficient statistic"); lossless for decision-making.

## The predict/correct update (the heartbeat)
| Step | Nondeterministic (sets) | Probabilistic (distributions) |
|---|---|---|
| **Predict** (after action `u`) | union `⋃ F(x,u)` over the set → set **grows** | marginalize `Σ P(x'|x,u)P(x)` |
| **Correct** (after obs `y`) | intersect with `H(y)` → set **shrinks** | Bayes: `∝ P(y|x)·P(x)` |
| **Goal** | drive the set into `X_G` | e.g. `P(x) > ½` |

**Analogy:** lost in your dark house. Your "shortlist of where I am" *spreads* when you take a step and *shrinks* when you feel a landmark.

## Why it matters for *minimalism*
Designing a minimal robot = choosing **how coarse an I-space you can get away with** and still solve the task. Coarser → simpler/cheaper robot. The art is the coarsest I-space that still works.

## Connections
- `readings/reading-04` (LaValle Ch.11) is the source text.
- `tray-tilting` = predict step with **no sensing**. `sensor-lattices` = ordering sensors by their preimage resolution. `filters-plans-and-reduction-algorithms` = computing/compressing I-states.

## 🎯 Likely exam points
- Define I-space; give example sensors + preimages.
- Run a predict/correct update by hand (nondeterministic and probabilistic).
- Contrast nondeterministic vs probabilistic I-states; define a sufficient I-map.

## 📝 In-class notes (fill after lecture)
- _Information space practice activity — what problem, what did we compute:_
- _Instructor's notation / examples / emphases:_

## ❓ Open questions
-
