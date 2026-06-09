# Minimalism as a Life Philosophy

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture · Fort TS128
> Status: 🟢 in-class notes added (Jun 9)

## TL;DR
The **history & philosophy** of minimalism — "simple robots" as a research stance — illustrated with the **RISC** analogy from computing, a couple of historical references, the **analytical tools** for reasoning about minimal systems (complexity, set theory, linear programming, average- vs worst-case), and **bio-inspired** examples where the *body* does the work.

## History & philosophy of minimalism
- **"Less is more"** as a design discipline and research stance: strip a robot to what a task *fundamentally* requires.
- "Simple robots" as both a **scientific probe** (remove a resource → does the task still work?) and a **design ethos**.
- Echoes broader ideas: **Occam's razor**; behaviour-based robotics ("intelligence without representation").
- **RISC analogy** 💡 — *Reduced Instruction Set Computing*: a **smaller, simpler** instruction set beat complex (CISC) designs on speed/efficiency. A canonical case that **reducing** complexity can **increase** capability — the same bet minimal robotics makes.
- Brief historical name-drops (mentioned in passing — confirm exact refs when you can):
  - **T. Smithers (1994)** — situated / behaviour-based robotics; the *dynamical-systems* view of behaviour. (Plausibly his SAB'94 piece *"On Why Better Robots Make It Harder"* — **verify**.)
  - **P. Cheeseman (1991)** — Bayesian / probabilistic approaches to AI & uncertainty. (Exact 1991 reference — **fill in**.)

## Analytical tools — how we reason about "minimal"
- **Time & space complexity** — minimal robots minimize **computation (time)** and **memory (space)**; the formal yardsticks.
- **Set theory** — reasoning about **possibilities**: a robot's knowledge as a **set** of possible states (exactly the nondeterministic I-state; predict/correct = set **union / intersection**). → `day2-information-spaces`
- **Linear programming (LP)** — an optimization formulation; also the source of a complexity lesson ↓
- **Average-case vs worst-case** ⭐
  - **Worst-case** = cost on the **hardest** input of size *n* — a guarantee that always holds.
  - **Average-case** = the **expected** cost over a **distribution of inputs** — *typical* behaviour averaged across inputs (not the one nasty input). Depends on the assumed input distribution.
  - **LP example:** the **simplex** method is **exponential worst-case** (Klee–Minty) but **polynomial on average / in practice** (interior-point methods are polynomial even worst-case).
  - **Takeaway:** worst-case bounds can be too pessimistic for what a robot *actually* encounters; don't over-build for cases that never occur.

## Bio-inspired minimalism — the body does the work
- 🪳 **Cockroach locomotion** — fast, stable running from **passive mechanical self-stabilization** ("preflexes"): body mechanics reject perturbations **without neural feedback** (Full & Koditschek). Stability almost "for free."
- 🐟 **Trout locomotion** — a trout (even a **dead** one) extracts energy from **vortices** shed by an obstacle to hold station / swim upstream with little-to-no muscle effort (the **Kármán gait**) — exploiting the environment's own dynamics.
- Both = **embodiment / morphological computation**: minimal sensing & control because **body + environment** do the work. → `day2-embodiment-x-minimalism`

## Connections
- The philosophical + foundational frame for the week → `day2-information-spaces`, `day2-sensor-lattices-and-comparing-robots`, `day4-information-invariants`, `day4-co-design`.
- Bio examples → `day2-embodiment-x-minimalism`; complexity / LP → `day3-filters-plans-and-reduction-algorithms`.

## 🎯 Likely exam points
*(These were brief mentions — aim to recognize/explain each in a sentence or two.)*
- **RISC** as the minimalism analogy ("simpler can be more powerful").
- **Average- vs worst-case** complexity, with the **simplex / LP** example.
- One **bio example** of embodiment (cockroach self-stabilization, or the dead-trout / vortex effect).
- Why minimal robots are scientifically & practically valuable.

## 📝 In-class notes (raw — from class, Jun 9)
- History of minimalism + philosophy; "simple robots".
- RISC architecture example.
- Brief refs: **T. Smithers 1994**, **P. Cheeseman 1991**.
- Time & space complexity; set theory; linear programming; **average vs worst-case** tradeoff.
- Cockroach locomotion; trout locomotion.

## ❓ Open questions
- Exact **Smithers 1994** & **Cheeseman 1991** citations + why they were cited?
- Was **LP** used for a specific robot formulation, or only as a complexity example?
- How much complexity theory is examinable?
