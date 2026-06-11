# Forward-Looking Survey: Current & Future Directions ("Doing More With Less")

> **Workshop A — Minimalism in Robotics** · UBISS 2026
> Day 3 · Wed Jun 10 · Afternoon survey talk · Fort TS128
> Status: 🟢 from the Lecture 7 slides (Nilles, Sakçak, Shell) · lighter/contextual — unlikely heavy exam weight, but good "big picture" framing.

## TL;DR
A tour of where minimalist robotics is heading: exploit **environment structure** instead of fighting it, build **nearly-passive / persistent / transient** robots, and apply all of it to **sustainability, agriculture, infrastructure, and the environment**. The throughline: *doing more with less*.

## Framing claims (Nilles)
- **Minimalist & Robust Robotics for the Planet** — challenging-but-*structured* environments (aquatic, forestry, infrastructure), performance **at scale & over long durations**, **DIY** solutions.
- **Design has trade-offs & orderings** (the minimalism thesis, stated as equivalences):
  - `(robot + fancy sensor) ≈ (robot + cheap sensor + clever calibration)`
  - `(multiple robots moving slowly) ≈ (one robot moving quickly)`
  - → optimize for **energy/resource efficiency**, **understand system limits**, **show robustness/safety**.
- 🔥 **"Hot take":** *most "unstructured" environments are actually kind of structured* — so **use** environment geometry & dynamics to **reduce resource requirements** rather than overpowering them. (Direct echo of `day2-embodiment-x-minimalism`.)

## Emerging classes of robot
- **Nearly-passive robots** — let physics/environment do the work (cf. passive dynamic walkers).
- **Persistent robotics** ("long-duration autonomy") — e.g. **SlothBot** (wire-traversing, Notomista/Emam/Egerstedt 2019), RaccoonBot, TreeSpider, underwater gliders, aquatic energy harvesting.
- **Transient robotics** — robots designed to **degrade/decompose** (edible pneumatic batteries; backyard-degradable interfaces; "Unmaking" workshops). The "rise of transient robotics."
- **Robot–animal interactions** — sufficiency & uncanniness set by the animal's **umwelt** (its perceptual world); ref *Ways of Being* (James Bridle).

## Application domains
- **Agriculture** — virtual fencing, GPS vs low-power radio, precision/regenerative ag, agrivoltaics; "stochastic modeling & control of wild bodies."
- **Environmental monitoring beyond fly-by** — sampling, sensor-seeding, construction; challenges: scaling, efficiency, repairability, robustness.
- **Infrastructure & accessibility** — embodied measurement of wheeled-agent accessibility; persistent monitoring of bridges etc.; challenges: scaling, privacy.

## A distinction worth remembering
> **Sustainable robotics ≠ robotics for sustainability** — making robots themselves sustainable is *not* the same as using robots to advance sustainability. (Usually distinct goals.)

## The group's process (how they actually work)
Solid algorithm/representation/math foundations → embodied design activities → movement & environment observation → **place-based design** → rapid prototyping → user/domain-expert interviews → open-sourcing (CAD tools, ROS2).

## Why it matters for *minimalism*
The capstone "so what": minimalism isn't just elegant theory — it's the route to robots that are **cheap, robust, long-lived, and planet-friendly**. Useful framing for the team-project report and the result-seminar narrative.

## Connections
- Practical payoff of `day2-embodiment-x-minimalism` (use the environment), `day2-sensor-lattices` (sensor trade-offs), `day3-filters-plans-and-reduction-algorithms` (resource minimization).

## Resources mentioned
ACM ASSETS · ClimateBase · **Climate Robotics Network** (climaterobotics.network) · wildbotics.eu / wilddrone.eu (HORIZON Europe) · drawdown.org explorer. *Advice: seek domain-specific venues; think critically about tech hype.*

## 📎 Slides
Reconciled against **`reading_material/lecture_slides/Lecture 7_ Future Directions.pdf`**.
