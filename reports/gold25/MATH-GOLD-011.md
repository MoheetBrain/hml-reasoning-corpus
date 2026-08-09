# MATH-GOLD-011

## Original problem

If three people are selected at random from a group of seven men and three women, what is the probability that at least one woman is selected? Express your answer as a common fraction.

## Original solution

We can find the probability that no women are selected and subtract it from 1 to find the probability that at least one woman is selected. To find the probability that only men are selected, we consider that the chance that the first person selected is male is $\frac{7}{10}$. Then the probability that the second person selected is male is reduced to $\frac{6}{9}=\frac{2}{3}$. For the third person, the probability is $\frac{5}{8}$. So the probability that only men are selected is $$\frac{7}{10}\cdot\frac{2}{3}\cdot\frac{5}{8}=\frac{7}{24}.$$ Notice that the 2 and 5 in the numerator cancel with the 10 in the denominator to leave $\frac{7}{24}$. Now we subtract from 1 to find the probability that at least one woman is selected. The probability is $1-\frac{7}{24}=\boxed{\frac{17}{24}}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)

## Trajectory

### Step 1: COMPLEMENT_COUNT

**Source span:** We can find the probability that no women are selected and subtract it from 1

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)

**Arguments:** `{}`

**Warrant:** For a binary event partition, P(at least one woman)=1-P(no woman). (`complement_rule`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:population, fact:sample

**Result:** `fact:s1` target = 1-P(no women)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Probability complement reasoning is not a core HML rule.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S1` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

### Step 2: CONDITIONAL_PROBABILITY

**Source span:** the chance that the first person selected is male is $\frac{7}{10}$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

**Arguments:** `{}`

**Warrant:** Count favorable men over the population size. (`uniform_sampling`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:population

**Result:** `fact:s2` P(first male)=7/10

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite-sampling probability lacks a trusted domain library.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S2` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

### Step 3: CONDITIONAL_PROBABILITY

**Source span:** Then the probability that the second person selected is male is reduced to $\frac{6}{9}=\frac{2}{3}$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

**Arguments:** `{}`

**Warrant:** Update the population after one male has been selected. (`without_replacement_update`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:population

**Result:** `fact:s3` P(second male | first male)=2/3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Conditional probability update is library-level.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S3` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

### Step 4: CONDITIONAL_PROBABILITY

**Source span:** For the third person, the probability is $\frac{5}{8}$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

**Arguments:** `{}`

**Warrant:** Update counts after two male selections. (`without_replacement_update`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:population

**Result:** `fact:s4` P(third male | first two male)=5/8

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Conditional probability update is library-level.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S4` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

### Step 5: MULTIPLY_CONDITIONALS

**Source span:** So the probability that only men are selected is $$\frac{7}{10}\cdot\frac{2}{3}\cdot\frac{5}{8}=\frac{7}{24}.$$

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

**Arguments:** `{}`

**Warrant:** Multiply the successive conditional probabilities. (`chain_rule`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:population, fact:sample

**Result:** `fact:s5` P(no women)=7/24

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Conditional-product semantics are not a core rule.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S5` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
- `fact:s5` P(no women)=7/24 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

### Step 6: COMPLEMENT_COUNT

**Source span:** Now we subtract from 1 to find the probability that at least one woman is selected. The probability is $1-\frac{7}{24}=\boxed{\frac{17}{24}}$.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
- `fact:s5` P(no women)=7/24 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample

**Arguments:** `{}`

**Warrant:** Subtract the exact complement from one. (`complement_rule`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:no_women

**Result:** `fact:s6` P(at least one woman)=17/24

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Numeric fraction arithmetic is checkable after the probability law is supplied.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S6` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
- `fact:s5` P(no women)=7/24 (established)
- `fact:s6` P(at least one woman)=17/24 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_open)
**Dependencies:**
- fact:population
- fact:sample
- fact:no_women

## Final state

`S6` scope: global
**Objects:**
- 7 men
- 3 women
- three selected people
**Declarations:**
- finite population
**Types/domains:**
- sampling without replacement
**Facts:**
- `fact:population` 7 men and 3 women (given)
- `fact:sample` sample size 3 (given)
- `fact:s1` target = 1-P(no women) (established)
- `fact:s2` P(first male)=7/10 (established)
- `fact:s3` P(second male | first male)=2/3 (established)
- `fact:s4` P(third male | first two male)=5/8 (established)
- `fact:s5` P(no women)=7/24 (established)
- `fact:s6` P(at least one woman)=17/24 (established)
**Goals:**
- `goal:answer` P(at least one woman)=17/24 (goal_discharged)
**Dependencies:**
- fact:population
- fact:sample
- fact:no_women

**Goal status:** `discharged`

## Operations observed

`COMPLEMENT_COUNT`, `CONDITIONAL_PROBABILITY`, `MULTIPLY_CONDITIONALS`

## HML gaps exposed

MATH-GAP-0008
