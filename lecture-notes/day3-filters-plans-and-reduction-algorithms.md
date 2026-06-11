# Filters, Plans & Reduction Algorithms ("Reduction of Filters and Plans: Hardness and Algorithms")

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Lecture · Fort TS128
> Status: 🟢 **reconciled with the Lecture 5 slides** · 🧮 = beginner explainer — deliberately gentle.
> (Research area of **Shell, Zhang, O'Kane** — the reference list is their papers 2020–2024.)

## TL;DR (the whole lecture in four sentences)
A **combinatorial filter** is a tiny machine — circles and arrows — that tracks what a robot knows. Smaller filter = less memory = more minimal robot, so we want to **reduce** filters by merging states. The shock result: although filters look exactly like classic automata (which minimize in near-linear time), **filter minimization is NP-complete**. The escape hatches: **special structural classes** where it's efficient, and a **fixed-parameter tractable** algorithm whose exponential cost is confined to structural parameters that are often small.

---

## 0 · Why (the slides' framing)
> *"How much state information is needed to achieve some ends?"*
- History: the **anti-model manifesto** of behaviour-based robotics — **Brooks (1991) "Intelligence without representation"**, **Connell (1990) "Minimalist mobile robotics"**.
- This lecture's emphasis is different:
  1. **Not about saving money** (though memory is costly);
  2. about uncovering the **indispensable information requirements** of tasks;
  3. limited-state designs **touch just the essentials**.
- And the agenda: such designs used to come from **clever humans** → can we **automate them with algorithms?** (= filter reduction).

> 🧮 **Key idea — information bottleneck.** Same picture as an **autoencoder** in ML: force the signal through a narrow waist; compression discards the irrelevant. The slides even set combinatorial filters alongside **Bayesian / Kalman / particle filters** — all are "stateful boxes turning observation streams into outputs"; we want the *smallest* such box.

## 1 · The objects
**Combinatorial filter** = finite-state machine for tracking knowledge: **circles** = I-states, **arrows** = observations, each circle carries an **output** (the current answer). No probabilities.
- Slide example: **"Are they together or apart?"** (Tovar et al. 2014) — a filter whose outputs are `Together`/`Apart`, then its **minimized** version: same answers, fewer states.
- 🧮 You've already built two: the parity counter (2 states), and the robot's homing loop (`{left, right, balanced, lost}`).

**Feedback plan** = the same object with **action outputs**. Slide example: a grid robot with observations `{bump, ¬bump}` and actions `{Forward, Left turn, Right turn, Stop}` reaching a goal `G`. Filters output *information*; plans output *actions* — one theory covers both.

## 2 · Minimization: automata vs filters ⭐ (the core table)

| | **Classic automaton (DFA)** | **Combinatorial filter** |
|---|---|---|
| Correctness notion | language equality `L(A_in) = L(A_out)` | **Output Simulation** (below) |
| What matters | all strings | only **feasible** strings — *"the world's structure ⇒ only some strings will ever arise"* |
| Minimization | **Θ(\|V\| log \|V\|)** — Myhill–Nerode (1958) / Hopcroft | **NP-complete** |

> **Output Simulation (the filter-correctness definition, verbatim):** *Filter F is output simulated by G if, for every input string that F can take, G takes that input string and produces an output matching F's.* — i.e. the small filter must answer identically on every observation sequence the world can actually produce. This replaces "same language" as what minimization must preserve.

> 🧮 **The punchline:** same picture, different correctness notion, *opposite* complexity. Intuitions from classic CS do not transfer.

## 3 · Complexity theory "in a nutshell" (as presented)
- Complexity theory **relates classes of problems**; you commit to a model of computation; and it's often about **"justifying bad news"** — the famous Garey & Johnson cartoon, three captions: *"I can't find an efficient algorithm…*
  1. *…I guess I'm just too dumb."* → 2. *…because no such algorithm is possible!"* (what we'd love to say) → 3. *…but neither can all these famous people."* (what NP-hardness actually gives us).
- **P ⊆ NP**; whether **P = NP** is open — results are conditional on widely-held assumptions.
- Nice slide line: you don't have to care about the computational device — complexity is *"a prism through which quite robust distinctions become visible to the naked eye."*

## 4 · The reduction algorithm (and where hardness bites)
Pipeline from the slides, for FM(DF→DF) (deterministic-filter → deterministic-filter minimization):
1. **Input filter** → build the **compatibility graph**: states `w_i, w_j` are **compatible** iff *their outputs agree on all their common extensions* (no future observation sequence makes them answer differently).
2. Find a **Minimum Clique Cover** of the compatibility graph — cover all states with the fewest fully-mutually-compatible groups; each clique becomes one merged state.

> 🧮 **Dinner-party intuition still applies:** compatibility is not transitive (A~B, B~C, yet A✗C), so grouping into fewest tables = clique cover (equivalently, coloring the conflict graph) — **NP-hard**. *This* is where the hardness lives.

