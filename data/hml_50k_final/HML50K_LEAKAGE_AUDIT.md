# HML50K leakage and candidate audit

Result: `PASS` on all 56,000 canonical examples.

- Exact delta target present in input: 0.
- Gold tactic outside the intentional candidate block: 0. Seventy-four source rows with
  natural verbatim overlap were excluded before selection.
- Answer positions across six slots: 9,418 / 9,241 / 9,203 / 9,416 / 9,366 / 9,356.
- Mean tactic length: gold 49.291 characters, distractors 49.484.
- Gold uniquely shortest: 1.466%; deterministic shortest-first baseline: 15.786% versus
  16.667% chance. The 80.030% “tied for shortest” rate is reported separately and is not a
  shortcut because equal-length ties dominate.
- 90.922% of distractors share the gold tactic head.
- Tactic-family first-tie baseline: 24.086%.
- Lexical-overlap baseline: 51.836%; the same predictor against deterministic randomized
  labels scores 16.661%. This real surface signal is a known task limitation, not suppressed.
- Planted exact-target, answer-marker, and canonical-hash corruptions were all detected.

Distractors have status `PLAUSIBLE_UNEXECUTED`. The corpus never claims that an action is
mathematically invalid merely because it was not the recorded source tactic.
