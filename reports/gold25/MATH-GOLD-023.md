# MATH-GOLD-023

## Original problem

A stick 5 cm long, a stick 9 cm long, and a third stick $n$ cm long form a triangle. What is the sum of all possible whole number values of $n$?

## Original solution

Using the Triangle Inequality, we see that $n > 4$ and $n < 14,$ so $n$ can be any integer from $5$ to $13,$ inclusive. The sum can be calculated in several ways, but regardless, $5 + 6 + 7 + 8 + 9 + 10 + 11 + 12 + 13 = \boxed{81}.$

## Canonical initial state

`S0` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)

## Trajectory

### Step 1: APPLY_THEOREM

**Source span:** Using the Triangle Inequality

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)

**Arguments:** `{}`

**Warrant:** A triangle exists exactly when each side is less than the sum of the other two; with sides 5 and 9 this bounds n. (`triangle_inequality`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:sides

**Result:** `fact:s1` 4<n<14

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Triangle inequality is not a trusted core theorem.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)
**Dependencies:**
- fact:sides

### Step 2: ENUMERATE

**Source span:** so $n$ can be any integer from $5$ to $13,$ inclusive.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)
**Dependencies:**
- fact:sides

**Arguments:** `{}`

**Warrant:** Intersect the open real interval with the integer domain. (`integer_interval_enumeration`, source `derived`)

**Preconditions:**
- n∈Natural — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` valid n={5,6,7,8,9,10,11,12,13}

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite interval enumeration is not native.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S2` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
- `fact:s2` valid n={5,6,7,8,9,10,11,12,13} (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)
**Dependencies:**
- fact:sides
- fact:s1

### Step 3: EVALUATE

**Source span:** The sum can be calculated in several ways, but regardless

**Explicitness:** `implicit`

**State before:**

`S2` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
- `fact:s2` valid n={5,6,7,8,9,10,11,12,13} (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)
**Dependencies:**
- fact:sides
- fact:s1

**Arguments:** `{}`

**Warrant:** Sum every valid integer exactly once. (`finite_sum`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` sum=81

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. The final arithmetic is checkable; interval derivation is not.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S3` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
- `fact:s2` valid n={5,6,7,8,9,10,11,12,13} (established)
- `fact:s3` sum=81 (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_open)
**Dependencies:**
- fact:sides
- fact:s1
- fact:s2

## Final state

`S3` scope: global
**Objects:**
- sticks 5cm, 9cm, ncm
**Declarations:**
- n : Natural
**Types/domains:**
- n is a whole-number side length
**Facts:**
- `fact:sides` 5,9,n form a triangle (given)
- `fact:s1` 4<n<14 (established)
- `fact:s2` valid n={5,6,7,8,9,10,11,12,13} (established)
- `fact:s3` sum=81 (established)
**Goals:**
- `goal:answer` sum of valid n=81 (goal_discharged)
**Dependencies:**
- fact:sides
- fact:s1
- fact:s2

**Goal status:** `discharged`

## Operations observed

`APPLY_THEOREM`, `ENUMERATE`, `EVALUATE`

## HML gaps exposed

MATH-GAP-0007, MATH-GAP-0010
