# Refinements & Approximate Information Spaces ("The Art of Forgetting")

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 lecture · Status: 🟢 **reconciled with the Lecture 6 slides** (Sakçak et al.)
> 🧮 = beginner math explainer. (This is the instructors' own research: Sakçak–Timperi–Weinstein–LaValle, *"A mathematical characterization of minimally sufficient robot brains,"* IJRR 2023.)

## TL;DR
The slides call it **"the art of forgetting"**: *how much can we collapse histories and still have something useful — what information should be preserved?* Answer: model the robot's "brain" as an **Information Transition System (ITS)**, collapse it with a **labeling/I-map κ**, require **sufficiency** (the collapse must stay consistent with the dynamics), and refine a task labeling **just until** it becomes sufficient. The headline theorem: a **minimal sufficient refinement exists and is unique** — every task has a well-defined smallest brain.

---

## 1 · The system picture (the slide everyone should memorize)
```
Physical World --(sensor h)--> y --> [ Internal System ι ] --(policy π(ι))--> u --> back to world
```
- `Y` = all possible observations, `U` = all possible actions; time is discrete, stage `k`.
- The interaction so far is the **history** `η_k = (y₁, u₁, y₂, u₂, …, u_{k-1}, y_k)`.
- The internal state `ι_k` (an **information state**) *encodes* this history.

## 2 · Background math, gently
- **Preimage / equivalence classes / partition.** For `τ : A → B`, the preimage `τ⁻¹(b) = {a ∈ A | τ(a) = b}`. The preimages form **equivalence classes** that **partition** A.
  > 🧮 Same machinery as the Day-2 sensor preimages: a function over a set slices the set into "treated-as-the-same" groups.
- **Labeled transition system** = triple `(S, Λ, T)`: states `S`, edge labels `Λ`, transitions `T ⊆ S × Λ × S`.
  > 🧮 Circles + labeled arrows. `T` is just the list of arrows: (from-state, label, to-state).
- **State-relabeled transition system** = `(S, Λ, T, σ, L)` — add a **labeling function** `σ : S → L` painting each state with a label from `L`.
  > 🧮 The label is what you *care about* at that state (an output, an action, "goal/not-goal").
- **Quotient transition system.** The preimages of `σ` partition `S` into classes `[s]_σ = {s′ | σ(s′) = σ(s)}`. Collapse each class to a single super-state: states `S/σ`, arrows inherited class-to-class. That's the **quotient** of the system by σ.
  > 🧮 The subway map: merge all individual streets (states) with the same label into one station, keep the connections. The formal bit `S/σ` just means "the set of merged groups."

## 3 · Information Transition System (ITS)
**The internal system is an ITS**: `S = (I, Λ, φ, ι₀)` —
- `I` = an information space; `ι₀` = initial I-state;
- `Λ` = edge labels — the lecture uses `Λ = Y` (observations), `Λ = U` (actions), or `Λ = U × Y` (both);
- `φ : I × Λ → I` = the **information transition function** (how the I-state updates per event).

A **state-relabeled ITS** adds a labeling `ℓ : I → L`. Three labelings matter:
| Labeling | Type | Meaning |
|---|---|---|
| **I-map** | `κ : I_hist → I` | "compress histories to derived I-states" |
| **Policy** | `π : I → U` | "what to do in each I-state" |
| **Task labeling** | `κ_task : I_hist → {0,1}` | "is this history task-accomplishing?" |

**History ITS** `S_hist = (I_hist, U×Y, φ_hist, ())` — states are whole histories; the transition is just **concatenation** `η_k = η_{k-1} ⌢ (u_{k-1}, y_k)`. Maximal information, but **impractical: it grows linearly forever** → we derive smaller ITSs from it via κ.

## 4 · Sufficiency — the exact condition ⭐
> **Definition (slide 11):** κ is **sufficient** iff for all histories `s, t` and every event `λ`:
> `κ(s) = κ(t)` and `s′ = φ(s,λ)`, `t′ = φ(t,λ)` **⟹** `κ(s′) = κ(t′)`.

> 🧮 **In words:** if the compressed brain treats two histories as *the same*, then after experiencing the *same next event*, it must **still** treat the results as the same. The collapse must never need un-forgetting.
> **Parity check:** histories "2 doorways" and "4 doorways" both map to EVEN. After one more doorway both become ODD — same derived state ✓. Sufficient. A collapse mapping "2 doorways" and "3 doorways" to one state would break instantly (next doorway sends them to different answers) ✗.
>
> Plus the second requirement: κ must **preserve crucial task information** — histories that the task needs distinguished stay distinguished.

## 5 · Minimal sufficient refinement (the headline) ⭐
The natural starting point is the **task labeling itself** (label each history by, e.g., which action to take, or accomplishing/not). **This is typically NOT sufficient.** Fix: **refine** it — split its classes — *just until* sufficiency holds.

> **Definition:** a **minimal sufficient refinement** of κ is a sufficient `κ′` such that **no** sufficient `κ″` sits strictly between: `κ′ ≻ κ″ ⪰ κ`. (`≻` = "is strictly finer than," the same refinement order as the sensor lattice.)
>
> **Theorem (Sakçak–Timperi–Weinstein–LaValle 2023):** minimal sufficient refinements **exist and are unique** in a general setting.

> 🧮 **Why this is a big deal:** "the smallest brain for the task" is not just poetry — it's a **well-defined, unique mathematical object**. You start from *what the task cares about* (too coarse) and add only the distinctions the dynamics force on you; the process bottoms out in exactly one place.

### Worked example from the slides — the two gates 🟥🟩
Setup: a robot circulates past two gates, **red** and **green** (`Y = {r, g}`, histories = strings of r/g). **Task:** *"is the robot crossing the gates consistently (going cw the whole time, or ccw the whole time)?"* — a passive task, `κ_task : I_hist → {0,1}`.
- The history ITS is an infinite binary tree: (), (r), (g), (r,r), (r,g), …
- `κ_task` alone (just "consistent so far? yes/no") is **not sufficient** — knowing "yes" isn't enough to update: you also need *which gate came last* (consistent-ending-in-r behaves differently from consistent-ending-in-g on the next observation).
- Refining until sufficient yields **4 states**: `ι₀` (start), `ι_r` (consistent, last saw red), `ι_g` (consistent, last saw green), `ι_nt` (not consistent — absorbing). The infinite tree **quotients down to a 4-state machine**, and `κ_task` factors through it: `κ_task = κ″ ∘ κ′` (first compress to the 4 states, then read off yes/no).
> 🧮 This is the parity example's big sibling: task label alone too coarse → forced to remember *one extra fact* (last gate) → done. Minimal, unique.

## 6 · Tasks: passive vs active (now formal)
- **Passive task** = maintain the **label** of the history as it grows → **filtering**.
- **Active task** = make the realized history of the **coupled system** land in the desired set `κ_task⁻¹(1)` → **planning**.
- The **coupled system** `S_π ⋆ X_h` pairs the internal ITS with the external world: `x_{k+1} = f(x_k, u_k)`, `y_k = h(x_k)`, `ι_k = φ(ι_{k-1}, y_k)`, `u_k = π(ι_k)` — brain and world driving each other in a loop, state space `I × X`.
- A policy is **feasible** if **every** possible initialization of the coupled system yields a task-accomplishing history.
- Tasks can also be specified by logic or **cost/reward** (§8) — "with caution," per the slides.

## 7 · Minimally sufficient structures (the 2024 results)
Two "what's the least…?" questions (Sakçak–Weinstein–Timperi–LaValle, WAFR 2024):
- **Minimal policy:** the smallest ITS that can *represent* a given feasible policy. Formalized via "**supports**": ITS `S` supports the history policy iff relabeling its states with actions reproduces the same input→output behaviour (🧮 — this is exactly Wednesday's **Output Simulation** in ITS clothing). **Theorem:** S supports π iff S is a **quotient** of the (policy-restricted) history ITS by a sufficient `κ ⪰ π` — and the **minimal one exists, is unique: the minimal sufficient refinement of π**.
- **Minimal sensor:** fix the brain to be *memoryless* — `I = Y`, i.e. the I-state IS the latest observation (a **reactive policy**). **Theorem:** a sensor `h` is sufficient for a reactive policy **iff `h ⪰ π_X`** for some feasible state-feedback policy — the sensor must *dominate* (refine) the policy's action-partition. And such a `π_X` exists iff some feasible policy applies the **same action at a state regardless of stage**.
> 🧮 **Reading the sensor result with our robot:** the docking policy needs to distinguish only {steer-left / steer-right / forward / re-scan}. Any sensor whose partition refines *that 4-way split* suffices — our two photodiodes do. The sensor-lattice `⪰` from Day 2 turns out to be exactly the right yardstick for "is this sensor enough for a reflex agent?"

Slide example — **Maze, Mouse & Cheese 🐭🧀**: actions `U = {→, ←}`, histories = action strings, `κ_task` labels cheese-reaching sequences 1 (mouse teleports back on exiting). Tiny world where you can compute these minimal objects by hand.

## 8 · Tasks as cost/reward → DP → (approximate) RL
- Add a **reward `r_k`** each stage; the task = maximize cumulative reward `J(π) = E[Σ r_k]`.
- **Dynamic-programming recurrence:** `V_k(η_k) = max_u E[ r_k + V_{k+1}(η_{k+1}) | η_k, u_k ]` — an optimal policy satisfies it. 🧮 *"The value of now = best (immediate reward + value of where that lands me)."* Computed over histories it's intractable — so when may we run DP on the **compressed** states instead?
- **Sufficiency for DP** (Subramanian–Sinha–Seraj–Mahajan, JMLR 2022 — the **approximate information state**): κ must be
  1. **sufficient for performance evaluation:** `E[r_k | η_k, u_k] = E[r_k | κ(η_k), u_k]` — 🧮 *the summary predicts today's reward as well as the full history would;*
  2. **sufficient for prediction:** `P(ι_{k+1} | η_k, u_k) = P(ι_{k+1} | κ(η_k), u_k)` — 🧮 *the summary predicts tomorrow's summary.*
  Hold both ⟹ planning/learning on the compressed brain loses nothing. **This is the bridge to RL:** agents with memory are *learning* an approximate κ with these two properties.

## Why it matters for *minimalism*
The week's thesis as theorems: the smallest brain for a task **exists, is unique** (minimal sufficient refinement), comes from **quotienting** histories, and the **sensor needed for a reflex agent is characterized by dominance** — minimal brains and minimal sensors are two faces of the same refinement order.

## Connections
- `day2-information-spaces` (histories, I-maps) · `day2-sensor-lattices` (the `⪰` order does double duty) · `day3-filters-plans-and-reduction-algorithms` (computing these objects = NP-complete in general; Output Simulation ↔ "supports") · `day4-information-invariants` (trading the resources that *supply* the information).
- References: Sakçak+ 2024 (WAFR), Sakçak+ 2023 (IJRR "minimally sufficient robot brains"), Weinstein+ 2022 (enactivist model of cognition), Subramanian+ 2022 (JMLR).

## 🎯 Likely exam points
- Define **(state-relabeled) transition system** and **quotient** (merge label-equivalence classes, inherit arrows).
- **ITS** `(I, Λ, φ, ι₀)`; the **History ITS** (concatenation; maximal but grows forever).
- State the **sufficiency condition** (κ(s)=κ(t) ∧ same event ⟹ κ(s′)=κ(t′)) and check it on a small example (parity / gates).
- **Minimal sufficient refinement**: definition via `κ′ ≻ κ″ ⪰ κ`, and **existence + uniqueness**.
- **Passive vs active** tasks (filtering vs planning; coupled system; feasible policy).
- **Minimal sensor for a reactive policy ⟺ `h ⪰ π_X`** (sensor dominance meets policies).
- DP recurrence + the **two sufficiency conditions** for planning on compressed states (reward + prediction) → approximate information state / RL.

## 📝 In-class notes (raw — Jun 10/11)
- Refinements, approximate I-spaces, policies; collapsing histories ("art of forgetting"); what to preserve.
- Transition system; state-relabeled TS; quotient TS via labeling functions.
- ITS; History ITS; sufficient I-map; minimal sufficient maps; task labeling; passive (filtering) vs active (planning); reactive policy; cost/reward; RL mention.

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture 6_ Refinements.pdf`** (30 pp). All earlier ⟵ flags resolved: the quotient condition is the sufficiency implication above; minimal sufficient refinements exist & are unique (2023); tasks defined via `κ_task` labelings (binary for planning); DP/RL connection via the approximate-information-state conditions.
