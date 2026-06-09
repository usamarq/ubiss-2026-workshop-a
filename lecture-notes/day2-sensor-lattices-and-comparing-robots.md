# Sensor Lattices & Comparing Robots (Lecture)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture · Fort TS128
> Status: 🟢 **reconciled with the Sensors lecture slides** (Jun 9) · 🧮 = beginner math explainer. (A research area of the instructors — esp. **Dylan Shell**.)

## TL;DR
A precise way to compare sensors (and therefore robots) by **how much they can tell apart**. Sensors sit in a "**more-informative-than**" ordering (the **dominance** partial order); that ordering turns out to be a **lattice**, which is what lets you hunt for the *minimal* sensor that still does a job.

---

## 1 · Partial order (poset)
A **partial order** is a way of saying "this is ≤ that" on a set, obeying three rules:
- **Reflexive:** `a ≤ a` (everything ≤ itself).
- **Antisymmetric:** if `a ≤ b` *and* `b ≤ a`, then `a = b` (no two *different* things are ≤ each other both ways).
- **Transitive:** if `a ≤ b` and `b ≤ c`, then `a ≤ c` (chains carry through).

> 🧮 **Why "partial"?** In a **total** order (like numbers on a line) *any* two things are comparable — one is always ≤ the other. In a **partial** order, some pairs are **incomparable**: neither `a ≤ b` nor `b ≤ a`. Think **"is an ancestor of"** in a family tree — your two grandparents are both above you, but neither is an ancestor of the other. Or **subsets under `⊆`**: `{1} ⊆ {1,2}`, but `{1}` and `{2}` are incomparable.
>
> 🧮 **Hasse diagram** = the usual picture of a poset: dots for elements, a line going *upward* from `a` to `b` whenever `a ≤ b` (skipping links you can infer). Incomparable elements sit side-by-side with no line between them.

---

## 2 · Upper/lower bounds → Lattice
Take a partial order and any two elements `a, b`:
- An **upper bound** = an element that sits **≥ both** `a` and `b`.
- A **lower bound** = an element that sits **≤ both**.
- The **least upper bound (LUB)**, a.k.a. **join** `a ∨ b` = the *smallest* of all the upper bounds.
- The **greatest lower bound (GLB)**, a.k.a. **meet** `a ∧ b` = the *largest* of all the lower bounds.

A **lattice** = a partial order in which **every pair has both a LUB and a GLB**.

> 🧮 **Plain version.** "Upper bounds of `a` and `b`" = everything sitting above *both*; the **join** is the *lowest* such ceiling. "Lower bounds" = everything below both; the **meet** is the *highest* such floor. A lattice just guarantees those two always exist. (Numbers under `≤`: join = max, meet = min.)

### The power-set (set-inclusion) lattice — the textbook example
Take any set `S`. Its **power set** `P(S)` = the set of **all subsets** of `S` (including `∅` and `S` itself). Order them by **inclusion `⊆`** → a lattice:
- **join = union `∪`** · **meet = intersection `∩`**
- **top `⊤` = S`** (the whole set) · **bottom `⊥` = ∅`** (empty set)

