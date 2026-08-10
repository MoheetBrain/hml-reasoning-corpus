# AMPS-Khan cross-source replication preparation

This is a bounded candidate-selection plan, not an annotation run. No 100k-row processing and no training were performed.

- Ontology gate passed: False
- Prospective topic-diverse candidates: 100
- Candidate status: PROSPECTIVE_ONLY_NOT_ANNOTATED
- Approval condition: resolve ontology-v1 unresolved and annotation-review cases before creating trajectories.

## Cross-source test

Given ontology-v1 learned/discovered from MATH, count separately: new core operation, new meta operation, new library operation, new backend operation, new warrant, and new state field. New mathematics is not automatically a new reasoning primitive.

## Filters

- Original parquet is the source of truth.
- One candidate per topic family where possible.
- Exclude null/empty, visual-dependent, and multiple-choice rows.
- Prefer source planning cues and clean machine-readable mathematics.
- Preserve row index, topic, source text, and stable hash.

## Candidate preview

| Candidate | Row | Topic | Planning cue | Solution chars | Status |
|---|---:|---|---|---:|---|
| AMPS-CANDIDATE-001 | 34759 | matrix_inverse_2x2 | yes | 2539 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-002 | 83444 | calculating-binomial-probability | yes | 2549 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-003 | 92265 | 177 | yes | 2295 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-004 | 79479 | stokes--theorem | yes | 2281 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-005 | 58671 | standard_deviation_of_a_population | yes | 2266 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-006 | 73319 | multiply-decimals--up-to-4-digit-factors- | yes | 2102 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-007 | 40470 | tangents-to-polar-curves | yes | 2093 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-008 | 47741 | powers_of_complex_numbers_1 | yes | 2057 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-009 | 74385 | equation-of-ellipse-from-foci | yes | 2028 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-010 | 79006 | volumes-with-triangles-and-semicircles-cross-sections | yes | 2012 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-011 | 12516 | variance | yes | 1972 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-012 | 30106 | modeling-with-periodic-functions-2 | yes | 1960 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-013 | 94440 | vector-word-problems | yes | 1924 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-014 | 57377 | 131 | yes | 1881 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-015 | 30041 | understanding-systems-of-equations-word-problems | yes | 1880 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-016 | 3259 | modeling-with-periodic-functions | yes | 1861 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-017 | 65589 | modeling-with-one-variable-equations-and-inequalities | yes | 1848 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-018 | 14244 | adding_and_subtracting_rational_expressions_5 | yes | 1818 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-019 | 15662 | surface-and-volume-density-word-problems | yes | 1775 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-020 | 89197 | computing-curl-in-3d | yes | 1752 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-021 | 87868 | interpreting-quadratic-models | yes | 1734 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-022 | 86191 | 457 | yes | 1727 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-023 | 35408 | multiplying_and_dividing_rational_expressions_3 | yes | 1717 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-024 | 26006 | construct-exponential-models-according-to-rate-of-change | yes | 1614 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-025 | 26191 | 439 | yes | 1591 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-026 | 87006 | solve-matrix-equations-add-sub | yes | 1567 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-027 | 72562 | dividing-polynomials-with-remainders | yes | 1529 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-028 | 64335 | 199 | yes | 1508 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-029 | 31397 | solve-matrix-equations-scalar-multiplication | yes | 1500 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-030 | 53233 | 198 | yes | 1483 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-031 | 73054 | 276 | yes | 1477 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-032 | 97384 | subtracting_fractions | yes | 1475 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-033 | 99358 | the-divergence-theorem | yes | 1470 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-034 | 88303 | computing-line-integrals-in-vector-fields | yes | 1463 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-035 | 23811 | adding_and_subtracting_rational_expressions_3 | yes | 1454 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-036 | 4476 | 192 | yes | 1450 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-037 | 87358 | sequences-as-functions | yes | 1443 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-038 | 60545 | limits_2 | yes | 1442 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-039 | 88755 | direction-angles | yes | 1425 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-040 | 15389 | adding_and_subtracting_rational_expressions_2 | yes | 1419 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-041 | 85332 | add---subtract-polynomials-challenge | yes | 1407 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-042 | 65247 | 536 | yes | 1389 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-043 | 28543 | constructing-and-interpreting-linear-functions | yes | 1358 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-044 | 58342 | limits-at-infinity-of-rational-functions-radicals | yes | 1341 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-045 | 98572 | differentiate-rational-functions | yes | 1341 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-046 | 59755 | applying-right-triangles | yes | 1340 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-047 | 100941 | construct-sinusoidal-functions | yes | 1337 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-048 | 8244 | change-of-variables--factor | yes | 1333 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-049 | 71708 | differentiate-quotients | yes | 1329 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-050 | 81920 | evaluate-logarithms-using-the-change-of-base-rule | yes | 1323 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-051 | 33210 | arithmetic_series | yes | 1317 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-052 | 6762 | compute-directional-derivatives | yes | 1316 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-053 | 77232 | u-substitution--definite-integrals | yes | 1308 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-054 | 56712 | geometric-series | yes | 1290 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-055 | 12959 | 218 | yes | 1262 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-056 | 73246 | find-the-missing-number--addition-and-subtraction-within-1000- | yes | 1258 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-057 | 78974 | dependent_probability | yes | 1249 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-058 | 56132 | compute-triple-integrals | yes | 1234 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-059 | 64055 | 393 | yes | 1231 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-060 | 35446 | solve-exponential-equations-using-properties-of-exponents-advanced | yes | 1221 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-061 | 59762 | differentiate-radical-functions-intro | yes | 1221 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-062 | 55188 | adding-and-subtracting-fractions-with-unlike-denominators-word-problems | yes | 1215 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-063 | 103051 | unit-vector | yes | 1201 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-064 | 14868 | 274 | yes | 1181 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-065 | 35774 | comparing-growth-rates-of-exponentials-and-polynomials | yes | 1181 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-066 | 33386 | applications-of-derivatives--motion-along-a-line | yes | 1160 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-067 | 16251 | 242 | yes | 1159 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-068 | 86599 | 495 | yes | 1147 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-069 | 93993 | equation_of_a_circle_2 | yes | 1142 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-070 | 95643 | potential-functions | yes | 1125 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-071 | 35748 | second-derivatives-implicit-equations | yes | 1124 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-072 | 13087 | planar-motion-integral-calc | yes | 1123 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-073 | 2679 | solve-exponential-equations-using-properties-of-exponents--basic- | yes | 1118 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-074 | 27595 | 430 | yes | 1093 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-075 | 16720 | 477 | yes | 1087 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-076 | 10105 | factor-quadratics-common-factor | yes | 1085 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-077 | 3890 | age_word_problems | yes | 1080 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-078 | 11902 | find-the-angle-of-complex-numbers | yes | 1078 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-079 | 48611 | solving-quadratics-by-using-structure | yes | 1075 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-080 | 24412 | 401 | yes | 1069 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-081 | 27861 | computing-the-laplacian | yes | 1064 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-082 | 80884 | reverse-power-rule-rewriting | yes | 1063 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-083 | 42602 | integration-by-u-substitution | yes | 1056 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-084 | 84436 | writing-linear-functions-word-problems | yes | 1055 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-085 | 73522 | factor-using-polynomial-division | yes | 1053 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-086 | 32481 | gcf-and-lcm-word-problems | yes | 1052 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-087 | 21407 | circles-and-pythagorean-identities | yes | 1045 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-088 | 47487 | solving_for_the_x-intercept | yes | 1045 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-089 | 42721 | two-sided-limits-using-algebra | yes | 1039 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-090 | 50078 | using-logarithms-to-solve-exponential-equations | yes | 1038 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-091 | 7309 | 399 | yes | 1037 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-092 | 37204 | represent-systems-with-matrices | yes | 1034 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-093 | 10160 | differentiate-fractional-powers | yes | 1031 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-094 | 60580 | 163 | yes | 1017 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-095 | 61483 | separable-differential-equations | yes | 1012 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-096 | 13072 | multivar-modeling | yes | 1002 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-097 | 65629 | variables-on-both-sides-rational | yes | 1001 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-098 | 66649 | higher-order-partial-derivatives | yes | 983 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-099 | 77645 | 460 | yes | 978 | PROSPECTIVE_ONLY_NOT_ANNOTATED |
| AMPS-CANDIDATE-100 | 47255 | two-step-equations-with-decimals-and-fractions | yes | 974 | PROSPECTIVE_ONLY_NOT_ANNOTATED |

This is not a Gold-100 trajectory corpus and must not be annotated automatically.
