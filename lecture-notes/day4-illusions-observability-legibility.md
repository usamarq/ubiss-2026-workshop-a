# Illusions, Observabilities, Legibilities

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 4 · Thu Jun 11 · Lecture · Fort TS128
> Status: 🟢 **reconciled with the Lecture 9 slides** · 🧮 = beginner explainer
> (Recent research of the instructors: Suomalainen–Nilles–LaValle 2020 "VR for robots"; Medici–LaValle–Sakçak 2025 "sensor-induced illusions".)

## TL;DR
Information states **hide** things: with a weak sensor, different worlds look identical (indistinguishability). That cuts two ways — an adversary (or a designer!) can **manipulate** what a robot believes by controlling its stimuli (**illusions**, VR-for-robots), and an observer watching a robot faces the mirror problem of inferring its goal (**plan recognition**), which the robot can make easy (**legibility**) or hard. One lecture, three perspectives on the same gap between *world* and *information state*.

---

## 1 · Indistinguishable environments
Back to the colored grid world, but now the I-space is **the set of possible *worlds***:
- Robot has only a **red detector**; the task: *determine which environment you're in* — i.e., **drive the I-state down to a singleton**.
- With a weak sensor, some environments are **indistinguishable** — no observation sequence ever separates them. (A second variant: a robot with an x-y position sensor — different hidden world, same story.)

> 🧮 **This is preimages over worlds.** Day 2's preimages grouped *states* a sensor can't tell apart; here whole **environments** group together. If two worlds produce identical observations under your sensor and policy, your I-state contains both forever — no amount of cleverness fixes a sensing gap.
>
> 🧮 **Our mapping task IS this slide:** "disk or triangle?" = two candidate worlds; the run succeeds exactly when the evidence collapses the task I-state to a singleton. Our corner-counting strategy is engineering *distinguishability* on purpose — choosing motions whose observations differ between the two worlds.

