# MATH-GOLD-024

## Original problem

Compute $1+6\cdot2-3+5\cdot4\div2$

## Original solution

When solving this problem, we must remember to apply the order of operations. First, we perform all cases of multiplication and division from left to right to obtain

\begin{align*}
1+6\cdot2-3+5\cdot4\div2&=1+12-3+5\cdot4\div2\\
&=1+12-3+20\div 2\\
&=1+12-3+10.
\end{align*}Next, we perform all the required additions and subtractions from left to right. We get  \begin{align*}
1+12-3+10&=13-3+10\\
&=10+10\\
&=\boxed{20}.
\end{align*}

## Canonical initial state

`S0` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
**Goals:**
- `goal:answer` value=20 (goal_open)

## Trajectory

### Step 1: APPLY_PRECEDENCE

**Source span:** When solving this problem, we must remember to apply the order of operations.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
**Goals:**
- `goal:answer` value=20 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply the conventional precedence relation. (`operator_precedence`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` multiplication/division precede addition/subtraction

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: closed_eval_v1. HML can evaluate a closed expression but does not expose a source-level precedence transition.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S1` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
**Goals:**
- `goal:answer` value=20 (goal_open)

### Step 2: EVALUATE

**Source span:** First, we perform all cases of multiplication and division from left to right to obtain

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
**Goals:**
- `goal:answer` value=20 (goal_open)

**Arguments:** `{}`

**Warrant:** Evaluate the multiplication 6·2 while preserving the remaining expression. (`exact_arithmetic`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1, fact:expression

**Result:** `fact:s2` 1+12-3+20÷2

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Exact closed arithmetic is supported as evidence.

**Semantic gaps:** none

**State after:**

`S2` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression

### Step 3: EVALUATE

**Source span:** 20\div 2

**Explicitness:** `implicit`

**State before:**

`S2` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression

**Arguments:** `{}`

**Warrant:** Evaluate 20÷2 exactly. (`exact_arithmetic`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` 1+12-3+10

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Exact closed arithmetic is supported as evidence.

**Semantic gaps:** none

**State after:**

`S3` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2

### Step 4: EVALUATE

**Source span:** Next, we perform all the required additions and subtractions from left to right.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2

**Arguments:** `{}`

**Warrant:** Evaluate addition and subtraction left-to-right after higher-precedence operations. (`operator_precedence`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s3

**Result:** `fact:s4` 13-3+10=10+10

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. The evaluator can check the final closed expression, not expose each provenance-preserving microstep.

**Semantic gaps:** none

**State after:**

`S4` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
- `fact:s4` 13-3+10=10+10 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2
- fact:s3

### Step 5: DISCHARGE_GOAL

**Source span:** &=\boxed{20}.

**Explicitness:** `implicit`

**State before:**

`S4` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
- `fact:s4` 13-3+10=10+10 (established)
**Goals:**
- `goal:answer` value=20 (goal_open)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2
- fact:s3

**Arguments:** `{}`

**Warrant:** Evaluate the final closed expression. (`exact_arithmetic`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s4

**Result:** `fact:s5` value=20

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed exact evaluation is current HML capability.

**Semantic gaps:** none

**State after:**

`S5` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
- `fact:s4` 13-3+10=10+10 (established)
- `fact:s5` value=20 (established)
**Goals:**
- `goal:answer` value=20 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2
- fact:s3
- fact:s4

## Final state

`S5` scope: global
**Objects:**
- closed arithmetic expression
**Types/domains:**
- integer arithmetic
**Facts:**
- `fact:expression` 1+6·2-3+5·4÷2 (given)
- `fact:s1` multiplication/division precede addition/subtraction (established)
- `fact:s2` 1+12-3+20÷2 (established)
- `fact:s3` 1+12-3+10 (established)
- `fact:s4` 13-3+10=10+10 (established)
- `fact:s5` value=20 (established)
**Goals:**
- `goal:answer` value=20 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:expression
- fact:s2
- fact:s3
- fact:s4

**Goal status:** `discharged`

## Operations observed

`APPLY_PRECEDENCE`, `DISCHARGE_GOAL`, `EVALUATE`

## HML gaps exposed

MATH-GAP-0006