> 🧮 **Power set.** "All possible subsets." If `S` has `n` elements, `P(S)` has `2ⁿ`. For `S = {a,b,c}` (2³ = 8 subsets) the Hasse diagram is a *cube*:
> ```
>         {a,b,c}        ⊤  (whole set)
>        /   |   \
>    {a,b} {a,c} {b,c}   size-2 subsets
>        \   |   /
>     {a}  {b}  {c}      size-1 subsets
>        \   |   /
>          { }           ⊥  (empty set)
> ```
> _(each set links upward to every set that contains it; drawn fully it's a cube.)_ Two subsets like `{a}` and `{b}` are **incomparable** — neither contains the other — so again the order is *partial*.

🔗 **Why this is THE example for us:** a sensor's knowledge is a *set* of possible states, and the **nondeterministic information space is exactly `pow(X)`** (from `day2-information-spaces`). So the set-inclusion lattice is the natural home for reasoning about what a robot can or can't rule out.

---

## 3 · Sensor lattice
Recall from `day2-information-spaces`: a sensor's readings **partition** the state space `X` into groups it can't tell apart (its **preimages**). Order sensors by how **fine** that partition is:
- **Finer partition = more distinctions = more informative.**
- **Top `⊤`** = the **perfect sensor** (every state in its own group → knows the exact state).
- **Bottom `⊥`** = the **null sensor** (one big group → tells you nothing).
- **Join two sensors** = *use both at once* (you can distinguish states if **either** sensor can) → moves **up** the lattice (more info).
- **Meet two sensors** = the information they **share** (only what both agree on) → moves **down**. ✅ *(Slides confirm the orientation: more-informative = finer = **higher**; in the distance-sensor lattice the full 360° scan is at the top, the null sensor at the bottom. Exact meet/join formulas for arbitrary sensors weren't given — just that the lattice exists.)*

> 🧮 **Concrete picture (using the grid-world colours):**
> ```
>            perfect sensor  (knows exact state)        ⊤  most informative
>                    |
>        "which exact colour?" (red/blue/green/black)
>              /                         \
>     "is it red?"                   "is it blue?"      ← incomparable!
>              \                         /
>                  null sensor (no info)                ⊥  least informative
> ```
> "is it red?" and "is it blue?" are **incomparable** — each spots something the other can't. Their **join** = a sensor telling red vs blue vs (the rest); their **meet** = the null sensor. That single picture shows a partial order, incomparability, and a lattice at once.

---

## 4 · Dominance partial order
The order on sensors has a name: **dominance**.
- **Sensor A dominates sensor B** (write `B ⪯ A`) ⇔ **A is at least as informative as B** ⇔ A's partition is at least as fine ⇔ *whenever A gives two states the same reading, B does too* (A never confuses states that B can separate).
- It's a genuine **partial order**: reflexive, transitive, and antisymmetric **up to equivalence** — two sensors that induce the *same* partition are treated as **equivalent** (so the order is really on "what a sensor can distinguish," not its wiring).
- **Incomparable sensors** exist (the red- vs blue-detector above): neither dominates the other.

> 🧮 **One-line test:** A dominates B if A's "confusions" are a subset of B's confusions — A makes *all* of B's distinctions and maybe more.

---

## 4b · Dominance = simulability (the slide's key result) ✅
If `h_a` dominates `h_b`, you can **simulate `h_b` using `h_a` plus a relabelling function** `g : Y_a → Y_b`:
> `h_b = g ∘ h_a` — take `h_a`'s reading and post-process it.

(Equivalently: if `Π_a` refines `Π_b`, you can *coarsen* `Π_a` to get `Π_b`.) So *"a is at least as good as b"* literally means *"a can stand in for b."*

> ⚠️ This **ignores the cost** of computing `g` — which is exactly the sensing ⇄ computation trade-off in `day4-information-invariants`.

## 5 · Comparing robots & the minimalism payoff
- **Compare two robots** by where their sensors sit in this lattice: a robot with a **dominating** sensor is *at least as capable* (information-wise). If they're **incomparable**, neither is strictly "better" — each knows things the other can't.
- **Minimalism = go as low as you can.** For a given task, find the **least informative sensor that still solves it** — the lowest point in the lattice that's still "good enough." That's a precise version of "how little sensing is enough?" and gives the **metrics** the workshop wants (objective #1).
- 💡 **"a minimal" vs "the minimal":** because dominance is a *partial* (not total) order, there can be **several incomparable minimal robots** — you find *a* minimal robot, not necessarily *the* minimal one.
- Directly useful for our **docking project**: it's the formal way to argue our two light sensors are *sufficient* (and that fancier sensors would be needlessly high in the lattice).

## From the slides (the Sensors lecture) 📊
**Why compare at all?** To know whether two pieces of hardware are **interchangeable** — from the *information* viewpoint, can one device's signal be transformed into another's? A lattice gives a **global view** of those interrelationships.

### Worked example — three distance sensors (LaValle 2019)
- **'All 360°'** — distance in every direction (a full scan).
- **'Nearest Obstacle'** — only the distance to the closest obstacle (the min over all directions).
- **'Distance Ahead'** — only the forward distance.

You can compute the latter two *from* the 360° scan, so it **dominates** both; *Nearest-Obstacle* and *Distance-Ahead* are **incomparable**. The lattice:
```
            h_360°           ← most informative (top)
           /      \
   h_NearestObs   h_Ahead    ← incomparable
           \      /
            h_∅              ← null sensor (bottom)
```

### Three generalizations (briefly shown)
- **Noisy sensors** → readings aren't deterministic, so the basic objects are **covers, not partitions** → you get a **semilattice** (Zhang & Shell 2021). And sometimes **less discriminating power is *desirable*** (e.g. privacy guarantees)!
- **General capabilities via *primitives*** → you can simulate a sensor with **actions**: a robot with only odometers that *drives until it bumps a wall, turns 180°, and returns* recovers what a distance sensor would have told it (O'Kane 2007). → sensing ⇄ motion trade-off.
- **Lattices of plans / action-based sensors** — plans (which use *memory*) and action-based sensors (*stateless*) both encode the information a task needs (McFassel & Shell 2022).

### Key references
LaValle 2019 (*Sensor Lattices*) · O'Kane 2007 (PhD, *A theory for comparing robot systems*) · O'Kane & LaValle 2008 (*On Comparing the Power of Robots*, IJRR) · Zhang & Shell 2021 · McFassel & Shell 2022.

## Connections
- Built on **preimages / partitions** from `day2-information-spaces`.
- Feeds `day4-information-invariants` (reductions/trades between sensing resources) and the docking `project/`.

## 🎯 Likely exam points
- Define a **partial order** (3 rules) and why it's "partial" (incomparable elements); contrast with a total order.
- Define **upper / lower bound** and **LUB (join) / GLB (meet)**; define a **lattice**; give the **power-set (set-inclusion) lattice** (join = `∪`, meet = `∩`, top = `S`, bottom = `∅`).
- Explain the **dominance** order on sensors (A dominates B = A's partition refines B's = A at least as informative); name the top (perfect) and bottom (null).
- Use it to **compare two robots** / pick a **minimal sufficient** sensor.
- State **dominance ⇔ simulability**: `h_a ⪰ h_b` iff `h_b = g ∘ h_a` for some relabelling `g`.
- Why there's *a* minimal robot, not *the* minimal robot (a partial, not total, order).

## 📝 In-class notes (raw — Jun 9)
- Intro to **partial order**, **lattices**, **sensor lattices**, **dominance partial order**, etc.
- Also covered: **upper bounds / lower bounds** (→ LUB / GLB), and the **power-set / set-inclusion lattice** as the worked example.
- _(add: any specific definitions, diagrams, or examples the instructor used — and the formal meet/join for sensors)_

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture_ Sensors.pdf`** ("On Sensor Lattices and Comparing Robots").

## ❓ Open questions
- ✅ Orientation resolved: more-informative = **top** (distance-sensor lattice: 360° on top, ∅ at bottom).
- ✅ Dominance characterised via **simulation** `h_b = g ∘ h_a`.
- Exact **meet/join formulas** for two arbitrary sensors weren't given explicitly — only that the lattice exists.
