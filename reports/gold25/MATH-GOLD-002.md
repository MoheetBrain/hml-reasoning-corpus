# MATH-GOLD-002

## Original problem

The sum of the squares of two positive integers is 90. The product of the two integers is 27. What is the sum of the two integers?

## Original solution

Call the two integers $x$ and $y$. We are given that $x^2 + y^2 = 90$ and that $xy = 27$. We want to find $x + y$. Note that $(x + y)^2 = x^2 + y^2 + 2xy = 90 + 2\cdot 27 = 144$. Taking the square root of 144, we see that $x + y = \boxed{12}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** Call the two integers $x$ and $y$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

**Arguments:** `{}`

**Warrant:** Name the objects already quantified by the problem. (`variable_binding`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` x and y denote the two positive integers

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: var. HML can declare typed variables.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

### Step 2: RECORD_GIVEN

**Source span:** We are given that $x^2 + y^2 = 90$ and that $xy = 27$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

**Arguments:** `{}`

**Warrant:** Translate the given numerical constraints into state facts. (`problem_translation`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s2` facts x²+y²=90 and xy=27 are active

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: assume. HML can record the facts but has no source-prose ingestion operation.

**Semantic gaps:** none

**State after:**

`S2` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

### Step 3: APPLY_IDENTITY

**Source span:** Note that $(x + y)^2 = x^2 + y^2 + 2xy = 90 + 2\cdot 27 = 144$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)

**Arguments:** `{}`

**Warrant:** Use the square-of-a-sum identity and substitute established facts. (`polynomial_identity`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` (x+y)²=144

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. The exact evaluator cannot establish this open-variable identity; no kernel identity rule covers it.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S3` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
- `fact:s3` (x+y)²=144 (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)
**Dependencies:**
- fact:s2

### Step 4: EXTRACT_ROOT

**Source span:** Taking the square root of 144, we see that $x + y = \boxed{12}$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
- `fact:s3` (x+y)²=144 (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)
**Dependencies:**
- fact:s2

**Arguments:** `{}`

**Warrant:** Because x and y are positive, x+y is nonnegative, so the principal square root selects 12. (`nonnegative_root`, source `derived`)

**Preconditions:**
- x+y≥0 — `satisfied`; x and y are positive integers from the problem.

**Obligations created:**
- `obl:root_sign` x+y≥0 selects the principal square root — `discharged`

**Dependencies:** fact:s3

**Result:** `fact:s4` x+y=12

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1, evidence. HML can check closed 144=12², but not the free-variable identity and sign-directed root step.

**Semantic gaps:** MATH-GAP-0003, MATH-GAP-0004, MATH-GAP-0006

**State after:**

`S4` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
- `fact:s3` (x+y)²=144 (established)
- `fact:s4` x+y=12 (established)
**Goals:**
- `goal:answer` x+y=12 (goal_open)
**Discharged obligations:**
- `obl:root_sign` x+y≥0 selects the principal square root (discharged)
**Dependencies:**
- fact:s2
- fact:s3

## Final state

`S4` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Integer
- y : Integer
**Types/domains:**
- x,y are positive integers
**Facts:**
- `fact:squares` x²+y²=90 (given)
- `fact:product` xy=27 (given)
- `fact:s1` x and y denote the two positive integers (established)
- `fact:s2` facts x²+y²=90 and xy=27 are active (established)
- `fact:s3` (x+y)²=144 (established)
- `fact:s4` x+y=12 (established)
**Goals:**
- `goal:answer` x+y=12 (goal_discharged)
**Discharged obligations:**
- `obl:root_sign` x+y≥0 selects the principal square root (discharged)
**Dependencies:**
- fact:s2
- fact:s3

**Goal status:** `discharged`

## Operations observed

`APPLY_IDENTITY`, `EXTRACT_ROOT`, `INTRODUCE_VARIABLE`, `RECORD_GIVEN`

## HML gaps exposed

MATH-GAP-0003, MATH-GAP-0004, MATH-GAP-0006
