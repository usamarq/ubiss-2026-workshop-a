# Refinements & Approximate Information Spaces

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Lecture · Fort TS128
> Status: 🟢 in-class notes added (Jun 10) · **slides pending** → inferred parts marked **⟵ verify w/ slides**
> 🧮 = beginner explainer. (This is the instructors' own research line — Sakçak/LaValle's *information transition systems*.)

## TL;DR
The history I-space is the *maximal* internal representation — and far too big. This lecture is about **collapsing histories while keeping something useful**: which information must be **preserved** for a task, formalized via **quotients of transition systems**, **sufficient I-maps**, and ultimately the **minimal sufficient** representation — the smallest "brain" that still does the job. Tasks split into **passive** (filtering) and **active** (planning/policies), and casting tasks as **cost/reward optimization** connects all of this to dynamic programming and **reinforcement learning**.

---

## 1 · The central question
> **What information must be preserved?**

Full histories `η_k = (y₁,u₁,…,y_k)` grow forever. We want to **collapse** them into something small that is *still useful* — where "useful" means: you can still (a) keep it updated, and (b) accomplish your task. Everything below is machinery for making "collapse but stay useful" precise.

## 2 · Transition systems (the modeling language)
- A **transition system** = a graph: **states** + labeled **arrows** (transitions) saying how inputs move you between states. (Like a board game: circles and moves.)
- A **state-relabeled transition system** adds a **labelling function** that paints each state with an output/label — marking *what you care about* (e.g. "goal / not-goal", a color, "door open / closed").

> 🧮 **Why labels?** The label is the *task-relevant* part of a state. Two states with the same label are "the same as far as the task cares" — *unless* their future behaviour differs. Labels are how a task gets injected into the math.

- **External vs internal:** the *external* system models the physical world (robot body + environment). The **internal system** is what runs in the robot's head — an **Information Transition System (ITS)**: its states are **I-states**, and incoming observations/actions drive its transitions. **⟵ verify w/ slides**
- **History ITS** — the internal system whose states are full histories: the *maximal* ITS. Everything else is a compression of it.

