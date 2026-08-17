# Structural Trajectory Audit

The complete LeanDojo source has **61,544** non-empty ordered trajectories among
122,514 theorem entries; 60,973 theorem entries contain no traced transition.
After excluding old VNext development parents, **57,874** complete ordered
trajectories remain, containing 216,623 transitions.

| Property | Result |
|---|---|
| median trajectory length | 2 |
| maximum trajectory length | 128 overall; 127 fresh |
| complete ordered sequence available | yes, for 61,544 non-empty traces |
| exact before states | yes |
| exact source actions | yes |
| exact after states | yes |
| replay executable now | no |
| environment required | pinned Lean/Mathlib checkout and trace replay toolchain |
| current blocker | source archive carries historical traces; matching executable Mathlib environment was not installed on the data VM |

Fresh transition proof-depth bins:

| Depth | Count |
|---|---:|
| step 1 | 57,874 |
| 2–3 | 60,539 |
| 4–5 | 30,716 |
| 6–10 | 36,432 |
| 11–20 | 21,671 |
| 21+ | 9,391 |
| **total** | **216,623** |

Fresh complete trajectory-length bins:

| Length | Trajectories |
|---|---:|
| 1 | 21,176 |
| 2–3 | 19,368 |
| 4–5 | 6,779 |
| 6–10 | 6,607 |
| 11–20 | 3,024 |
| 21+ | 920 |
| **total** | **57,874** |

There are **36,698** fresh actual complete multi-step source trajectories (length
greater than one).

These are source trajectory positions. They are not observed model rollouts. The
number of true free-running executable trajectories prepared by this mission is
**0**, because no admitted dataset/replay environment exists.
