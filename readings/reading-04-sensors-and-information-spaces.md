# Reading 4 — Sensors and Information Spaces ⭐

> LaValle SM (2006). *Sensors and Information Spaces.* In: **Planning Algorithms**, Cambridge University Press, Ch. 11, pp. 559–631. (Free: planning.cs.uiuc.edu)
> Status: 🟡 basics pre-filled — **the core reading; ≈ the whole information-spaces exam objective**

## TL;DR
Defines **sensors, sensor mappings, and information spaces**, and shows how to plan when the **state is unknown** — by working with *what is knowable* instead of the state itself.

## Chapter map
- **§11.1 Discrete state spaces**
  - **Sensor** = observation space `Y` + **sensor mapping** `h`. Kinds: *state* `h(x)`, *state-nature* `h(x,ψ)`, *history-based*.
  - **Preimage** `H(y) = {x : y = h(x)}` — states consistent with a reading; preimages **partition** `X` = the sensor's resolution. Examples: odd/even, mod, sign, **selective**, **bijective** (perfect), **null** (no info).
  - **History I-state** `η_k = (η₀, ũ_{k-1}, ỹ_k)`; **history I-space**; planning defined on it (Formulation 11.1). Initial conditions: known / nondeterministic / probabilistic.
- **§11.2 Derived information spaces**
  - **I-map** `κ` compresses the history; **sufficient I-map** (update from current derived I-state + `u` + `y`, like a sufficient statistic).
  - **Nondeterministic I-space** `I_ndet = pow(X)`: I-state = **set** `X_k`. Update: **predict** `X_{k+1}=⋃_{x∈X_k} F(x,u)`, **correct** `∩ H(y)`.
  - **Probabilistic I-space** `I_prob` (a simplex): I-state = **distribution** `P(x)`. Update: **predict** = marginalize, **correct** = **Bayes' rule**.
  - **Limited-memory** I-spaces (truncate history).
- **§11.3–11.6** continuous I-spaces. **§11.7** game theory (multiple players, each with its own I-space).

## Relevance to the workshop
Source text for `information-spaces`, `gridbots`, `tray-tilting`, `filters-plans-and-reduction-algorithms`. Discrete first (grids), then continuous.

## 🎯 Likely exam points
- Define I-space; give example sensors + preimages.
- History vs derived I-states; nondeterministic vs probabilistic; **sufficient I-map**.
- Run a predict/correct update by hand (both flavours).

## 📝 My notes / highlights
-
