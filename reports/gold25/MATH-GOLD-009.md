# MATH-GOLD-009

## Original problem

Let $x,$ $y,$ $z$ be positive real numbers such that $xyz = 8.$  Find the minimum value of $x + 2y + 4z.$

## Original solution

By AM-GM,
\[x + 2y + 4z \ge 3 \sqrt[3]{(x)(2y)(4z)} = 3 \sqrt[3]{8xyz} = 3 \sqrt[3]{8 \cdot 8} = 12.\]Equality occurs when $x = 2y = 4z$ and $xyz = 8.$  We can solve to get $x = 4,$ $y = 2,$ and $z = 1,$ so the minimum value is $\boxed{12}.$

## Canonical initial state

`S0` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)

## Trajectory

### Step 1: APPLY_THEOREM

**Source span:** By AM-GM,

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply AM-GM to the three positive quantities x, 2y, and 4z. (`AM_GM`, source `library`)

**Preconditions:**
- x>0,y>0,z>0 — `satisfied`; Given in the problem.
- three positive terms — `satisfied`; x,2y,4z are positive.

**Obligations created:**
- none

**Dependencies:** fact:product

**Result:** `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z))

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. AM-GM is not a core HML rule or trusted library checker.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product

### Step 2: EVALUATE

**Source span:** = 3 \sqrt[3]{8xyz} = 3 \sqrt[3]{8 \cdot 8} = 12.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product

**Arguments:** `{}`

**Warrant:** Substitute xyz=8 and evaluate the exact cube root. (`exact_arithmetic`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` x+2y+4z≥12

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Only the closed numeric subexpression is directly certifiable.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product
- fact:s1

### Step 3: RECORD_EQUALITY_CONDITION

**Source span:** Equality occurs when $x = 2y = 4z$ and $xyz = 8.$

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product
- fact:s1

**Arguments:** `{}`

**Warrant:** Use the equality condition of AM-GM together with the product constraint. (`AM_GM_equality`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1, fact:product

**Result:** `fact:s3` equality condition x=2y=4z

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. The equality condition requires theorem-library semantics.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S3` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
- `fact:s3` equality condition x=2y=4z (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product
- fact:s1

### Step 4: SOLVE

**Source span:** We can solve to get $x = 4,$ $y = 2,$ and $z = 1,

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
- `fact:s3` equality condition x=2y=4z (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product
- fact:s1

**Arguments:** `{}`

**Warrant:** Solve the equality condition and verify the product constraint. (`constraint_solving`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s3, fact:product

**Result:** `fact:s4` witness (x,y,z)=(4,2,1) attains 12

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: evidence. HML can record the witness and closed checks but cannot invoke AM-GM.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S4` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
- `fact:s3` equality condition x=2y=4z (established)
- `fact:s4` witness (x,y,z)=(4,2,1) attains 12 (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_open)
**Dependencies:**
- fact:product
- fact:s1
- fact:s3

## Final state

`S4` scope: global
**Objects:**
- x
- y
- z
**Declarations:**
- x : PositiveReal
- y : PositiveReal
- z : PositiveReal
**Types/domains:**
- x,y,z>0
**Facts:**
- `fact:product` xyz=8 (given)
- `fact:s1` x+2y+4z ≥ 3∛((x)(2y)(4z)) (established)
- `fact:s2` x+2y+4z≥12 (established)
- `fact:s3` equality condition x=2y=4z (established)
- `fact:s4` witness (x,y,z)=(4,2,1) attains 12 (established)
**Goals:**
- `goal:answer` min(x+2y+4z)=12 (goal_discharged)
**Dependencies:**
- fact:product
- fact:s1
- fact:s3

**Goal status:** `discharged`

## Operations observed

`APPLY_THEOREM`, `EVALUATE`, `RECORD_EQUALITY_CONDITION`, `SOLVE`

## HML gaps exposed

MATH-GAP-0007
