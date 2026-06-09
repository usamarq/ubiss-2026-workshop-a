# Information Spaces ⭐ (Lecture)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture + "Information space practice" · Fort TS128
> Status: 🟢 in-class notes added (Jun 9) · **the core topic**
>
> 🧮 = beginner math explainer · **⟵ reconcile w/ slides** = I inferred this, cross-check when the slides are added.

## TL;DR
A robot can't see its true state — only its **observations** and the **actions** it took. Instead of estimating the state, we reformulate the task over **what the robot can know**: the **information space (I-space)**. "Information" here is the **game-theory** sense (an *information set* of indistinguishable possibilities), **not** Shannon's bits/entropy.

---

## 1 · Setup — the robot, time, and two sets
A robotic system interacts with the physical world. Two basic sets:
- **`Y`** — the set of all possible **observations** (sensor readings).
- **`U`** — the set of all possible **actions** the robot can take.

Interaction happens in **discrete time**, indexed by a **stage** `k = 1, 2, 3, …`.

> 🧮 **What is "stage / time k"?** Time isn't a smooth flow here — the robot acts in a sequence of steps, like turns in a board game. `k` simply counts them: stage 1, stage 2, …. At each stage `k` the robot gets an observation `y_k ∈ Y` and applies an action `u_k ∈ U`.
> (`y_k ∈ Y` reads *"y_k is an element of Y"* — i.e. `y_k` is one particular reading out of all the possible ones in `Y`.)

**Maximal information space** — the richest possible bookkeeping: keep *everything* the robot could know. Everything else we do is *deliberately throwing some of it away* to get something smaller and usable. **⟵ reconcile w/ slides**

---

## 2 · What "information" means here (NOT Shannon!)
- ❌ **Not** Shannon information theory — no bits, entropy, channel capacity, or "noisy information" in that sense.
- ✅ **Yes** — "information" as an **information set** from **game theory** (von Neumann & Morgenstern, *Theory of Games and Economic Behavior*), specifically **games with hidden / imperfect information**.

> 🧮 **Information set (the key analogy).** In a card game you can't see your opponent's hand — you only know you're in *one of several* situations consistent with what you've observed. That set of indistinguishable possibilities is your **information set**. A robot is identical: from its readings it knows only that the world is in *one of a set* of possible states. **That set is the information state.**

---

## 3 · History Information Space (History I-space)
As it runs, the robot accumulates a **history**: the actions it took and observations it saw.
- The **History I-space** = the **set of all finite-length histories** the robot could ever have.

> 🧮 **What's a "history"?** Just the ordered log so far: `(u₁, y₁, u₂, y₂, …)` up to stage `k`. *"Finite-length"* = the log has some finite number of entries (you've only run `k` steps). The History I-space is the set of *every possible such log*.

