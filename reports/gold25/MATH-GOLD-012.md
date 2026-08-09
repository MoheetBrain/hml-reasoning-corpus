# MATH-GOLD-012

## Original problem

If three, standard, 6-faced dice are rolled, what is the probability that the sum of the face up integers is 16?

## Original solution

At least one of the dice must come up 6, since otherwise the best we can do is 15.  The other two dice must add up to 10.  There are two ways two dice add to 10: $4+6$ and $5+5$.

So, we have two cases to consider:

A) The dice are 6, 6, 4.  There are three possible ways this can happen, and the probability of each is $(1/6)^3 = 1/216$.  So, the probability of this case is $3(1/216) = 1/72$.


B) The dice are 6, 5, 5.  There are three possible ways this can happen, and the probability of each is $(1/6)^3 = 1/216$.  So, the probability of this case is $3(1/216) = 1/72$.

Adding the probabilities of these two cases gives us a total probability of $\frac{1}{72} + \frac{1}{72} = \boxed{\frac{1}{36}}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)

## Trajectory

### Step 1: BOUND_REASONING

**Source span:** At least one of the dice must come up 6, since otherwise the best we can do is 15.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)

**Arguments:** `{}`

**Warrant:** The sum of three values at most 5 is at most 15. (`upper_bound`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:target

**Result:** `fact:s1` at least one die is 6

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: assume, evidence. Bound reasoning over finite domains is not a core rule.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S1` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Dependencies:**
- fact:target

### Step 2: CONSTRAINT_PROPAGATION

**Source span:** The other two dice must add up to 10.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Dependencies:**
- fact:target

**Arguments:** `{}`

**Warrant:** Subtract the required 6 contribution from the target sum. (`arithmetic_constraint`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:target

**Result:** `fact:s2` remaining two dice sum to 10

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed arithmetic is checkable; finite-domain propagation is not.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S2` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Dependencies:**
- fact:target

### Step 3: ENUMERATE

**Source span:** There are two ways two dice add to 10: $4+6$ and $5+5$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Dependencies:**
- fact:target

**Arguments:** `{}`

**Warrant:** Enumerate all pairs in {1,…,6} summing to 10, up to order. (`finite_exhaustion`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 — `discharged`

**Dependencies:** fact:target

**Result:** `fact:s3` patterns (6,6,4) and (6,5,5)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: scope. No finite enumeration rule or completeness certificate exists.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0004, MATH-GAP-0008

**State after:**

`S3` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target

### Step 4: COUNT_PERMUTATIONS

**Source span:** A) The dice are 6, 6, 4.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target

**Arguments:** `{}`

**Warrant:** Choose which die shows 4; the two 6s are identical. (`permutation_count`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:target

**Result:** `fact:s4` case A has 3 ordered outcomes

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Permutation counting is library-level.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S4` scope: global, branch:case A
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target

### Step 5: EVALUATE_PROBABILITY

**Source span:** There are three possible ways this can happen, and the probability of each is $(1/6)^3 = 1/216$.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global, branch:case A
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target

**Arguments:** `{}`

**Warrant:** Each ordered triple has probability 1/216; multiply by the case multiplicity. (`uniform_product_space`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:sample_space

**Result:** `fact:s5` P(case A)=3/216=1/72

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite probability and multiplicity need a domain library.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S5` scope: global, branch:case A
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

### Step 6: COUNT_PERMUTATIONS

**Source span:** B) The dice are 6, 5, 5.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global, branch:case A
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

**Arguments:** `{}`

**Warrant:** Choose which die shows 6; the two 5s are identical. (`permutation_count`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:target

**Result:** `fact:s6` case B has 3 ordered outcomes

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Permutation counting is library-level.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S6` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

### Step 7: EVALUATE_PROBABILITY

**Source span:** So, the probability of this case is $3(1/216) = 1/72$.

**Explicitness:** `explicit`

**State before:**

`S6` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

**Arguments:** `{}`

**Warrant:** Use the same ordered-outcome probability for case B. (`uniform_product_space`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:sample_space

**Result:** `fact:s7` P(case B)=3/216=1/72

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite probability and multiplicity need a domain library.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S7` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
- `fact:s7` P(case B)=3/216=1/72 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

### Step 8: COMBINE_CASE_COUNTS

**Source span:** Adding the probabilities of these two cases gives us a total probability of $\frac{1}{72} + \frac{1}{72} = \boxed{\frac{1}{36}}$.

**Explicitness:** `explicit`

**State before:**

`S7` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
- `fact:s7` P(case B)=3/216=1/72 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space

**Arguments:** `{}`

**Warrant:** The cases are disjoint and exhaustive, so add their probabilities. (`disjoint_case_sum`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:case_A, fact:case_B

**Result:** `fact:s8` P(sum=16)=1/36

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. The final rational sum is checkable after case semantics are supplied.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0004, MATH-GAP-0008

**State after:**

`S8` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
- `fact:s7` P(case B)=3/216=1/72 (established)
- `fact:s8` P(sum=16)=1/36 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_open)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space
- fact:case_A
- fact:case_B

## Final state

`S8` scope: global, branch:case A, branch:case B
**Objects:**
- three six-sided dice
**Declarations:**
- D1,D2,D3 : {1,2,3,4,5,6}
**Types/domains:**
- independent fair dice
**Facts:**
- `fact:sample_space` 6³ equally likely ordered outcomes (given)
- `fact:target` D1+D2+D3=16 (given)
- `fact:s1` at least one die is 6 (established)
- `fact:s2` remaining two dice sum to 10 (established)
- `fact:s3` patterns (6,6,4) and (6,5,5) (established)
- `fact:s4` case A has 3 ordered outcomes (established)
- `fact:s5` P(case A)=3/216=1/72 (established)
- `fact:s6` case B has 3 ordered outcomes (established)
- `fact:s7` P(case B)=3/216=1/72 (established)
- `fact:s8` P(sum=16)=1/36 (established)
**Goals:**
- `goal:answer` probability=1/36 (goal_discharged)
**Discharged obligations:**
- `obl:dice_case_cover` the listed dice patterns exhaust the finite pairs summing to 10 (discharged)
**Dependencies:**
- fact:target
- fact:sample_space
- fact:case_A
- fact:case_B

**Goal status:** `discharged`

## Operations observed

`BOUND_REASONING`, `COMBINE_CASE_COUNTS`, `CONSTRAINT_PROPAGATION`, `COUNT_PERMUTATIONS`, `ENUMERATE`, `EVALUATE_PROBABILITY`

## HML gaps exposed

MATH-GAP-0001, MATH-GAP-0004, MATH-GAP-0008
