# Information Invariants ("Theory of Information Invariants")

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 4 · Thu Jun 11 · Lecture · Fort TS128
> Status: 🟢 **reconciled with the Lecture 8 slides** · 🧮 = beginner explainer
> Foundations: **Donald, "On Information Invariants in Robotics," Artificial Intelligence 72:217–304, 1995** · **Donald, Jennings & Rus, "Minimalism + Distribution = Supermodularity," JETAI 1997**.

## TL;DR
The deepest version of the workshop's question: **what is the irreducible information a task needs, and what resources can be traded to supply it?** Donald's machinery: write sensor systems as **equations** you can rearrange (a beacon + compass + a message ≅ a goal-direction sensor), price the trades in **bit-seconds**, model everything as **sensori-computational circuits** *situated in space*, and account honestly for **calibration**. Today's examples: **platooning, navigation, manipulation**.

---

## 1 · The agenda, in Donald's own words (exam-quotable)
> *"For a given robotics task, find the minimal configuration of resources required to solve the task. Thus, minimalism attempts to reduce the **resource signature** for a task, in the same way that Stealth technology decreases the radar signature of an aircraft. Minimalism is interesting because **doing task A without resource B proves that B is somehow inessential to the information structure of the task**."* — Donald et al. (1997)

And the methodological bet (Donald 1995): **spatially distributing resources among collaborating agents makes the information characteristics of a task explicit** — just as *parallelizing an algorithm teaches you its structure* in computer science.

## 2 · The resource currencies
A task's information budget can be paid in different currencies — and converted between them:

| Currency | Spend it to… |
|---|---|
| **Sensing** | measure directly |
| **Computation** | infer what a sensor would have said |
| **Communication** | be told (by a peer, a beacon) |
| **Motion / time** | move (or wait) to create the information |
| **Prior knowledge / calibration** | bake it in beforehand |

> 🧮 **"Invariant" = what's conserved.** Across all designs that solve a task, the hardware varies wildly but the **information that must flow does not**. Like energy changing form (kinetic ⇄ potential ⇄ heat), information changes form (sensing ⇄ comms ⇄ motion) while the total requirement stays fixed.

## 3 · Platooning — Tommy & Lily 🚗🚗 (the developed example)
Leader **Tommy**, follower **Lily**. Lily must keep station behind Tommy. Three designs that supply the *same* information:
1. **Tommy slows down** so Lily can follow by line-of-sight. *Cost: Δt* (time — the detour via p′ rather than p).
2. **Tommy sends a "tighten up" message.** *Cost: |M_tighten|* (message bits).
3. **Tommy transmits his position p.** *Cost: |M_p|* (more bits).

> 🧮 **The punchline: costs are measured in **bit-seconds*** — information and time on a *common axis*, so "slow down" (pay time) and "send a message" (pay bits) become **commensurable**. That's what makes "trade motion for communication" a calculation rather than a metaphor.

## 4 · Navigation — the lighthouse and sensor *arithmetic* 🗼 ⭐
Task: orient toward a goal — defined via a hypothetical **goal-orientation sensor**. The construction: a **lighthouse beacon** + a **receiver** on the robot + a **compass** ("local north") + simple angle bookkeeping (the slides' relation `π = HA − BR + θ_R`) yields the goal direction.

Donald writes such constructions as **equations between sensor systems**:
```
EG ≅ HG + h_r              EG ≅ HG* + comm(θ_r)
```
> 🧮 **How to read "sensor arithmetic":** "the goal-orientation sensor **EG** can be *simulated* by (≅) the heading sensor **HG** *plus* a small extra resource" — where the extra is a local sensor (`h_r`) in one design, or a **communication** of an angle (`comm(θ_r)`) in another. Like algebra: rearrange resources across the `≅` until the design is cheapest. Each valid equation IS an information invariant — the same information content expressed in different hardware.
>
> 🧮 **Our robot is literally this example:** strobe beacon (lighthouse) + two photodiodes (receiver) + steering arithmetic ≅ a "direction-to-dock sensor" we never installed.

## 5 · Manipulation
Third developed example (Donald et al. 1997): cooperative **pushing/reorienting** with minimal robots — motion + contact mechanics paying the budget that "proper" sensing would otherwise pay (the tray-tilting lineage, scaled to teams).

## 6 · Sensori-computational circuits (s-circuits)
The formal object (1997, verbatim essence):
> *"Units of organization called **circuits**, modeled as **graphs**. **Vertices** = sensori-computational components; **edges** = the data paths through which information passes. Circuits can be transformed by changing edge or vertex structure. Different **immersions** of the graphs correspond to different **spatial allocations** of resources. An important class of transformations consists of **permutations** (a vertex permutation followed by an edge permutation)."*

> 🧮 **Plain version:** draw the robot team's information flow as a wiring diagram, but **pinned to physical space** — each component sits *somewhere* (that's the "immersion"). Now redesign = graph surgery: re-wire edges, or **permute** which component sits on which body. The astonishing observation from the summary slide: **when sensing is spatially distributed, permuting resources can *add* information** — moving the same parts to different places yields strictly more knowledge. *Where* information lives matters, not just *what* you have.

