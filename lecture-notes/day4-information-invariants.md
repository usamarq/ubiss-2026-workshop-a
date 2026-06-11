# Information Invariants

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 4 · Thu Jun 11 · Lecture · Fort TS128
> Status: 🟢 in-class notes added (Jun 11) · **slides pending** → inferred parts **⟵ verify w/ slides**
> 🧮 = beginner explainer. (Foundational paper: **Bruce Donald, "Information Invariants in Robotics," Artificial Intelligence, 1995**.)

## TL;DR
The deepest version of the workshop's question: **what is the irreducible amount of information a task needs, and what resources can be traded for one another to supply it?** Donald's answer: treat **sensing, computation, communication, and motion** as *interchangeable currencies*, and use **reductions** (à la complexity theory) to prove when one robot can do whatever another can. Today's three running examples — **platooning, navigation, manipulation** — each show a different trade.

---

## 1 · The core idea
- Every task has an **inherent information requirement** — a "budget" of information that *must* be acquired to succeed, no matter the design.
- That budget can be **paid in different currencies**:

| Currency | Spend more of it to… |
|---|---|
| **Sensing** | measure the world directly |
| **Computation / memory** | infer what a sensor would have told you |
| **Communication** | get the info from someone/something else (a beacon, a peer) |
| **Motion / action** | move to *create* the measurement (sensorless-manipulation style) |
| **Prior knowledge** | bake the info into the design ahead of time |

> 🧮 **The slogan:** *information can be "stored" in any of these, and converted between them.* A task doesn't care **how** you supply its information budget — only that you do. Minimalism = pay the budget in the **cheapest available currency**.

## 2 · Information invariants = what's conserved across designs
> 🧮 **Why "invariant"?** Across all the different robot designs that solve a given task, *something stays constant* — the underlying information requirement. The hardware, the sensors, the code all change; the **information that must flow** does not. That conserved quantity is the **information invariant** of the task. (Analogy: energy is conserved while it changes form — kinetic ⇄ potential ⇄ heat. Here information changes form — sensing ⇄ comms ⇄ computation ⇄ motion — but the task's total requirement is conserved.)

## 3 · Reductions: "simulate one robot with another" ⭐
The formal engine (this connects Tue's sensor lattices + Wed's Output Simulation):
- To show **robot/resource A is at least as powerful as B**, give a **reduction**: a construction that makes A **simulate** B — possibly by adding computation, motion, or communication.
- 🧮 **Just like complexity theory:** "problem X reduces to Y" means "if you can solve Y, you can solve X." Here: "sensor/robot B reduces to A" means "with A (+ some glue resource) you can do whatever B does." Build enough reductions and you get a **partial order of robot power** — exactly the `sensor-lattices` dominance order, now spanning *all* resources, not just sensors.
- Donald's reductions are **resource-explicit**: they account for the *cost* of the glue (the computation/comms/motion you add) — answering the caveat the sensor-lattice lecture left open ("we ignored the cost of `g`").

## 4 · The three examples (today's lecture)
> ⟵ verify w/ slides for the exact constructions; here's what each example *demonstrates*:

- 🚗 **Platooning** (cars/robots following in a line) — the headline **sensing ⇄ communication** trade. A follower can **measure** the gap to the car ahead (sensing), *or* the leader can **broadcast** its speed/position (communication) and the follower computes the gap. Same task, information sourced two different ways. Also classic **sensing ⇄ computation** (estimate vs measure) and the role of **shared coordinate frames**.
- 🧭 **Navigation** (get from A to B) — **sensing ⇄ motion/prior-knowledge**. With a rich map (prior knowledge) you need little sensing; with no map you must **sense more or move to explore**. "Information left in the environment" (landmarks, your own breadcrumbs) substitutes for onboard sensing. *(Our mapping task is exactly this: we let motion + a known arena substitute for rich perception.)*
- 🤏 **Manipulation** (orient/place a part) — **sensing ⇄ motion**, the sensorless-manipulation story: **tray tilting** and squeeze-grasps pay the information budget with *clever motion + mechanics* instead of sensors. (Ties `tray-tilting`, `embodiment`.)

## 5 · "Calibration" / the universal-reduction caveat
Donald is careful that reductions can **hide costs** — e.g. a "free" communication channel presumes a **shared frame / calibration**, which is itself information that had to be established somehow. A fair comparison must **account for the calibration/installation information**, not just the runtime sensing. (This is the rigorous version of yesterday's "we are ignoring the cost of computing g.") **⟵ verify w/ slides for the exact bookkeeping**

## Why it matters for *minimalism*
This is the **theoretical backbone** of the whole week: it turns "how little is enough, and what can replace what?" into a **formal, provable** question, and unifies every earlier lecture —
- info spaces (what's knowable) → sensor lattices (compare sensors) → ITS/sufficiency (minimal memory) → filter reduction (compute it) → **information invariants (trade *any* resource for any other)**.

## Connections
- `day2-sensor-lattices` (dominance/simulation — now across all resources, with costs counted).
- `day3-filters-plans-and-reduction-algorithms` (Output Simulation = the runtime-behaviour version of a reduction).
- `day2-tray-tilting`, `day2-embodiment-x-minimalism` (motion/body paying the info budget).
- **Our project:** docking pays its budget with cheap sensing (2 photodiodes + 1 hall bit) + **embodiment** (funnel, magnet) + **communication** (the strobe beacon = info broadcast to the robot); mapping pays with **motion + odometry + prior knowledge of the arena**. Both are *information-invariant arguments* in disguise — say so in the result seminar.

## 🎯 Likely exam points
- State what an **information invariant** is (the conserved information requirement of a task; resources are interchangeable currencies).
- Give a concrete trade in each mode: **sensing ⇄ communication** (platooning), **sensing ⇄ motion** (manipulation / navigation).
- Explain **reduction between robots/sensors** by analogy to complexity-theory reductions; how it yields a *power ordering*.
- The **hidden-cost / calibration** caveat: fair reductions must count the glue (computation, comms setup, shared frames).

## 📝 In-class notes (raw — Jun 11)
- Information invariants (Donald 1995); information requirement of a task; trading sensing ⇄ computation ⇄ communication ⇄ motion.
- Examples: **platooning, navigation, manipulation**.
- _(add: exact definitions/diagrams, the reduction formalism, any hierarchy, the calibration bookkeeping)_

## 📎 Slides
_Pending — drop the deck in `reading_material/lecture_slides/` and I'll reconcile the ⟵ flags._

## ❓ Open questions
- Donald's exact formal definition of an information invariant / the reduction (the "≥" relation) as stated on the slides.
- For each example (platooning/navigation/manipulation): the specific resources traded and the construction shown.
- How explicitly did they connect this to Tue's sensor lattices and Wed's Output Simulation?
