# Introductions, Organization & Roadmap (Lecture 1)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 1 · Mon Jun 8 · Lecture (~60 min) · Fort TS128
> Status: 🟢 in-class notes added — *the opening / framing lecture*

## TL;DR
The opening lecture: the central question of minimalism, its **history & philosophy** ("simple robots"), the **RISC** analogy from computing, the **analytical tools** for reasoning about minimal robots (complexity, set theory, linear programming, average- vs worst-case), and **bio-inspired** examples where the *body* does the work.

## The central question
- What is the **minimum** a robot needs — across **sensing, actuation, computation, communication** — to accomplish a task?
- **Two motivations:** (1) *scientific* — simple robots reveal the resources a task fundamentally requires; (2) *engineering* — simplicity aids manufacturability, cost & robustness.

## History & philosophy of minimalism
- "Simple robots" as both a **scientific probe** (remove a resource → does the task still work?) and a **design ethos** (less is more).
- **RISC analogy** 💡 — *Reduced Instruction Set Computing*: a **smaller, simpler** instruction set beat complex (CISC) designs on speed/efficiency. A canonical case that **reducing** complexity can **increase** capability — the same bet minimal robotics makes.
- Brief historical name-drops (mentioned in passing — confirm exact refs when you can):
  - **T. Smithers (1994)** — situated / behaviour-based robotics; the *dynamical-systems* view of behaviour. (Plausibly his SAB'94 piece *"On Why Better Robots Make It Harder"* — **verify**.)
  - **P. Cheeseman (1991)** — Bayesian / probabilistic approaches to AI & uncertainty. (Exact 1991 reference — **fill in**.)

## Analytical tools — how we reason about "minimal"
- **Time & space complexity** — minimal robots minimize **computation (time)** and **memory (space)**; these are the formal yardsticks.
- **Set theory** — reasoning about **possibilities**: a robot's knowledge as a **set** of possible states (this is exactly the nondeterministic I-state; predict/correct = set **union / intersection**). → `day2-information-spaces`
- **Linear programming (LP)** — an optimization formulation; also the source of a key complexity lesson ↓
- **Average-case vs worst-case** ⭐ *(answers "what does average mean here?")*
  - **Worst-case** = cost on the **hardest** input of size *n* — a guarantee that always holds.
  - **Average-case** = the **expected** cost over a **distribution of inputs** — i.e. *typical* behaviour, averaged across all inputs (not the one nasty input).
  - **The LP example:** the **simplex** method is **exponential in the worst case** (Klee–Minty), yet **polynomial on average / in practice**. (Interior-point methods are polynomial even worst-case.)
  - **Why it's a tradeoff / why it matters:** worst-case bounds can be far too pessimistic for what a robot *actually* encounters; "average" captures typical performance but **depends on the assumed input distribution**. Which one you optimize is a genuine design decision.

## Bio-inspired minimalism — the body does the work
- 🪳 **Cockroach locomotion** — fast, stable running comes largely from **passive mechanical self-stabilization** ("preflexes"): the body's mechanics reject perturbations **without neural feedback** (Full & Koditschek). Stability almost "for free."
- 🐟 **Trout locomotion** — a trout (even a **dead** one) can extract energy from **vortices** shed by an obstacle to hold station / move upstream with little-to-no muscle effort (the **Kármán gait**) — exploiting the environment's own dynamics.
- Both illustrate **embodiment / morphological computation**: minimal sensing & control because the **body + environment** do the work. → `day2-embodiment-x-minimalism`

## Connections
- Frames the whole week → `day2-information-spaces`, `day2-sensor-lattices-and-comparing-robots`, `day4-information-invariants`, `day4-co-design`.
- Bio examples → `day2-embodiment-x-minimalism`; complexity / LP → `day3-filters-plans-and-reduction-algorithms`.

## 🎯 Likely exam points
*(These were brief mentions — aim to recognize/explain each in a sentence or two, not in depth.)*
- The central question + the **four resource dimensions** + two motivations.
- **RISC** as the minimalism analogy ("simpler can be more powerful").
- **Average- vs worst-case** complexity, with the **simplex / LP** example.
- One **bio example** of embodiment (cockroach self-stabilization, or the dead-trout / vortex effect).

## 📝 In-class notes (raw — from class)
- History of minimalism + philosophy; "simple robots".
- RISC architecture example.
- Brief refs: **T. Smithers 1994**, **P. Cheeseman 1991**.
- Time & space complexity; set theory; linear programming; **average vs worst-case** tradeoff.
- Cockroach locomotion; trout locomotion.

## ❓ Open questions
- Exact **Smithers 1994** & **Cheeseman 1991** citations + why they were cited?
- Was **LP** used for a specific robot formulation, or only as a complexity example?
- How much complexity theory is examinable?
