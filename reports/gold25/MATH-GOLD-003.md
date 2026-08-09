# MATH-GOLD-003

## Original problem

Solve the following equation for $x$: \[ \ \frac{2}{3} = \frac{4}{x-5}.\]

## Original solution

Multiplying both sides by $x-5$ and by 3 gives $2(x-5) = 4(3)$.  Expanding the left side gives $2x-10 = 12$.  Adding 10 to both sides gives $2x = 22$ and dividing by 2 gives $x = \boxed{11}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
**Goals:**
- `goal:answer` x=11 (goal_open)

## Trajectory

### Step 1: CROSS_MULTIPLY

**Source span:** Multiplying both sides by $x-5$ and by 3 gives $2(x-5) = 4(3)$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
**Goals:**
- `goal:answer` x=11 (goal_open)

**Arguments:** `{}`

**Warrant:** Multiply both sides by the common factors. (`equality_preservation`, source `derived`)

**Preconditions:**
- x-5≠0 — `implicit`; The worked solution does not state this condition explicitly.
- 3≠0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- `obl:denominator` x-5≠0 — `discharged`

**Dependencies:** fact:eq

**Result:** `fact:s1` 2(x-5)=12

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: multiply_both_sides, partiality. HML can multiply both sides; denominator obligations are term-level, but cross-multiplication as a compound operation is absent.

**Semantic gaps:** MATH-GAP-0003

**State after:**

`S1` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

### Step 2: EXPAND

**Source span:** Expanding the left side gives $2x-10 = 12$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

**Arguments:** `{}`

**Warrant:** Apply the distributive law. (`distributive_law`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:eq

**Result:** `fact:s2` 2x-10=12

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. No trusted symbolic expansion rule is registered.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S2` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

### Step 3: ADD_BOTH_SIDES

**Source span:** Adding 10 to both sides gives $2x = 22$

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

**Arguments:** `{}`

**Warrant:** Add the same term to both sides. (`equality_preservation`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:eq

**Result:** `fact:s3` 2x=22

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: add_both_sides. Current HML has the corresponding trusted rule.

**Semantic gaps:** none

**State after:**

`S3` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
- `fact:s3` 2x=22 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

### Step 4: DIVIDE_BOTH_SIDES

**Source span:** and dividing by 2 gives $x = \boxed{11}$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
- `fact:s3` 2x=22 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

**Arguments:** `{}`

**Warrant:** Divide both sides by the nonzero coefficient 2. (`equality_preservation`, source `core`)

**Preconditions:**
- 2≠0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:eq

**Result:** `fact:s4` x=11

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: divide_both_sides. The division rule is current; its obligation is discharged by the literal nonzero divisor.

**Semantic gaps:** none

**State after:**

`S4` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
- `fact:s3` 2x=22 (established)
- `fact:s4` x=11 (established)
**Goals:**
- `goal:answer` x=11 (goal_open)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

## Final state

`S4` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:eq` 2/3=4/(x-5) (given)
- `fact:s1` 2(x-5)=12 (established)
- `fact:s2` 2x-10=12 (established)
- `fact:s3` 2x=22 (established)
- `fact:s4` x=11 (established)
**Goals:**
- `goal:answer` x=11 (goal_discharged)
**Discharged obligations:**
- `obl:denominator` x-5≠0 (discharged)
**Dependencies:**
- fact:eq

**Goal status:** `discharged`

## Operations observed

`ADD_BOTH_SIDES`, `CROSS_MULTIPLY`, `DIVIDE_BOTH_SIDES`, `EXPAND`

## HML gaps exposed

MATH-GAP-0003, MATH-GAP-0006
