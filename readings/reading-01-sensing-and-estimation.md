# Reading 1 — Sensing and Estimation

> Christensen HI & Hager GD (2016). *Sensing and Estimation.* In: Siciliano & Khatib (eds.), **Springer Handbook of Robotics**, 2nd ed., pp. 91–112.
> Status: 🟡 basics pre-filled

## TL;DR
How robots **sense** the world and turn **noisy, partial measurements into state estimates** — the "classical approach" that information spaces offer an alternative to.

## Key topics
- **Sensor types:** *proprioceptive* (internal — encoders, IMU) vs *exteroceptive* (external — cameras, range/LiDAR, contact).
- **Sensor models & uncertainty:** measurements are incomplete and noisy; model as `y = h(x) + noise`.
- **State estimation** = recover `x` from measurement history.
- **Bayesian estimation:** maintain a belief `P(x)`, updated by **prediction** (motion model) and **correction** (measurement model) — i.e. the **predict/correct** loop.
- **Kalman filter** (linear-Gaussian) and **EKF** (nonlinear); least-squares; **data association**; **sensor fusion**.

## Relevance to the workshop
- The probabilistic **I-state** (`information-spaces`) *is* a Bayesian estimate; this chapter is the estimation half.
- Minimalism asks: **when can you skip estimation entirely** and act on a coarse I-state instead?

## 🎯 Likely exam points
- Proprioceptive vs exteroceptive sensors.
- Sketch Bayesian estimation / the Kalman predict–update cycle.

## 📝 My notes / highlights
-
