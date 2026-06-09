# Minimalism as a Life Philosophy (Lecture 1)

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 2 · Tue Jun 9 · Opening lecture · Fort TS128
> Status: 🟢 **reconciled with the Lecture 1 slides** (Jun 9) · 🧮 = beginner explainer

## TL;DR
The "why" lecture: minimalism as a **research stance** — *what are the fewest resources necessary to perform a task?* — set in its **history**, with biological and historical examples where less is more.

## The core question (slides)
> **"What are the fewest resources necessary to perform some task?"**
- A natural **theoretical** question · practically useful · intellectually deep · **remains mostly open**.
- 👁️ **The Graeae** metaphor — three Titan sisters (Deino, Enyo, Pemphredo) who **share a single eye and a single tooth**, passing them around: doing the job with the bare minimum.

## A short history of minimalism in robotics (slides)
A lineage of workshops:
- **ICRA 1996** (K. Goldberg & A. Bicchi) — gave the working **definition**:
  > *minimalism* = **"the pursuit of the least complex solution to a given class of tasks"** — e.g. the **fewest actuators / control variables (DOF)**, or the **simplest set of sensors**.
- **RSS'08** (Ghrist, LaValle, Pappas) · **RSS'16** "Minimality + Design Automation" (Censi, O'Kane, **Shell**) · **RSS'17** "Minimality and Trade-offs in Automated Robot Design" (Censi, Kress-Gazit, **Nilles**, O'Kane).
- (Your instructors **Nilles & Shell** are part of this lineage.)

## Key observations & references — now confirmed ✅
- **"More capable robots don't always make life easier."**
  → ✅ **T. Smithers (1994), _"On why better robots make it harder,"_** *From Animals to Animats: Simulation of Adaptive Behavior*, pp. 64–72.
- **"Constraints give different regimes"** · *"Creativity arises from constraints."*
  → ✅ **P. Cheeseman et al. (1991), _"Where the Really Hard Problems Are,"_** IJCAI, pp. 331–337 — the hardest instances **cluster in a narrow band** (a phase-transition view of complexity). *This is where the complexity / average-vs-worst-case discussion fits.*

## Historical & biological examples (slides)
- 🐢 **Grey Walter's Tortoises** (≈1948–51) — early minimalist robots: **analog** (vacuum tubes), a **light sensor** + a **bump-sensor shell**, yet lifelike behaviour. Ancestor of Braitenberg-style reactive robots → `day1-braitenberg-vehicles`.
- 🪳 **Cockroach locomotion** — fast, stable running from **passive mechanical self-stabilization** (Jindrich & Full, *J. Exp. Biol.*, 2006). Stability "for free."
- 🐟 **Trout locomotion** — a trout — *even a **dead** one!* — extracts energy from **vortices** to hold station / swim upstream (Beal et al., *J. Fluid Mech.*, 2006). Body + environment doing the work.
- 🤖 **"Vision-Language Models are Biased"** (Vo et al., ICML 2026) — a cautionary modern example, capped by **Feynman**: *"For a successful technology, honesty must take precedence over public relations, for nature cannot be fooled."*
- 📐 **D'Arcy Thompson's "principle of negligibility"** (*On Growth and Form*) — don't be derailed by irrelevant detail: *"if Tycho Brahé's instruments had been ten times as exact there would have been no Kepler, no Newton."* Separate the **practical working robot** from the **theoretical narrative**.

## Mentioned in discussion (not in this deck — verify)
- The **RISC** analogy (reduced instruction set → simpler can be more powerful); **time & space complexity**, **set theory**, **linear programming**, **average- vs worst-case** (the simplex example). These came up verbally; the complexity thread connects to the **Cheeseman "really hard problems"** slide above.

## Why it matters for *minimalism*
The framing for the whole week — every later topic is an instance of *"how little is enough?"*

## Connections
- Frames → `day2-information-spaces`, `day2-sensor-lattices-and-comparing-robots`, `day2-embodiment-x-minimalism`, `day4-information-invariants`, `day4-co-design`.
- Bio examples + Grey Walter → `day2-embodiment-x-minimalism` & `day1-braitenberg-vehicles`.

## 🎯 Likely exam points
- State the **core question** ("fewest resources for a task") and the **1996 definition** of minimalism (fewest actuators/DOF, simplest sensors).
- "**More capable robots don't always make life easier**" (Smithers 1994); "**constraints give different regimes**" (Cheeseman 1991, hard-problem phase transition).
- Give a **historical** minimalist robot (Grey Walter's Tortoise) and a **biological** one (cockroach self-stabilization / dead-trout vortex gait).

## 📝 In-class notes (raw — Jun 9)
- History + philosophy of minimalism; "simple robots"; the **Graeae** (shared eye/tooth).
- Refs: Smithers 1994, Cheeseman 1991, Goldberg/Bicchi 1996 definition; Grey Walter's Tortoises; D'Arcy Thompson; VLM-biased + Feynman.
- (Verbal) RISC; time/space complexity; set theory; linear programming; average vs worst-case.
- Cockroach & trout locomotion.

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture 1_ minimalism_as_a_life_philosophy.pdf`** (36 pp).

## ❓ Open questions
- Was RISC / LP / average-vs-worst-case on a slide I'm missing, or purely verbal elaboration?
