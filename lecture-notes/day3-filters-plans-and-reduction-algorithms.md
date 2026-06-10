# Filters, Plans & Reduction Algorithms

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Lecture · Fort TS128
> Status: 🟢 in-class notes added (Jun 10) · user missed the first minutes · **slides pending** → ⟵ flags
> 🧮 = beginner explainer — this note is deliberately gentle. (Research area of **O'Kane & Shell**.)

## TL;DR (the whole lecture in four sentences)
A **combinatorial filter** is a tiny machine — circles and arrows — that tracks what a robot knows. Smaller filter = less memory = more minimal robot, so we want to **shrink (reduce) filters** by **merging** states. The shock result: although these look exactly like the automata of classic CS (which are easy to minimize), **finding the smallest filter is NP-hard** — provably "computationally nasty." The escape hatches: **special structures** (no-missing-edges, unitary, once-appearing observations) where shrinking becomes easy, and **fixed-parameter tractability** (fast when some parameter of the problem happens to be small).

---

## 1 · What you (probably) missed at the start: the combinatorial filter
A **combinatorial filter** is a finite-state machine for tracking knowledge:
- **Circles** = I-states ("what I currently know").
- **Arrows** = observations ("when you see `y`, move along the `y` arrow").
- Each circle carries an **output** — the filter's current answer (a color/label).
- No probabilities anywhere — pure structure. ("Combinatorial" ≈ "discrete, no numbers.")

> 🧮 **Example — the parity filter (from lecture 1).** Task: report whether you've passed an even or odd number of doorways. Two circles: `EVEN` (output: "even") and `ODD` (output: "odd"); the `doorway` observation arrows swap you between them; any other observation loops back to the same circle. That's a complete combinatorial filter — 2 states of memory, always-correct output.
>
> 🧮 **Your robot runs one too:** the homing loop's `{left-brighter, right-brighter, balanced, lost}` is a 4-state filter whose outputs are actions.

## 2 · Feedback plans = filters that output actions
A **feedback plan** maps what-you-know → what-to-do (`π : I-state → action`). Structurally it's **the same object as a filter** — circles, observation arrows — except the outputs are *actions* rather than answers. Consequence: everything in this lecture about shrinking filters applies to shrinking **plans** as well ("concise planning"). Passive task → filter; active task → feedback plan (yesterday's split).

## 3 · Classic automata vs filters — the concept ⭐
This is the heart of the lecture:

| | **Classic automaton (DFA)** | **Combinatorial filter** |
|---|---|---|
| Looks like | circles + labeled arrows | circles + labeled arrows (same!) |
| Job | read a **whole string**, then say **accept/reject** once at the end | give a **correct output at every step**, forever, as observations stream in |
| Which inputs matter | **all** strings | only the **feasible** observation sequences (ones the physical world can actually produce) |
| Minimization | **EASY** — polynomial time (taught in every CS course; Myhill–Nerode / Hopcroft) | **NP-HARD** — no known fast algorithm, likely none exists |

> 🧮 **The punchline in one breath:** two machines that *look identical* have wildly different minimization difficulty, because the filter's job is subtly different (always-on outputs + only feasible sequences). The lecture's message: *our intuition from classic CS does not transfer — robot-knowledge compression is fundamentally harder than language recognition.*

## 4 · Quick complexity primer (P, NP, NP-hard)
> 🧮 - **P** = problems solvable **fast** (polynomial time) — e.g. sorting, shortest path, DFA minimization.
> - **NP** = problems where a proposed answer can be **checked** fast, even if *finding* one might be slow.
> - **NP-hard** = at least as hard as everything in NP. No polynomial algorithm is known for any NP-hard problem, and it's widely believed none exists (the P ≠ NP conjecture). Practical translation: **exact answers don't scale** — for big instances you must approximate, exploit structure, or wait forever.

## 5 · Reduction by merging — and why it's hard
The natural shrinking algorithm: **merge** states that are *compatible* — same output, and their onward arrows can be made to agree. Repeat until nothing merges. (This is exactly how DFA minimization works, where it succeeds perfectly.)

> 🧮 **Why it breaks for filters — the dinner-party analogy.** Compatibility is **not transitive**: state A may be compatible with B, and B with C, while **A clashes with C**. So "who can merge with whom" is like seating guests at the fewest tables when some pairs can't sit together — and *that* is graph coloring, a famously NP-hard problem. Greedy merging can lock you into a bad seating: merge A+B first, and C ends up needing its own table; merge B+C first, and you'd have done better. **Order matters, choices interact globally — that's where the hardness lives.** (DFA states don't have this problem: their "indistinguishability" IS transitive, so merging is safe in any order.)

