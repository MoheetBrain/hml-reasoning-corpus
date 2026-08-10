# Gold-125 selection audit

The frozen Gold-25 was not reselected or rewritten. This report describes exactly the 100 new rows selected from the local Hendrycks MATH parquet.

## Selection controls

- Exactly 100 new records.
- No source row overlaps the frozen Gold-25 manifest.
- Known near-duplicate i-power and coin-majority rows were excluded.
- Asymptote, image-dependent, TikZ, empty, malformed, and extreme-length records were excluded.
- Category and level quotas are deterministic and interleaved across IDs 026–125 so each saturation tranche contains broad domain coverage.

## Category counts

| Category | Target | Selected |
|---|---:|---:|
| Algebra | 15 | 15 |
| Intermediate Algebra | 15 | 15 |
| Counting & Probability | 15 | 15 |
| Number Theory | 15 | 15 |
| Precalculus | 15 | 15 |
| Geometry | 12 | 12 |
| Prealgebra | 13 | 13 |

## Level counts

| Level | Selected |
|---|---:|
| Level 1 | 20 |
| Level 2 | 20 |
| Level 3 | 21 |
| Level 4 | 20 |
| Level 5 | 19 |

## Targeted semantic features

| Feature | Records |
|---|---:|
| case_analysis | 57 |
| construction | 44 |
| polynomial | 40 |
| counting | 37 |
| meta_observation | 31 |
| inequality | 29 |
| geometry | 29 |
| sequence | 29 |
| complex | 24 |
| rational | 24 |
| radical | 21 |
| function | 17 |
| probability | 16 |
| modular | 16 |
| trigonometry | 14 |
| calculus | 11 |
| symmetry | 11 |
| contradiction | 9 |
| logarithm | 6 |
| induction | 4 |
| inclusion_exclusion | 2 |

## New-record manifest