## 2 · Controlling perceptions — illusions & VR for robots 🥽
If a robot's knowledge comes only through its sensors, then **whoever controls the stimuli controls the belief**:
- VR for **humans** (the slides' fun example: Juho navigating a robot in an apocalyptic world), VR for **rodents** (classic neuroscience rigs) → **VR for robots** (Suomalainen–Nilles–LaValle, IROS 2020).

### The producer–receiver formalism (LaValle et al. 2024)
Two agents share one physical world `x_{k+1} = f(x_k, u_p, u_r)`:
- the **receiver** — the ordinary robot (sensor `h_r`, internal ITS `φ_r`, policy `π_r`);
- the **producer** — an agent whose *actions shape what the receiver senses* (it "produces" stimuli).

The receiver reasons with a **model** of the world `(X̄, U, f̄, h̄, Y)` (possibly nondeterministic, `f̄ : X̄×U → pow(X̄)`) and a **model relation** `M ⊆ I × X̄`:
> **Plausible I-state:** `ι_r` is **plausible** if there exists a world state `x` with `(ι_r, x) ∈ M` — i.e. the belief is consistent with *some* world allowed by the model. (`ι_r = ∅` — believing in *no* possible world — is the canonical *implausible* state: the robot would know something's wrong.)

> 🧮 **The illusion game:** the producer may fool the receiver **as long as every belief it induces stays plausible** — the receiver's own model never flags a contradiction. The slides' "**evil producer**" controls the lighthouse-tower intensities and bends a robot's localization without it noticing. Notice the design flip: VR-for-robots is the *benevolent* version (test a real robot in a synthetic world); the evil producer is the *adversarial* one — same math.

## 3 · Regulating perceptions — belief puppeteering (Medici–LaValle–Sakçak 2025)
The producer doesn't just fool the robot — it **steers** it. Toy dynamics from the slides:
```
x_{k+1} = x_k + π_r(ι_k)     ← the robot moves per ITS own policy
ι_{k+1} = ι_k + u_p          ← the producer nudges the robot's BELIEF directly
```
**Problem:** choose the producer inputs `u_p` to bring robot-and-belief to a goal, subject to (1) **every intermediate `ι_k` stays plausible** (the illusion must never be detectable) and (2) at the end, **belief = truth** (`ι_N = x_N` — hand the robot back an honest state).
> 🧮 **Puppeteering with belief-strings:** the producer never touches the robot — it nudges the *belief*; the robot's own controller, reacting to the (false) belief, produces the motion. The slides cast finding `u_p` as a standard **optimal-control problem** (quadratic costs, bounded inputs, the receiver's disturbance model respected) — illusions become a *control engineering* discipline, not a hack.

## 4 · The observer's side: plan & goal recognition 👀
Flip the roles: now *we* watch a robot — **what is its goal/plan?** (the "observer" box in the system picture).
- Slide example (Ramirez & Geffner 2009, *plan recognition as planning*): candidate goals `C, I, K` on a grid; observations "A→B" then "F→G" arrive in order; which goals are **consistent**? (An action sequence *satisfies* an observation sequence if it contains it in order.) Recognition = planning run backwards: ask which goals admit plans matching what was seen.

## 5 · Predictability vs legibility ⭐ (Dragan–Lee–Srinivasa 2013)
Two properties of robot motion that sound alike and are **not the same** — they're *opposite mappings*:

| | **Predictability** | **Legibility** |
|---|---|---|
| Direction | **goal → trajectory** | **trajectory → goal** |
| Question | "knowing the goal, does the robot move as I'd expect?" | "watching the motion, how fast can I infer the goal?" |
| Measure | gap between actual and expected trajectory | **time** until the observer pins the true goal |
| Maximized by | the cost-minimizing (efficient) trajectory | motion that makes the correct goal **maximally probable from a snippet** |

> 🧮 **The reaching example:** two bottles on a table. The **predictable** reach is the efficient straight line — but for a long while it's ambiguous *which* bottle. The **legible** reach **exaggerates** early — arcs wide toward the chosen bottle so a watcher knows almost immediately — at the price of efficiency. Same goal, different audiences: predictability serves someone who already knows the goal; legibility serves someone trying to find out. You generally **cannot maximize both at once**.

## 6 · The Day-1 thread, closed
Braitenberg's *uphill analysis* (Day 1): observers over-attribute inner life to simple mechanisms — behavior underdetermines mechanism. Today's lecture is that asymmetry **weaponized and engineered**: illusions exploit what a robot's I-state hides; legibility deliberately *spends* motion to close the observer's gap. Sensing limits aren't only constraints — they're a design surface.

## Why it matters for *minimalism*
- Indistinguishability tells you when a sensor is **too** minimal: the task's worlds must remain separable — the hard floor under "how little is enough."
- Illusions show information states are **objects you can manipulate** — the I-space machinery runs in *both* directions (estimate the world / fabricate it).
- Legibility prices a *communication* requirement into **motion** — an information-invariant trade (information for the *observer*, paid in trajectory cost).

## Connections
- `day2-information-spaces` (preimages, nondeterministic I-states, plausibility), `day1-braitenberg-vehicles` (uphill analysis), `day4-information-invariants` (motion ⇄ communication trade), `project/environment-mapping.md` (distinguishability is the whole game).

## 🎯 Likely exam points
- Define **indistinguishable environments**; why a weak sensor can make "which world am I in?" unsolvable (and give an example).
- **Plausible I-state** (`∃x : (ι, x) ∈ M`); the producer/receiver setup; the illusion constraint (*stay plausible throughout*).
- VR-for-robots vs the "evil producer" — benevolent vs adversarial stimulus control (same formalism).
- **Plan recognition** (consistent goals given ordered observations).
- **Predictability vs legibility**: the two opposite mappings, what each maximizes, why they conflict — the reaching example.

## 📝 In-class notes (raw — Jun 11)
- Illusions / observabilities / legibilities (lecture attended; slides supplied same day).

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture 9_ Illusions_observabilities_legibilities.pdf`** (17 pp). Refs: Medici–LaValle–Sakçak ECC 2025 · Dragan–Lee–Srinivasa HRI 2013 · Suomalainen–Nilles–LaValle IROS 2020 · Ramirez–Geffner IJCAI 2009.