**Problem:** the history **grows forever** — one entry longer every stage. So: *how much of it do we actually need?* Ways to **compress** it (each keeps less, hoping it's still enough):
1. **Discard everything up to `y_k`** — keep only the **latest observation**.
2. **Keep only the stage `k`** — just "what step am I on," nothing else.
3. **Refer to a model of the physical world** — use the model to fold the whole history into a compact **state estimate**.

> A compression that keeps *enough* to still act correctly is called **sufficient** (it loses nothing that matters for the decision). The art of minimalism = compress as hard as possible while staying sufficient.

---

## 4 · Running example — the Colored Grid World 🎨
- A **4×4 grid**. Each cell is colored **red, blue, green, or black**. The robot is a **yellow disk** at position `(i, j)`.
- `(i, j) ∈ {0,1,2,3} × {0,1,2,3}`.

> 🧮 **The "×" (Cartesian product).** `A × B` = the set of all ordered pairs `(a, b)` with `a` from `A` and `b` from `B`. So `{0,1,2,3} × {0,1,2,3}` = all 16 coordinate pairs `(0,0), (0,1), …, (3,3)` — the 16 cells.

**Key twist:** the **grid coloring can be anything** — the physical world is *unknown*, so the state has to include *which coloring* it currently is.

> 🧮 **How big is the state space `X`?** Each of the 16 cells is 1 of 4 colors → `4¹⁶ = 4,294,967,296 ≈ 4.3 billion` colorings. Times the 16 robot positions ≈ **69 billion** states. Far too many to track exactly — which is *precisely why* we reason with information **sets** instead of exact states.

---

## 5 · Sensors → Preimages, Equivalence Classes, Partitions
A **sensor** is a mapping `h : X → Y` — it reads the state and returns an observation.

> 🧮 **"Mapping / function `h : X → Y`."** A rule taking any state `x` and giving exactly one reading `y`. Crucially, *many different states can give the same reading* — that's the source of the robot's uncertainty.

**Example sensor — a red-detector**: `Y = {0, 1}`
```
h(x) = 1   if the cell under the robot is red
h(x) = 0   otherwise
```

The **preimage** of a reading `y` is *every state that would produce it*:
```
h⁻¹(y) = { x ∈ X : h(x) = y }
```

> 🧮 **Preimage — don't panic at the `⁻¹`.** It is **not** "1 over h" and **not** a true inverse function. `h⁻¹(y)` just means *"the set of all inputs that map to y"* — read it as *"everything that could have caused reading y."* The braces `{ x ∈ X : … }` read *"the set of all x in X such that …"* (the colon `:` = "such that").

**✅ Answers for the red-detector:**
- `h⁻¹(1)` = **all states where the cell under the robot is red** — every (coloring, position) with a red cell beneath the disk.
- `h⁻¹(0)` = **all states where that cell is *not* red** — i.e. it's blue, green, or black.

These two preimages are **disjoint** (no overlap) and together cover **all of `X`** → they **partition** `X` into two pieces.

> 🧮 **Equivalence classes & partition.** Declare two states "the same" when the sensor can't tell them apart: `x ∼ x′` exactly when `h(x) = h(x′)`. Each group of look-alike states is an **equivalence class** (here just two: red-underfoot vs not). A **partition** = slicing a set into non-overlapping pieces that together cover the whole — like cutting a pizza. **Each preimage is one slice**, and a reading tells the robot *which slice* it's in. That slice **is** its information state.

### What if the grid is *continuous*? (cell values in `[0, 4]`)
Suppose a cell's "color" isn't 1 of 4 discrete labels but **any real value in the interval `[0, 4]`**.

> 🧮 **Discrete vs continuous.**
> - *Discrete* = you can **list / count** the options (4 colors, 16 cells — countable, even if huge).
> - *Continuous* = **uncountably** many values between any two points; you simply can't list them.
>
> Consequences:
> - `X` becomes a **continuous region**: each cell ∈ `[0,4]`, 16 cells → the 16-dimensional cube `[0,4]¹⁶`.
> - "Red" becomes an **interval**, say `[r₁, r₂] ⊂ [0,4]`. Then `h⁻¹(1) = { x : cell value ∈ [r₁, r₂] }` — an **uncountable region**, not a countable list.
> - You stop **counting** states and start measuring **lengths / areas / volumes**; probabilities come from **integrating** a density rather than summing. The partition is now into continuous **regions** instead of discrete buckets.

---

## 6 · Two kinds of Information State
Given its reading-history, what does the robot actually *hold*? Two choices:

### (a) Nondeterministic / possibilistic I-space
- An I-state is just a **subset of the physical state space**, `X_k ⊆ X` — *"I'm in one of these states,"* with **no probabilities**.
- It's literally a preimage (or an intersection of preimages) — a plain **set of possibilities**.

> 🧮 **`⊆`** = "is a subset of": every element of `X_k` is also in `X`. The I-state is a *chunk* of `X`.

### (b) Probabilistic I-space
- An I-state is a **probability distribution over `X`** — instead of just "possible / impossible," each state gets a **likelihood**.

> 🧮 **Probability distribution.** A function `P` assigning each state a number `≥ 0`, with all of them **summing to 1** (discrete) or **integrating to 1** (continuous). It's a *graded* belief — "70% here, 30% there" — versus the nondeterministic "could be either." (Same idea as a Bayes-filter / POMDP belief.)

---

## 7 · How information states evolve (actions, transitions, disturbance)
- `U` = the set of **actions**.
- The world changes via a **transition function** `f : X × U → X`: given the current state and an action, it returns the next state.

> 🧮 **`f : X × U → X`.** Input = a pair *(current state, action)*; output = the *next state*. E.g. *(at cell (1,1), move right)* → *(at cell (1,2))*.

- **Disturbance / imperfect world:** the real world isn't clean — "nature" perturbs things. Model it by adding a **disturbance** `θ` from a set `Θ`:  `f : X × U × Θ → X`. Now the *same* `(x, u)` can lead to *several* possible next states. Write `F(x,u) = { f(x,u,θ) : θ ∈ Θ }` for that **set** of possible next states.

> 🧮 **Why disturbance matters.** Because the next state isn't unique, after acting the robot is unsure where it landed → its information **set grows** (the **predict** step). A fresh sensor reading then **shrinks** it (the **correct** step).

**The update loop — the central mechanism:**

| Step | Nondeterministic (sets) | Probabilistic (distributions) |
|---|---|---|
| **Predict** — apply action `u` | pool all reachable states → set **grows** | spread the belief through the motion model |
| **Correct** — see observation `y` | keep only consistent states → set **shrinks** | re-weight the belief by the sensor model (Bayes) |

The actual formulas (kept out of the table so the `|` bars read cleanly):
- **Nondeterministic predict:** `X′ = ⋃ₓ F(x,u)` over all `x` in the current set.
- **Nondeterministic correct:** `X′ ← X′ ∩ h⁻¹(y)`.
- **Probabilistic predict:** `P′(x′) = Σₓ P(x′ | x,u) · P(x)`.
- **Probabilistic correct (Bayes):** `P(x | y) = P(y | x) · P(x) / Σₓ P(y | x) · P(x)`.

> 🧮 **The symbols.** `⋃` (union) = "throw all these sets together into one." `∩` (intersection) = "keep only what's in *both*" — here, states both reachable **and** consistent with the reading. `Σ` (sigma) = "add up over all current states." `P(x′ | x,u)` reads "probability of next state `x′` **given** current `x` and action `u`."
> 🧮 **Bayes' rule** turns *"chance of this reading if I were in state x"* into *"chance I'm in state x given the reading."* Numerator = (likelihood of the reading from `x`) × (how likely `x` was already); the denominator just **re-normalizes** so the new probabilities sum to 1.

---

## Connections
- Source text: `readings/reading-04` (LaValle Ch. 11). The grid example is the **discrete** case (`gridbots`).
- `tray-tilting` = the **predict** step with *no sensing*. `sensor-lattices` = ordering sensors by how finely their preimages **partition** `X`. `filters-plans-and-reduction-algorithms` (Wed) = computing & compressing I-states.

## 🎯 Likely exam points
- Define `Y`, `U`, stage `k`; explain why "information" here ≠ Shannon (it's an **information set**).
- Define the **history I-space**; give ways to compress it (latest `y_k` / stage `k` / world-model estimate).
- Given a sensor, write its **preimages** `h⁻¹(y)` and the **partition** they induce — e.g. do it for the red-detector.
- Contrast **nondeterministic** (subset of `X`) vs **probabilistic** (distribution over `X`) I-states.
- Write the transition `f : X × U (× Θ) → X` and run **one** predict/correct update by hand.

## 📝 In-class notes (raw — Jun 9)
- System interacts w/ physical world; sets `Y`, `U`; discrete time, stage `k`; "maximal information space."
- Information = info **set** (von Neumann–Morgenstern, imperfect-info games), **not** Shannon / noisy info.
- History I-space = all finite histories; compress by keeping only `y_k`, only `k`, or a world model.
- Colored Grid World: 4×4, cells red/blue/green/black, robot = yellow disk, `(i,j) ∈ {0,1,2,3}²`; grid can be anything.
- Preimages / equivalence classes / partition; red-only sensor, `h⁻¹(1)` & `h⁻¹(0)`.
- Continuous grid: values in `[0,4]`.
- Nondeterministic / possibilistic I-space = subsets of `X`; `U` actions; `f : X×U`; states evolve; disturbance / imperfect world; probabilistic I-space.

## 📎 Slides
_Drop the lecture slides in [`../slides/`](../slides/) (e.g. `information-spaces.pdf`) and tell me — I'll **reconcile** these notes against them, especially the items flagged **⟵ reconcile w/ slides**._

## ❓ Open questions
- Exact definition of **"maximal information space"** as used in the lecture.
- Were the formal **predict/correct equations** given, or just the intuition?
- In the continuous case, exactly how was "red" defined as a subset of `[0,4]`?