## 3 · Quotient transition systems — "collapse but stay consistent"
- Take a labelling/equivalence on states → **merge** each group of equivalent states into one super-state → the **quotient transition system**.
- The quotient is only *legitimate* if it stays **consistent with the dynamics**: whenever you merge states, their merged transitions must still be well-defined (same input from the merged state can't need to go to two different merged states). **⟵ verify w/ slides for the exact condition used**

> 🧮 **Subway-map analogy.** A city map (every street = every history) vs the subway map (stations = merged regions). The subway map is *useful* because it's consistent: "take line U from station A" has one well-defined result. A quotient is exactly that: a smaller map that still navigates correctly. "Which states are useful to distinguish?" = "which stations must not be merged?"

## 4 · Sufficient I-maps → Minimal sufficient I-maps ⭐
- An **I-map** `κ` collapses history I-states into derived I-states (Day 2). It is **sufficient** if the derived I-state can be **updated from itself + the new action/observation alone** — no peeking back at the history — *and* it still determines what the task needs.
- A **minimal sufficient I-map** is a sufficient I-map that **cannot be collapsed any further** — merge any two of its states and either the update rule breaks or the task answer is lost. It's the **coarsest quotient that still works**: the smallest internal system for the job.

> 🧮 **Simple example — the parity counter.** Task: report whether the robot has crossed an **even or odd** number of doorways.
> - Full history: the entire walk log — unbounded.
> - Sufficient I-map: **one bit** `{even, odd}`, flipped every time a doorway is sensed. Updatable from itself + the latest observation ✓, answers the task ✓.
> - **Minimal**: try to compress further — one single state can't distinguish even from odd ✗. So the 2-state filter is **the minimal sufficient ITS**. An infinite history space collapsed to **two states**, with zero loss *for this task*.
>
> 🧮 **Live example — our docking robot.** For "drive to the strobe," the full history of light readings collapses to **four derived I-states**: `{left-brighter, right-brighter, balanced, lost}` (computed from the current wobble pair). That's a sufficient I-map for homing — and it's (close to) minimal: merge any two and the behaviour breaks. Our actual `code.py` *is* a small ITS.

- Analogy worth knowing: this is the same idea as **minimizing a finite automaton** (merge indistinguishable states); "can't-collapse-further" plays the role of Myhill–Nerode equivalence. **⟵ verify w/ slides if they named it**

## 5 · Tasks: passive vs active
Tasks are specified by **labelling** (what counts as correct output / goal).

| | **Passive task** | **Active task** |
|---|---|---|
| Robot's job | **track / report** something as data streams in | **achieve** something by choosing actions |
| Robot chooses actions? | no (or they're irrelevant to the task) | yes — that's the point |
| Solved by | a **filter** (I-state update + readout) | **planning / a policy** over I-states |
| Example | "always know which room I'm in", people-counting | "dock on the target", "reach the kitchen" |

> 🧮 **How the filtering/planning split works.** A *passive* task only needs correct **bookkeeping**: maintain the I-state, answer the question — that maintenance loop *is* a filter. An *active* task needs **choices**: a **policy** `π : I-state → action`. But notice the policy must be fed by an I-state — so **every active task contains a passive core** (track enough to act on). Filter design underlies planning; that's why tomorrow's filter-minimization results matter for both.

- **Policy** = a rule mapping each internal state to an action (this lecture's "introduction of policies in robotic systems").
- **Reactive policy** = a policy that needs **only the current (latest) derived I-state — no extra memory**. Braitenberg vehicles are the purest case: sensor wired to motor. Our homing loop is a reactive policy over its 4 derived states.

> 🧮 **How reactive ties to refinements.** Whether a *reactive* policy suffices depends on **how far you collapsed**. If the task's minimal sufficient ITS is computable from the current reading alone (docking: yes), a reactive policy works — maximum minimalism. If the task inherently needs **memory** (parity: you must *remember* the bit), pure reactivity fails, and you must **refine** — preserve more information (add states/memory). Refinement ↔ moving finer along the spectrum: *reactive (coarsest) … minimal sufficient … full history (finest)*. The task fixes how coarse you may go; minimalism says: go exactly there.

## 6 · Tasks as cost/reward optimization → DP & RL
- Generalize "goal labels" to **costs/rewards** per state-action; the task = optimize cumulative cost/reward.
- With a **known model**: **dynamic programming** (value iteration / Bellman backups) computes optimal policies over the (derived) I-space — feasible only if the I-space is small ⇒ another reason to want minimal/approximate I-spaces.
- With an **unknown model**: **reinforcement learning** — learn the policy/value from experience. Modern RL agents with memory (recurrent nets) are implicitly *learning a sufficient I-map*; "state abstraction" in RL is this lecture's quotient idea in learned form. **⟵ verify w/ slides for how deep they went**

## 7 · Approximate information spaces
Exact minimal sufficient ITSs can be hard to compute (ties into tomorrow's NP-hardness of filter reduction). So in practice: **approximate** — quantize the I-space, cap memory, or learn a representation — trading some optimality/guarantees for tractability. **⟵ verify w/ slides for the specific approximation scheme shown**

## Why it matters for *minimalism*
This is the workshop's thesis made formal: the **minimal sufficient ITS is the smallest brain (memory + distinctions) a task requires**. Below it, the task breaks; above it, you're carrying dead weight.

## Connections
- Builds on `day2-information-spaces` (I-maps, sufficiency) and `day2-sensor-lattices` (refinement order on partitions — same "coarsest that works" logic, now with dynamics).
- Sets up `day3-filters-plans-and-reduction-algorithms` (computing/minimizing filters; complexity).
- The docking project is a running example (reactive policy on a 4-state ITS).

## 🎯 Likely exam points
- *What information must be preserved?* — explain collapsing histories via **quotient transition systems** (labelling → merge → consistency).
- Define **sufficient I-map** and **minimal sufficient I-map**; give the parity (2-state) example.
- **Passive vs active tasks** → filtering vs planning; why active tasks still need a filter.
- Define **policy** and **reactive policy**; when does reactivity suffice (and when is memory unavoidable)?
- How cost/reward framing connects I-spaces to **DP and RL**.

## 📝 In-class notes (raw — Jun 10)
- Refinements; approximate information spaces; policies in robotic systems.
- Collapsing histories while keeping something useful — what to preserve?
- Transition system; state-relabeled transition system; labelling function → **quotient transition system** (which states are useful to distinguish).
- Internal system = **Information Transition System (ITS)**; **History ITS**; **sufficient I-map**; **minimal sufficient maps**.
- Task labelling; **passive tasks** (filtering) vs **active tasks** (planning); **reactive policy**.
- Tasks as **cost/reward optimization**; mention of **reinforcement learning**.

## 📎 Slides
_Pending — drop the deck in `reading_material/lecture_slides/` and I'll reconcile the ⟵ flags._

## ❓ Open questions
- Exact consistency condition for a legal quotient (bisimulation-style?) as stated on the slides.
- Did they give an algorithm for computing the minimal sufficient ITS, or only existence/definitions?
- The precise definition of "task" used (label sequences? reachability? cost)?
