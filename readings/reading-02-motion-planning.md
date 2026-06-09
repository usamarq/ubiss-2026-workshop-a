# Reading 2 — Motion Planning

> Kavraki LE & LaValle SM (2016). *Motion Planning.* In: Siciliano & Khatib (eds.), **Springer Handbook of Robotics**, 2nd ed., pp. 139–161.
> Status: 🟡 basics pre-filled

## TL;DR
Finding a **collision-free motion** from a start to a goal — the classic "the state is known" planning problem.

## Key topics
- **Configuration space (C-space)** — each robot pose = a point; planning happens here. `C_free` (collision-free) vs `C_obs` (obstacles).
- **Combinatorial (exact) planning** — complete, but expensive; cell decomposition, roadmaps, visibility graphs.
- **Sampling-based planning** — scales to high dimensions:
  - **PRM** (Probabilistic Roadmap) — sample configs, connect neighbours → graph; great for multi-query.
  - **RRT** (Rapidly-exploring Random Tree) — grow a tree toward random samples; great for single-query / kinodynamic.
- **Completeness:** *complete* → *resolution-complete* → *probabilistically complete* (sampling methods).
- Collision checking, distance metrics, narrow passages.

## Relevance to the workshop
- This is planning **with perfect state info**. Contrast with planning in **information spaces** (planning under uncertainty) — the **filtering vs planning** theme.

## 🎯 Likely exam points
- Define C-space, `C_free`/`C_obs`.
- PRM vs RRT (multi- vs single-query); the three kinds of completeness.

## 📝 My notes / highlights
-
