# Sensor Lattices & Comparing Robots (Lecture)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture · Fort TS128
> Status: 🟢 in-class notes added (Jun 9) · **official slides pending** → items marked **⟵ reconcile w/ slides**
>
> 🧮 = beginner math explainer. (This is a research area of the instructors — esp. **Dylan Shell** — so expect the formal version.)

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

## 2 · Lattice
A **lattice** is a partial order where **every pair** of elements `a, b` has both:
- a **join** `a ∨ b` — the **least upper bound**: the *smallest* element that is ≥ both, and
- a **meet** `a ∧ b` — the **greatest lower bound**: the *largest* element that is ≤ both.

> 🧮 **Plain version.** A lattice is a poset where any two things have a well-defined *"smallest thing sitting above both"* (join) and *"biggest thing sitting below both"* (meet). Example — **subsets under `⊆`**: `join = union (∪)`, `meet = intersection (∩)`; the **top `⊤`** is the whole set, the **bottom `⊥`** is the empty set. (Numbers under `≤`: join = max, meet = min.)

---

## 3 · Sensor lattice
Recall from `day2-information-spaces`: a sensor's readings **partition** the state space `X` into groups it can't tell apart (its **preimages**). Order sensors by how **fine** that partition is:
- **Finer partition = more distinctions = more informative.**
- **Top `⊤`** = the **perfect sensor** (every state in its own group → knows the exact state).
- **Bottom `⊥`** = the **null sensor** (one big group → tells you nothing).
- **Join two sensors** = *use both at once* (you can distinguish states if **either** sensor can) → moves **up** the lattice (more info).
- **Meet two sensors** = the information they **share** (only what both agree on) → moves **down**.  **⟵ reconcile w/ slides** (exact meet/join definitions & which way "up" points can flip between conventions).

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

## 5 · Comparing robots & the minimalism payoff
- **Compare two robots** by where their sensors sit in this lattice: a robot with a **dominating** sensor is *at least as capable* (information-wise). If they're **incomparable**, neither is strictly "better" — each knows things the other can't.
- **Minimalism = go as low as you can.** For a given task, find the **least informative sensor that still solves it** — the lowest point in the lattice that's still "good enough." That's a precise version of "how little sensing is enough?" and gives the **metrics** the workshop wants (objective #1).
- Directly useful for our **docking project**: it's the formal way to argue our two light sensors are *sufficient* (and that fancier sensors would be needlessly high in the lattice).

## Connections
- Built on **preimages / partitions** from `day2-information-spaces`.
- Feeds `day4-information-invariants` (reductions/trades between sensing resources) and the docking `project/`.

## 🎯 Likely exam points
- Define a **partial order** (3 rules) and why it's "partial" (incomparable elements); contrast with a total order.
- Define a **lattice** (join = least upper bound, meet = greatest lower bound); give the subset example.
- Explain the **dominance** order on sensors (A dominates B = A's partition refines B's = A at least as informative); name the top (perfect) and bottom (null).
- Use it to **compare two robots** / pick a **minimal sufficient** sensor.

## 📝 In-class notes (raw — Jun 9)
- Intro to **partial order**, **lattices**, **sensor lattices**, **dominance partial order**, etc.
- _(add: any specific definitions, diagrams, or examples the instructor used — and the formal meet/join for sensors)_

## 📎 Slides
_Drop the deck in [`../slides/`](../slides/) (e.g. `sensor-lattices.pdf`) and I'll reconcile — especially the exact meet/join definitions and order orientation (flagged ⟵ reconcile w/ slides)._

## ❓ Open questions
- Exact **meet/join** of two sensors as defined in the lecture (and is "more informative" drawn at the top or the bottom?).
- Did they cover **how to compute** the lattice / minimal sensor, or just the concepts?
- Any **named results** (e.g. about the size/complexity of the sensor lattice)?