3. **Zipper constraints:** merging two states forces other merges downstream (their successors must also agree — the merge "zips" forward along transitions). With multiple outputs per state these constraints live on a **compatibility simplicial complex**, and there can be exponentially many — so they're represented **implicitly in a SAT formulation** (solve exactly with a SAT solver; Zhang, Rahmani, Shell & O'Kane, ICRA 2021).

## 5 · Efficient special cases (the "edge cases")
The slides showed a **hierarchy of special classes** where minimization is efficient (Zhang & Shell, ICRA 2023 — "a general class of combinatorial filters that can be minimized efficiently"):
- **no-missing-edge** — every state has an arrow for every observation;
- **unitary**;
- **once-appearing-observation** — an observation label appears only once;
- nested inside broader notions: *neighborhood-comparable* ⊂ … ⊂ *globally-language-comparable* (the general efficient class).

> 🧮 **Meta-lesson (more exam-worthy than the definitions):** NP-completeness is about the *general worst case*. Restrict the filter's shape and the problem can drop into P — *hardness is fragile, and finding the tractable structure is the research contribution.*

## 6 · Fixed-parameter tractability (FPT)
- **Definition (Flum & Grohe):** an NP-hard problem is **FPT** if some algorithm solves it in **`f(k) · n^O(1)`** time, where `k` is a parameter of the instance — all the exponential pain is confined to `k`.
- 🧮 Slide warm-up example — **SAT**: with `k` variables and `m` clauses, brute force is `O(2^k · m)`: exponential *only* in k. A formula with millions of clauses but 20 variables is easy.
- **The filter result (Zhang & Shell, WAFR 2024):** FM(DF→DF) is **FPT** with runtime roughly `O((2+ℓ)^ω · 2^((β+z)(m+z)) log(m+z) · |V|^O(1))` — the parameters are **structural**: `z` = number of **zipper arcs**, `ω`/`ℓ` = width/height of the zipper graph, `β` = largest clique size, `m` = number of cliques in the smallest cover. **Core idea:** *pick chains to merge and enforce zipper constraints by augmenting a traditional covering problem.*
- 🧮 Translation: if the filter's *merge-interaction structure* (the zipper graph) is small/shallow — which it often is in practice — exact minimization is feasible even though the general problem is NP-complete.

## 7 · Nondeterminism (the frontier)
For **plans**, *causal constraints affect nondeterminism* — you can't condition on observations you haven't received — and allowing nondeterministic machines under **output commitment** yields *"automata-like objects that form a genuine new class"* (Zhang & Shell, ICRA 2022 & WAFR 2022). Mentioned as current research; depth not required.

## The summary aphorism (quotable in the exam)
> **"Compression discards the irrelevant; and whatever remains expresses that which is important."**

## Why it matters for *minimalism*
Filter size = robot memory. Yesterday defined the target (**minimal sufficient ITS**); today: **computing it is NP-complete in general** — *even deciding how simple a robot can be is computationally expensive* — but structure + parameters often rescue practice. This is exam objective #5 verbatim.

## Connections
- `day3-refinements-and-dynamic-programming` (minimal sufficient object; quotients = what merging implements).
- `day2-information-spaces`, `day2-sensor-lattices` (Output Simulation is the dynamic cousin of sensor dominance/simulation `h_b = g ∘ h_a`).
- Behaviour-based history: `day2-minimalism-as-life-philosophy` (Brooks).

## 🎯 Likely exam points
- Define a **combinatorial filter** + give a small example; **feedback plan** = filter with action outputs.
- **DFA vs filter minimization**: Myhill–Nerode / `Θ(|V| log |V|)` vs **NP-complete**; the role of **feasible strings**; define **Output Simulation**.
- The algorithm: **compatibility graph → minimum clique cover**, **zipper constraints**, SAT encoding; why greedy merging fails (compatibility not transitive).
- Name the efficient **special cases** (no-missing-edge, unitary, once-appearing-observation) + the meta-lesson.
- **FPT**: `f(k)·n^O(1)` (Flum & Grohe); SAT `O(2^k m)` example; filter reduction is FPT in zipper-structure parameters.

## 📝 In-class notes (raw — Jun 10; first minutes missed → §0–1 cover them)
- Combinatorial filter; reduction algorithms; feedback plans; automata-vs-filters; P/NP; merging; no-missing-edges/unitary/once-appearing; NP-hardness; FPT; parameterized complexity.

## 📚 References (from the deck)
Brooks 1991 · Connell 1990 · Zhang & Shell WAFR 2024 (FPT) · Zhang & Shell ICRA 2023 (efficient class) · Zhang & Shell WAFR 2022 + ICRA 2022 (nondeterminism) · Zhang, Rahmani, Shell, O'Kane ICRA 2021 (SAT/constraints) · Zhang & Shell WAFR 2020 (cover filters) · Tovar et al. 2014 (together/apart example).

## ❓ Open questions
- Precise definition of **unitary** (named on the hierarchy slide but not defined there).
- The NP-completeness *reduction source* wasn't shown — fine for the exam (the statement + why-it-matters suffice).