## 7 · Supermodularity 🧩
> **Definition (1997):** *"A circuit is **supermodular** if it can be relocated to a different physical location and still function correctly — even in the absence of circuits that formerly surrounded it and in the presence of new circuits at this new location."*

> 🧮 A supermodular component is a **true plug-and-play module**: unplug it from one robot/place, drop it elsewhere, it still works — no hidden dependence on its old neighbourhood. Hence the paper's slogan-title: **"Minimalism + Distribution = Supermodularity"** — pushing for minimal, spatially-distributed designs forces components to be honest, self-contained modules.

## 8 · Calibration complexity — the honesty rule ⭐
> **Definition (Donald 1995):** *"Consider two sensor systems S and Q. When S and Q require equivalent installation calibration, and when the calibration required to install Q is necessary to specify S, we say **S dominates Q in calibration complexity**."*

> 🧮 **Why this matters:** trades can hide costs. A beacon looks "free" at runtime, but someone had to *install and calibrate* it (shared frames, alignments). Donald's dominance ordering counts that **set-up information** so comparisons stay fair — you can't win the minimalism game by smuggling information in through calibration. (This resolves the open caveat from the sensor-lattice lecture: "we ignored the cost of g.")

## 9 · Follow-up work (slides)
- **Zhang & Parker (ICRA 2010):** dynamic optimization over a *team's* resource allocation, inspired by Donald's permutations — task allocation at the level of **information components**.
- **Ahmed (2010, TAMU thesis):** real beacon implementations differ in **noise** → equivalence should consider uncertainty; propagate error values through the s-circuit DAG.

## Why it matters for *minimalism*
This is the workshop's theoretical backbone: it turns *"how little is enough, and what can substitute for what?"* into **equations with priced trades** — and the whole week now chains together:
info spaces (what's knowable) → sensor lattices (compare sensors) → minimal sufficient ITS (smallest brain) → filter reduction (compute it, NP-complete) → **information invariants (trade any resource for any other, fairly priced)**.

## Connections
- `day2-sensor-lattices` (dominance/simulation — now across all resources, with calibration counted).
- `day3-filters-plans-and-reduction-algorithms` (Output Simulation = the runtime face of these reductions).
- `day2-tray-tilting` / `day2-embodiment-x-minimalism` (motion & mechanics as currencies).
- **Our project, framed for the result seminar:** docking pays with a beacon (communication) + photodiodes (cheap sensing) + funnel & magnet (embodiment); mapping pays with motion + odometry + prior arena knowledge. Both are information-invariant arguments in action.

## 🎯 Likely exam points
- The Donald 1997 **minimalism/Stealth/resource-signature** quote and the logic: *doing task A without resource B proves B inessential to the task's information structure*.
- **Platooning (Tommy & Lily):** three designs (slow down / "tighten up" / transmit p), their costs, and **bit-seconds** as the common unit.
- **Sensor equations** `EG ≅ HG + comm(θ_r)`: simulating one sensor with others + communication — write/read one such reduction.
- **S-circuits** (graph of components & datapaths, *immersed* in space; permutations; distributed sensing — permutation can ADD information).
- **Supermodularity** definition + "Minimalism + Distribution = Supermodularity."
- **Calibration-complexity dominance**: why fair comparisons must count installation information.

## 📝 In-class notes (raw — Jun 11)
- Information invariants; platooning, navigation, manipulation.

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture 8_ Information Invariants.pdf`**. All earlier ⟵ flags resolved (the trades per example, the reduction notation, and the calibration bookkeeping are now exact).
