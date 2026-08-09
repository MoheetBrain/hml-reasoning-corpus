# MATH-GOLD-025

## Original problem

Bob is trying to decide between two cell phone plans. Plan A has no flat fee, but the user must pay $10$ cents per minute on the phone. Plan B requires a one-time fee of $\$20$, but only requires a payment of $5$ cents per minute on the phone. What is the minimum whole number of minutes Bob has to use the phone for to make Plan B the cheaper plan?

## Original solution

Let $x$ be the number of minutes that Bob anticipates using. Plan A costs $10x$ cents, while Plan B costs $2000 + 5x$ cents. We therefore have the inequality \begin{align*}
2000+5x &< 10x \\
\Rightarrow\qquad 2000 &< 5x \\
\Rightarrow\qquad 400 &< x.
\end{align*} The smallest integer $x$ such that $400 < x$ is $401$. Therefore, Bob must use at least $\boxed{401}$ minutes to make Plan B cheaper.

## Canonical initial state

`S0` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** Let $x$ be the number of minutes that Bob anticipates using.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

**Arguments:** `{}`

**Warrant:** Name the unknown usage count. (`variable_binding`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` x denotes minutes

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: var. Typed variable declaration is native.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

### Step 2: FORMULATE_EQUATION

**Source span:** Plan A costs $10x$ cents, while Plan B costs $2000 + 5x$ cents.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

**Arguments:** `{}`

**Warrant:** Translate price schedules into affine cost functions. (`word_problem_modeling`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s2` cost_A=10x; cost_B=2000+5x

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: def, assume. HML can record cost functions but has no prose modeling operation.

**Semantic gaps:** none

**State after:**

`S2` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

### Step 3: FORMULATE_INEQUALITY

**Source span:** We therefore have the inequality

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)

**Arguments:** `{}`

**Warrant:** Plan B is cheaper exactly when its cost is strictly below Plan A. (`comparison_goal`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:plan_A, fact:plan_B

**Result:** `fact:s3` 2000+5x<10x

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: goal, assume. Inequalities are representable; source-model construction is external.

**Semantic gaps:** none

**State after:**

`S3` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

### Step 4: SUBTRACT_BOTH_SIDES

**Source span:** We therefore have the inequality

**Explicitness:** `implicit`

**State before:**

`S3` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

**Arguments:** `{}`

**Warrant:** Subtract 5x and divide by positive 5, preserving inequality direction. (`order_preserving_affine_transform`, source `core`)

**Preconditions:**
- 5>0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:plan_A, fact:plan_B

**Result:** `fact:s4` x>400

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: add_inequality, multiply_inequality. Current kernel supports some inequality transformations; this compound normalization is partial.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S4` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

### Step 5: ROUND_TO_DOMAIN

**Source span:** The smallest integer $x$ such that $400 < x$ is $401$.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

**Arguments:** `{}`

**Warrant:** Select the least natural number strictly above 400. (`integer_ceiling`, source `derived`)

**Preconditions:**
- x∈Natural — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:plan_A, fact:plan_B

**Result:** `fact:s5` minimum whole-number x=401

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Integer threshold selection is not a current kernel rule.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S5` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
- `fact:s5` minimum whole-number x=401 (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

### Step 6: VERIFY_CANDIDATE

**Source span:** Therefore, Bob must use at least

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
- `fact:s5` minimum whole-number x=401 (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Dependencies:**
- fact:plan_A
- fact:plan_B

**Arguments:** `{}`

**Warrant:** Check the candidate in the original inequality and use the strict threshold for minimality. (`candidate_verification`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- `obl:threshold_minimality` x=401 is the least natural number satisfying x>400 — `discharged`

**Dependencies:** fact:plan_A, fact:plan_B

**Result:** `fact:s6` x=401 satisfies cost_B<cost_A and is minimal

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed cost comparison is checkable; integer minimality is not a core rule.

**Semantic gaps:** MATH-GAP-0002, MATH-GAP-0004, MATH-GAP-0010

**State after:**

`S6` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
- `fact:s5` minimum whole-number x=401 (established)
- `fact:s6` x=401 satisfies cost_B<cost_A and is minimal (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_open)
**Discharged obligations:**
- `obl:threshold_minimality` x=401 is the least natural number satisfying x>400 (discharged)
**Dependencies:**
- fact:plan_A
- fact:plan_B

## Final state

`S6` scope: global
**Objects:**
- phone plans
- x minutes
**Declarations:**
- x : Natural
**Types/domains:**
- x is a whole number of minutes
**Facts:**
- `fact:plan_A` cost_A=10x cents (given)
- `fact:plan_B` cost_B=2000+5x cents (given)
- `fact:s1` x denotes minutes (established)
- `fact:s2` cost_A=10x; cost_B=2000+5x (established)
- `fact:s3` 2000+5x<10x (established)
- `fact:s4` x>400 (established)
- `fact:s5` minimum whole-number x=401 (established)
- `fact:s6` x=401 satisfies cost_B<cost_A and is minimal (established)
**Goals:**
- `goal:answer` minimum x=401 (goal_discharged)
**Discharged obligations:**
- `obl:threshold_minimality` x=401 is the least natural number satisfying x>400 (discharged)
**Dependencies:**
- fact:plan_A
- fact:plan_B

**Goal status:** `discharged`

## Operations observed

`FORMULATE_EQUATION`, `FORMULATE_INEQUALITY`, `INTRODUCE_VARIABLE`, `ROUND_TO_DOMAIN`, `SUBTRACT_BOTH_SIDES`, `VERIFY_CANDIDATE`

## HML gaps exposed

MATH-GAP-0002, MATH-GAP-0004, MATH-GAP-0006, MATH-GAP-0010
