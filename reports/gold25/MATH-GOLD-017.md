# MATH-GOLD-017

## Original problem

How many positive factors of 72 are perfect cubes?

## Original solution

Prime factorize $72$ as $2^3\cdot 3^2$.  A positive integer is a factor of 72 if and only if the exponents in its prime factorization are less than or equal to the corresponding exponents in the prime factorization of 72.  Also, a positive integer is a perfect cube if and only if every exponent is a multiple of 3.  Therefore, in forming a perfect cube factor of 72, we have 2 choices for the exponent of $2$ (either 0 or 3) and only 1 choice for the exponent of 3 (namely 0).  There are $2\cdot 1=\boxed{2}$ ways to make these choices.

## Canonical initial state

`S0` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
**Goals:**
- `goal:answer` count=2 (goal_open)

## Trajectory

### Step 1: PRIME_FACTORIZE

**Source span:** Prime factorize $72$ as $2^3\cdot 3^2$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
**Goals:**
- `goal:answer` count=2 (goal_open)

**Arguments:** `{}`

**Warrant:** Use unique prime factorization. (`unique_factorization`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` 72=2³·3²

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Prime factorization is not a current HML rule.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S1` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
**Goals:**
- `goal:answer` count=2 (goal_open)

### Step 2: APPLY_DEFINITION

**Source span:** A positive integer is a factor of 72 if and only if the exponents in its prime factorization are less than or equal to the corresponding exponents in the prime factorization of 72.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
**Goals:**
- `goal:answer` count=2 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply the prime-exponent characterization of divisors. (`factor_definition`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Divisor-set construction is library-level.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S2` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1

### Step 3: APPLY_DEFINITION

**Source span:** Also, a positive integer is a perfect cube if and only if every exponent is a multiple of 3.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Apply the exponent characterization of perfect cubes. (`perfect_power_definition`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s3` e₂,e₃ must be multiples of 3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Perfect-power theorem is not in the core.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S3` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1

### Step 4: COUNT_CASES

**Source span:** Therefore, in forming a perfect cube factor of 72

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Intersect divisor bounds with cube-exponent constraints. (`finite_constraint_intersection`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2, fact:s3

**Result:** `fact:s4` admissible exponent choices: e₂∈{0,3}, e₃=0

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite exponent enumeration is library-level.

**Semantic gaps:** MATH-GAP-0008, MATH-GAP-0009

**State after:**

`S4` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
- `fact:s4` admissible exponent choices: e₂∈{0,3}, e₃=0 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3

### Step 5: COMBINE_CASE_COUNTS

**Source span:** There are $2\cdot 1=\boxed{2}$ ways to make these choices.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
- `fact:s4` admissible exponent choices: e₂∈{0,3}, e₃=0 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3

**Arguments:** `{}`

**Warrant:** Multiply independent exponent-choice counts. (`product_rule`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s4

**Result:** `fact:s5` count=2

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Numeric multiplication is checkable after number-theory semantics are supplied.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S5` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
- `fact:s4` admissible exponent choices: e₂∈{0,3}, e₃=0 (established)
- `fact:s5` count=2 (established)
**Goals:**
- `goal:answer` count=2 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:s4

## Final state

`S5` scope: global
**Objects:**
- positive factors of 72
**Declarations:**
- m : Natural
**Types/domains:**
- m|72 and m is a perfect cube
**Facts:**
- `fact:factorization` 72=2³·3² (given)
- `fact:s1` 72=2³·3² (established)
- `fact:s2` factor exponents satisfy 0≤e₂≤3 and 0≤e₃≤2 (established)
- `fact:s3` e₂,e₃ must be multiples of 3 (established)
- `fact:s4` admissible exponent choices: e₂∈{0,3}, e₃=0 (established)
- `fact:s5` count=2 (established)
**Goals:**
- `goal:answer` count=2 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:s4

**Goal status:** `discharged`

## Operations observed

`APPLY_DEFINITION`, `COMBINE_CASE_COUNTS`, `COUNT_CASES`, `PRIME_FACTORIZE`

## HML gaps exposed

MATH-GAP-0008, MATH-GAP-0009
