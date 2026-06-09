# Embodiment × Minimalism

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Lecture · Fort TS128
> Status: 🟢 **reconciled with the Lecture 4 slides** (Jun 9) · 🧮 = beginner explainer

## TL;DR
The robot's **physical body** can do work that would otherwise need sensing, computation, or control. Exploiting the body = a route to minimalism: **let the morphology compute.** Today's lecture focused on **embodied control** — the body doing part of the controlling, not just a software "brain."

## Embodied control — the lecture's focus ✅
**Embodied control** = letting the **body and its interaction with the world** do part of the controlling, instead of a central "brain" doing it all in software.

> 🧮 **Plain version.** The usual control loop is *sense → compute → actuate*, run on a processor. In **embodied control**, the **physics of the body** (shape, springiness, damping, contacts) closes part of that loop *mechanically* — so the software controller can be simpler, or sometimes absent. The body isn't just *moved by* the controller; it **is** part of the controller.

- **Why it's minimal:** every bit of control the body handles for free is sensing/computation you don't have to build → fewer parts, less code, more robustness.
- **A spectrum:** *all-brain* (sense everything, compute everything) ⟷ *all-body* (a passive dynamic walker: zero control, mechanics do it). Real designs sit in between; minimalism pushes toward the body end where the task allows.
- ✅ **Slide framing:** *understanding embodied intelligence helps us **shift information processing from the "brain" to the body** → **reduces explicit computational requirements*** (Iida, Sirithunge, Maiolino & Hughes, 2025, *"Foundations of Embodied Intelligence for Robotic Systems"*).
- 🔗 **Our docking plan is embodied control:** the **funnel + magnet** align and hold the robot *mechanically* — no controller computes the final pose (see [`../project/docking-station.md`](../project/docking-station.md)).

## Key concepts
- **Morphological computation** — shape, materials, and mechanics perform "computation" for free (no code, no sensors).
- **Passive dynamics** — e.g. **passive dynamic walkers** that walk down a slope with no motors or control.
- **Biological examples (raised in the Minimalism-as-philosophy lecture):** 🪳 **cockroach** running is stabilized by body mechanics ("preflexes") with no neural feedback; 🐟 a **trout** can hold station / swim upstream by exploiting **vortices** (the Kármán gait) with minimal muscle effort — body + environment doing the control. See `day2-minimalism-as-life-philosophy`.
- **Mechanics replacing sensing** — the tray's walls funnel a part (`tray-tilting`); a gripper's compliance aligns an object without measuring it.
- **Reactive wiring** — Braitenberg vehicles get behaviour from body+wiring, not deliberation.
- Trade-off: cleverer **body** ⇄ simpler **brain/sensing**. This is the seed of **co-design**.

## Why it matters for *minimalism*
Embodiment is a resource like any other. Offloading work to the body lets you delete sensors/computation — directly shrinking the robot.

## From the slides (Lecture 4) 📊
**Embodiment** = *having a physical body*; an **embodied agent** has *meaningful sensory-motor interactions with the environment.*

**Embodied intelligence** — a broad field (human experience, biology, robotics, even **dance**; the EI conference). Core idea: **move information processing from the brain to the body → less explicit computation** (Iida et al., 2025).

**Ways the body buys minimalism (the lecture's categories):**
- **Geometry** — *visibility & reachability*; **compliance, friction/stiction** for manipulation. (Goldberg, *"Orienting polygonal parts without sensors,"* 1993 — a sensorless classic, cf. `tray-tilting`.)
- **Dynamics** — **funnel chaining** in control; oscillations & fixed points; **passive dynamic walkers**.
- **Expressivity** — an information-theoretic measure of the static & dynamic states a body can take.

**Proprioception vs exteroception** — sensing *internal* states vs the *external* world. _(Your robot's stepper step-count = proprioception; its light sensors = exteroception.)_

**Example smorgasbord:** embodied wall-following; minimal directed flight (origami solar microfliers — Johnson et al., *Science Robotics* 2023); soft robots / **passive fish**; collective effects (**Brazil-nut effect**, collective Braitenberg vehicles).

🔗 **The lecture literally closed on "connections to docking?"** — embodiment is exactly our **funnel + magnet** frame: let the body finish the job.

## Connections
- Pays off `tray-tilting`, `braitenberg-vehicles`; sets up `co-design` (Thu).

## 🎯 Likely exam points
- Define morphological computation; give a concrete example (passive walker, compliant gripper, tray).
- Explain the body ⇄ brain trade-off in minimal design.
- Define **embodied control** (the body/physics doing part of the control loop) vs software-only control; place an example on the all-brain ↔ all-body spectrum.

## 📝 In-class notes (raw — Jun 9)
- Lecture: **Embodiment × Minimalism**, focused on **embodied control**.
- _(add: the exact definition/framing, examples, videos or systems shown — and how they formalised "the body doing control")_
- 📎 **Reconciled** against `reading_material/lecture_slides/Lecture 4_ embodiment-slides.pdf` (33 pp).

## ❓ Open questions
-