| ID | Row | Category | Level | Targeted features | Selection reason |
|---|---:|---|---|---|---|
| MATH-GOLD-026 | train-row-07557 | Algebra | Level 5 | case_analysis, complex, construction, counting, inequality, meta_observation, polynomial, probability, rational | Selected for semantic diversity in Algebra at Level 5; targeted case_analysis, complex, construction, counting, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-027 | train-row-04255 | Intermediate Algebra | Level 5 | case_analysis, complex, construction, counting, function, geometry, inequality, meta_observation, modular, radical, sequence | Selected for semantic diversity in Intermediate Algebra at Level 5; targeted case_analysis, complex, construction, counting, function and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-028 | train-row-02124 | Counting & Probability | Level 5 | case_analysis, complex, construction, counting, geometry, inclusion_exclusion, inequality, meta_observation, modular | Selected for semantic diversity in Counting & Probability at Level 5; targeted case_analysis, complex, construction, counting, geometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-029 | train-row-05254 | Number Theory | Level 5 | calculus, case_analysis, complex, construction, counting, geometry, inequality, polynomial, rational | Selected for semantic diversity in Number Theory at Level 5; targeted calculus, case_analysis, complex, construction, counting and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-030 | train-row-06774 | Precalculus | Level 4 | case_analysis, complex, construction, counting, meta_observation, polynomial, probability, rational, trigonometry | Selected for semantic diversity in Precalculus at Level 4; targeted case_analysis, complex, construction, counting, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-031 | train-row-03087 | Geometry | Level 5 | case_analysis, complex, construction, geometry, inequality, meta_observation, probability, radical, symmetry | Selected for semantic diversity in Geometry at Level 5; targeted case_analysis, complex, construction, geometry, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-032 | train-row-05674 | Prealgebra | Level 5 | case_analysis, complex, construction, counting, meta_observation, polynomial | Selected for semantic diversity in Prealgebra at Level 5; targeted case_analysis, complex, construction, counting, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-033 | train-row-00291 | Algebra | Level 5 | construction, counting, geometry, inequality, meta_observation, polynomial, radical, sequence | Selected for semantic diversity in Algebra at Level 5; targeted construction, counting, geometry, inequality, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-034 | train-row-04566 | Intermediate Algebra | Level 4 | case_analysis, complex, construction, geometry, meta_observation, polynomial, rational, symmetry | Selected for semantic diversity in Intermediate Algebra at Level 4; targeted case_analysis, complex, construction, geometry, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-035 | train-row-02077 | Counting & Probability | Level 5 | calculus, case_analysis, construction, counting, meta_observation, probability, rational, sequence | Selected for semantic diversity in Counting & Probability at Level 5; targeted calculus, case_analysis, construction, counting, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-036 | train-row-05265 | Number Theory | Level 5 | case_analysis, construction, counting, inclusion_exclusion, meta_observation, probability, rational, symmetry | Selected for semantic diversity in Number Theory at Level 5; targeted case_analysis, construction, counting, inclusion_exclusion, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-037 | train-row-07376 | Precalculus | Level 5 | calculus, geometry, inequality, meta_observation, radical, rational, trigonometry | Selected for semantic diversity in Precalculus at Level 5; targeted calculus, geometry, inequality, meta_observation, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-038 | train-row-03071 | Geometry | Level 5 | contradiction, geometry, polynomial, radical, sequence, trigonometry | Selected for semantic diversity in Geometry at Level 5; targeted contradiction, geometry, polynomial, radical, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-039 | train-row-11178 | Prealgebra | Level 5 | case_analysis, complex, construction, geometry, probability, rational | Selected for semantic diversity in Prealgebra at Level 5; targeted case_analysis, complex, construction, geometry, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-040 | train-row-00585 | Algebra | Level 5 | calculus, case_analysis, function, rational, symmetry | Selected for semantic diversity in Algebra at Level 5; targeted calculus, case_analysis, function, rational, symmetry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-041 | train-row-10327 | Intermediate Algebra | Level 3 | function, inequality, polynomial, radical, sequence, trigonometry | Selected for semantic diversity in Intermediate Algebra at Level 3; targeted function, inequality, polynomial, radical, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-042 | train-row-02088 | Counting & Probability | Level 5 | case_analysis, counting, inequality, polynomial, probability, radical, sequence | Selected for semantic diversity in Counting & Probability at Level 5; targeted case_analysis, counting, inequality, polynomial, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-043 | train-row-10805 | Number Theory | Level 5 | case_analysis, construction, contradiction, counting, inequality, meta_observation, modular, sequence | Selected for semantic diversity in Number Theory at Level 5; targeted case_analysis, construction, contradiction, counting, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-044 | train-row-07067 | Precalculus | Level 5 | case_analysis, contradiction, counting, function, modular, polynomial, trigonometry | Selected for semantic diversity in Precalculus at Level 5; targeted case_analysis, contradiction, counting, function, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-045 | train-row-09608 | Geometry | Level 3 | case_analysis, counting, geometry, inequality, probability, rational | Selected for semantic diversity in Geometry at Level 3; targeted case_analysis, counting, geometry, inequality, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-046 | train-row-06046 | Prealgebra | Level 4 | inequality, meta_observation, polynomial, sequence | Selected for semantic diversity in Prealgebra at Level 4; targeted inequality, meta_observation, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-047 | train-row-01508 | Algebra | Level 4 | complex, modular, sequence | Selected for semantic diversity in Algebra at Level 4; targeted complex, modular, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-048 | train-row-04498 | Intermediate Algebra | Level 5 | case_analysis, complex, construction, counting, probability, radical, sequence, symmetry | Selected for semantic diversity in Intermediate Algebra at Level 5; targeted case_analysis, complex, construction, counting, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-049 | train-row-08913 | Counting & Probability | Level 4 | complex, construction, function, geometry, inequality | Selected for semantic diversity in Counting & Probability at Level 4; targeted complex, construction, function, geometry, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-050 | train-row-10953 | Number Theory | Level 3 | case_analysis, construction, function, inequality, polynomial, rational | Selected for semantic diversity in Number Theory at Level 3; targeted case_analysis, construction, function, inequality, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-051 | train-row-07198 | Precalculus | Level 5 | case_analysis, construction, counting, geometry, induction, polynomial, rational, sequence | Selected for semantic diversity in Precalculus at Level 5; targeted case_analysis, construction, counting, geometry, induction and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-052 | train-row-03236 | Geometry | Level 4 | calculus, case_analysis, construction, geometry, inequality | Selected for semantic diversity in Geometry at Level 4; targeted calculus, case_analysis, construction, geometry, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-053 | train-row-06307 | Prealgebra | Level 1 | case_analysis, counting, inequality, modular | Selected for semantic diversity in Prealgebra at Level 1; targeted case_analysis, counting, inequality, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-054 | train-row-08667 | Algebra | Level 4 | case_analysis, function, logarithm, meta_observation, polynomial | Selected for semantic diversity in Algebra at Level 4; targeted case_analysis, function, logarithm, meta_observation, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-055 | train-row-03944 | Intermediate Algebra | Level 5 | calculus, case_analysis, complex, construction, polynomial, rational | Selected for semantic diversity in Intermediate Algebra at Level 5; targeted calculus, case_analysis, complex, construction, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-056 | train-row-02416 | Counting & Probability | Level 4 | case_analysis, construction, counting, probability, rational, trigonometry | Selected for semantic diversity in Counting & Probability at Level 4; targeted case_analysis, construction, counting, probability, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-057 | train-row-04696 | Number Theory | Level 3 | case_analysis, inequality, meta_observation, radical | Selected for semantic diversity in Number Theory at Level 3; targeted case_analysis, inequality, meta_observation, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-058 | train-row-07437 | Precalculus | Level 3 | case_analysis, construction, contradiction, geometry, meta_observation, polynomial, symmetry, trigonometry | Selected for semantic diversity in Precalculus at Level 3; targeted case_analysis, construction, contradiction, geometry, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-059 | train-row-02807 | Geometry | Level 4 | complex, function, geometry | Selected for semantic diversity in Geometry at Level 4; targeted complex, function, geometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-060 | train-row-05563 | Prealgebra | Level 4 | geometry, radical, rational | Selected for semantic diversity in Prealgebra at Level 4; targeted geometry, radical, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-061 | train-row-00183 | Algebra | Level 4 | case_analysis, construction, induction, sequence | Selected for semantic diversity in Algebra at Level 4; targeted case_analysis, construction, induction, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-062 | train-row-03670 | Intermediate Algebra | Level 4 | construction, logarithm, modular, radical, sequence | Selected for semantic diversity in Intermediate Algebra at Level 4; targeted construction, logarithm, modular, radical, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-063 | train-row-02461 | Counting & Probability | Level 3 | complex, inequality, meta_observation, sequence, symmetry | Selected for semantic diversity in Counting & Probability at Level 3; targeted complex, inequality, meta_observation, sequence, symmetry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-064 | train-row-05140 | Number Theory | Level 2 | induction | Selected for semantic diversity in Number Theory at Level 2; targeted induction and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-065 | train-row-12366 | Precalculus | Level 2 | function, logarithm, radical, trigonometry | Selected for semantic diversity in Precalculus at Level 2; targeted function, logarithm, radical, trigonometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-066 | train-row-03299 | Geometry | Level 4 | case_analysis, geometry, meta_observation, rational, symmetry | Selected for semantic diversity in Geometry at Level 4; targeted case_analysis, geometry, meta_observation, rational, symmetry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-067 | train-row-11421 | Prealgebra | Level 3 | calculus | Selected for semantic diversity in Prealgebra at Level 3; targeted calculus and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-068 | train-row-01368 | Algebra | Level 3 | case_analysis, contradiction, inequality | Selected for semantic diversity in Algebra at Level 3; targeted case_analysis, contradiction, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-069 | train-row-10018 | Intermediate Algebra | Level 4 | case_analysis, contradiction, counting, function, polynomial, radical | Selected for semantic diversity in Intermediate Algebra at Level 4; targeted case_analysis, contradiction, counting, function, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-070 | train-row-08696 | Counting & Probability | Level 4 | case_analysis, complex, contradiction, counting, inequality | Selected for semantic diversity in Counting & Probability at Level 4; targeted case_analysis, complex, contradiction, counting, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-071 | train-row-05189 | Number Theory | Level 4 | complex, modular, sequence | Selected for semantic diversity in Number Theory at Level 4; targeted complex, modular, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-072 | train-row-12377 | Precalculus | Level 3 | geometry, meta_observation, modular, radical, sequence, trigonometry | Selected for semantic diversity in Precalculus at Level 3; targeted geometry, meta_observation, modular, radical, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-073 | train-row-02866 | Geometry | Level 3 | counting, geometry, polynomial, radical, sequence | Selected for semantic diversity in Geometry at Level 3; targeted counting, geometry, polynomial, radical, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-074 | train-row-11511 | Prealgebra | Level 3 | case_analysis, polynomial, sequence | Selected for semantic diversity in Prealgebra at Level 3; targeted case_analysis, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-075 | train-row-01429 | Algebra | Level 3 | geometry, polynomial, radical, symmetry | Selected for semantic diversity in Algebra at Level 3; targeted geometry, polynomial, radical, symmetry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-076 | train-row-09881 | Intermediate Algebra | Level 3 | construction, induction, inequality, polynomial, sequence | Selected for semantic diversity in Intermediate Algebra at Level 3; targeted construction, induction, inequality, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-077 | train-row-08769 | Counting & Probability | Level 3 | case_analysis, construction, meta_observation, probability, rational, sequence, symmetry | Selected for semantic diversity in Counting & Probability at Level 3; targeted case_analysis, construction, meta_observation, probability, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-078 | train-row-04895 | Number Theory | Level 4 | case_analysis, counting, radical | Selected for semantic diversity in Number Theory at Level 4; targeted case_analysis, counting, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-079 | train-row-06858 | Precalculus | Level 4 | complex, construction, polynomial, probability, radical, trigonometry | Selected for semantic diversity in Precalculus at Level 4; targeted complex, construction, polynomial, probability, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-080 | train-row-09625 | Geometry | Level 3 | calculus, case_analysis, construction, geometry, inequality | Selected for semantic diversity in Geometry at Level 3; targeted calculus, case_analysis, construction, geometry, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-081 | train-row-05804 | Prealgebra | Level 3 | calculus, inequality | Selected for semantic diversity in Prealgebra at Level 3; targeted calculus, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-082 | train-row-00411 | Algebra | Level 3 | case_analysis, logarithm, meta_observation, radical | Selected for semantic diversity in Algebra at Level 3; targeted case_analysis, logarithm, meta_observation, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-083 | train-row-09676 | Intermediate Algebra | Level 3 | case_analysis, complex, contradiction, function, polynomial, sequence | Selected for semantic diversity in Intermediate Algebra at Level 3; targeted case_analysis, complex, contradiction, function, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-084 | train-row-08950 | Counting & Probability | Level 2 | case_analysis, counting, function, geometry, inequality | Selected for semantic diversity in Counting & Probability at Level 2; targeted case_analysis, counting, function, geometry, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-085 | train-row-10614 | Number Theory | Level 4 | case_analysis, counting, probability | Selected for semantic diversity in Number Theory at Level 4; targeted case_analysis, counting, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-086 | train-row-12235 | Precalculus | Level 3 | case_analysis, construction, counting, function, inequality, polynomial | Selected for semantic diversity in Precalculus at Level 3; targeted case_analysis, construction, counting, function, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-087 | train-row-09441 | Geometry | Level 1 | trigonometry | Selected for semantic diversity in Geometry at Level 1; targeted trigonometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-088 | train-row-06510 | Prealgebra | Level 1 | case_analysis, construction, probability | Selected for semantic diversity in Prealgebra at Level 1; targeted case_analysis, construction, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-089 | train-row-00064 | Algebra | Level 2 | contradiction, sequence | Selected for semantic diversity in Algebra at Level 2; targeted contradiction, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-090 | train-row-09968 | Intermediate Algebra | Level 2 | case_analysis, logarithm | Selected for semantic diversity in Intermediate Algebra at Level 2; targeted case_analysis, logarithm and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-091 | train-row-02329 | Counting & Probability | Level 3 | complex, counting, trigonometry | Selected for semantic diversity in Counting & Probability at Level 3; targeted complex, counting, trigonometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-092 | train-row-10971 | Number Theory | Level 3 | calculus, case_analysis, construction, inequality, polynomial | Selected for semantic diversity in Number Theory at Level 3; targeted calculus, case_analysis, construction, inequality, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-093 | train-row-07324 | Precalculus | Level 4 | construction, function, logarithm, meta_observation, polynomial | Selected for semantic diversity in Precalculus at Level 4; targeted construction, function, logarithm, meta_observation, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-094 | train-row-09511 | Geometry | Level 2 | counting, geometry, polynomial, rational | Selected for semantic diversity in Geometry at Level 2; targeted counting, geometry, polynomial, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-095 | train-row-06407 | Prealgebra | Level 2 | case_analysis, inequality, modular | Selected for semantic diversity in Prealgebra at Level 2; targeted case_analysis, inequality, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-096 | train-row-07881 | Algebra | Level 2 | case_analysis, construction, meta_observation, polynomial, symmetry | Selected for semantic diversity in Algebra at Level 2; targeted case_analysis, construction, meta_observation, polynomial, symmetry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-097 | train-row-04537 | Intermediate Algebra | Level 2 | case_analysis, construction, function, polynomial, rational, sequence | Selected for semantic diversity in Intermediate Algebra at Level 2; targeted case_analysis, construction, function, polynomial, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-098 | train-row-02200 | Counting & Probability | Level 2 | case_analysis, complex, counting, meta_observation, polynomial | Selected for semantic diversity in Counting & Probability at Level 2; targeted case_analysis, complex, counting, meta_observation, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-099 | train-row-11017 | Number Theory | Level 2 | case_analysis, construction, counting, inequality, meta_observation, modular | Selected for semantic diversity in Number Theory at Level 2; targeted case_analysis, construction, counting, inequality, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-100 | train-row-07496 | Precalculus | Level 2 | construction, geometry, sequence, trigonometry | Selected for semantic diversity in Precalculus at Level 2; targeted construction, geometry, sequence, trigonometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-101 | train-row-09497 | Geometry | Level 2 | case_analysis, construction, geometry, polynomial, sequence | Selected for semantic diversity in Geometry at Level 2; targeted case_analysis, construction, geometry, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-102 | train-row-11948 | Prealgebra | Level 2 | radical | Selected for semantic diversity in Prealgebra at Level 2; targeted radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-103 | train-row-08028 | Algebra | Level 2 | case_analysis, counting, meta_observation, polynomial | Selected for semantic diversity in Algebra at Level 2; targeted case_analysis, counting, meta_observation, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-104 | train-row-10335 | Intermediate Algebra | Level 2 | case_analysis, construction, function, polynomial, sequence | Selected for semantic diversity in Intermediate Algebra at Level 2; targeted case_analysis, construction, function, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-105 | train-row-09108 | Counting & Probability | Level 2 | modular, sequence | Selected for semantic diversity in Counting & Probability at Level 2; targeted modular, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-106 | train-row-10543 | Number Theory | Level 2 | case_analysis, probability, rational | Selected for semantic diversity in Number Theory at Level 2; targeted case_analysis, probability, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-107 | train-row-07497 | Precalculus | Level 2 | construction, geometry | Selected for semantic diversity in Precalculus at Level 2; targeted construction, geometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-108 | train-row-03371 | Geometry | Level 1 | counting, geometry, rational | Selected for semantic diversity in Geometry at Level 1; targeted counting, geometry, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-109 | train-row-11290 | Prealgebra | Level 2 | construction, counting, meta_observation | Selected for semantic diversity in Prealgebra at Level 2; targeted construction, counting, meta_observation and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-110 | train-row-00255 | Algebra | Level 1 | case_analysis, counting, polynomial | Selected for semantic diversity in Algebra at Level 1; targeted case_analysis, counting, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-111 | train-row-09672 | Intermediate Algebra | Level 1 | complex, geometry, polynomial, radical | Selected for semantic diversity in Intermediate Algebra at Level 1; targeted complex, geometry, polynomial, radical and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-112 | train-row-02495 | Counting & Probability | Level 1 | case_analysis, construction, counting, inequality | Selected for semantic diversity in Counting & Probability at Level 1; targeted case_analysis, construction, counting, inequality and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-113 | train-row-04870 | Number Theory | Level 1 | construction, counting, modular | Selected for semantic diversity in Number Theory at Level 1; targeted construction, counting, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-114 | train-row-12303 | Precalculus | Level 1 | construction, function | Selected for semantic diversity in Precalculus at Level 1; targeted construction, function and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-115 | train-row-11895 | Prealgebra | Level 1 | calculus | Selected for semantic diversity in Prealgebra at Level 1; targeted calculus and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-116 | train-row-00583 | Algebra | Level 1 | complex, meta_observation, polynomial, sequence | Selected for semantic diversity in Algebra at Level 1; targeted complex, meta_observation, polynomial, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-117 | train-row-03616 | Intermediate Algebra | Level 1 | meta_observation, polynomial, rational, sequence | Selected for semantic diversity in Intermediate Algebra at Level 1; targeted meta_observation, polynomial, rational, sequence and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-118 | train-row-08910 | Counting & Probability | Level 1 | case_analysis, construction, counting, meta_observation, probability, rational | Selected for semantic diversity in Counting & Probability at Level 1; targeted case_analysis, construction, counting, meta_observation, probability and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-119 | train-row-10745 | Number Theory | Level 1 | case_analysis, counting, modular | Selected for semantic diversity in Number Theory at Level 1; targeted case_analysis, counting, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-120 | train-row-07109 | Precalculus | Level 1 | geometry | Selected for semantic diversity in Precalculus at Level 1; targeted geometry and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-121 | train-row-08118 | Algebra | Level 1 | complex, construction, counting, polynomial | Selected for semantic diversity in Algebra at Level 1; targeted complex, construction, counting, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-122 | train-row-04038 | Intermediate Algebra | Level 1 | modular, polynomial | Selected for semantic diversity in Intermediate Algebra at Level 1; targeted modular, polynomial and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-123 | train-row-08708 | Counting & Probability | Level 1 | polynomial, rational | Selected for semantic diversity in Counting & Probability at Level 1; targeted polynomial, rational and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-124 | train-row-04775 | Number Theory | Level 1 | case_analysis, meta_observation, modular | Selected for semantic diversity in Number Theory at Level 1; targeted case_analysis, meta_observation, modular and active-coverage pressure beyond the frozen Gold-25. |
| MATH-GOLD-125 | train-row-06915 | Precalculus | Level 1 | trigonometry | Selected for semantic diversity in Precalculus at Level 1; targeted trigonometry and active-coverage pressure beyond the frozen Gold-25. |