In practice: heuristic merge orders, or encode the conflict structure (graph coloring / clique-cover style) and feed it to a solver for exact answers on small filters. **⟵ verify w/ slides for the exact algorithm(s) shown**

## 6 · The "edge cases" — special structures where reduction gets easy
Hardness is **fragile**: restrict the filter's shape a bit and minimization drops into P. The lecture's named cases (from Saberifar–O'Kane–Shell's work):
- **No missing edges** — every state has an arrow for **every** observation (nothing undefined). Removing the "missing edge" freedom removes the bad interactions → **polynomial-time** minimization.
- **Unitary** — a structural restriction on the filter (exact definition ⟵ **verify w/ slides**) under which minimization is also tractable.
- **Once-appearing observations** — each observation label appears (essentially) once in the filter, limiting how merge choices can interact → tractable.

> 🧮 **The meta-lesson** (more exam-relevant than the definitions): *NP-hardness is a statement about the worst case of the general problem.* Real filters often have special structure — and identifying structure that restores tractability is itself a research contribution. "Hard in general, easy in your case" is a perfectly good engineering outcome.

## 7 · Parameterized complexity & FPT
> 🧮 **Fixed-parameter tractable (FPT)** = the runtime looks like `f(k) · poly(n)`: possibly horrible in some **parameter k**, but only polynomial in the input size n. If k is **small in practice**, the problem is effectively fast even though it's NP-hard in general.
>
> 🧮 **Analogy:** re-shelving a library of n books is brutal in general — but if only **k** books are misplaced, you can fix it quickly for small k, no matter how big the library. The exponential pain is *quarantined inside k*.

For filter reduction: NP-hard overall, but **FPT in a suitable parameter** (which parameter was used ⟵ **verify w/ slides**) — so meaningful reductions are computable when that parameter stays small.

## Why it matters for *minimalism*
- Filter size = the robot's **memory**. Reduction = mechanically answering "how little memory does this task need?"
- Yesterday defined the target (**minimal sufficient ITS**); today says **computing it is NP-hard in general** — a profound, slightly ironic result: *even deciding how simple a robot can be is computationally expensive.* This is exam objective #5 verbatim ("problems in robotic complexity reduction that are known to be computationally intractable").

## Connections
- `day3-refinements-and-dynamic-programming` (the minimal-sufficient object; quotients = what merging implements).
- `day2-information-spaces` (I-states), `day2-sensor-lattices` (the order in which sensors/filters compare).
- Your robot: the 4-state homing filter is near-minimal; the docking state machine is a feedback plan.

## 🎯 Likely exam points
- Define a **combinatorial filter** (states = I-states, edges = observations, outputs per state; no probabilities); give a small example (parity).
- **Filters vs DFAs**: same picture, different job (always-on output vs end verdict; feasible-only inputs) — and **DFA minimization is in P while filter minimization is NP-hard**.
- Why merging is hard: **compatibility is not transitive** → choices interact (graph-coloring flavor).
- Name the tractable **special cases** (no-missing-edges, unitary, once-appearing observations) and the meta-lesson.
- **FPT / parameterized complexity** in one sentence: `f(k)·poly(n)` — exponential confined to a small parameter.
- **Feedback plan** = filter with action outputs → plan reduction is the same problem family.

## 📝 In-class notes (raw — Jun 10; first minutes missed)
- Reduction algorithms and filters; **combinatorial filter**; feedback plans.
- Classic **automata vs filters** comparison.
- **Computational complexity**: P, NP, NP-hard.
- **Merging** as the reduction mechanism in the algorithms shown.
- Special cases: **no-missing edges, unitary, once-appearing observations**.
- **NP-hardness** of reduction; **fixed-parameter tractability**; **parameterized complexity**.

## 📎 Slides
_Pending — drop the deck in `reading_material/lecture_slides/` and I'll reconcile the ⟵ flags (exact algorithms, definition of "unitary," the FPT parameter)._

## ❓ Open questions
- Exact definition of **unitary** filters as given on the slides.
- Which **parameter** makes reduction FPT in the result they showed.
- Did they show the actual **hardness reduction** (from which NP-hard problem)?
