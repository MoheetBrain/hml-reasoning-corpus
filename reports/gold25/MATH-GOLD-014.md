# MATH-GOLD-014

## Original problem

The four-digit number $\underline{374n}$ is divisible by 18. Find the units digit $n$.

## Original solution

We know that the prime factorization of 18 is $2\cdot 3^2$, so in order for the four digit number to be divisible by 18 it must also be divisible by 9 and 2. In order for a number to be divisible by 9, the sum of its digits must be divisible by 9 as well. Thus, $3+7+4+n$, or $14+n$, must be divisible by 9. Since 18 is the smallest multiple of 9 that is greater than 10, $14+n=18$, and $n=18-14=\boxed{4}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
**Goals:**
- `goal:answer` n=4 (goal_open)

## Trajectory

### Step 1: APPLY_THEOREM

**Source span:** We know that the prime factorization of 18 is $2\cdot 3^2$, so in order for the four digit number to be divisible by 18 it must also be divisible by 9 and 2.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
**Goals:**
- `goal:answer` n=4 (goal_open)

**Arguments:** `{}`

**Warrant:** A number divisible by 18 is divisible by each prime-power factor 2 and 9. (`divisibility_factorization`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:number, fact:divisor

**Result:** `fact:s1` 374n must be divisible by 9 and by 2

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Number-theoretic divisibility theorems are not trusted core rules.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S1` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor

### Step 2: APPLY_THEOREM

**Source span:** In order for a number to be divisible by 9, the sum of its digits must be divisible by 9 as well.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor

**Arguments:** `{}`

**Warrant:** Apply the base-10 divisibility-by-9 theorem. (`digit_sum_rule`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` 14+n is divisible by 9

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Digit-sum divisibility requires a number-theory library.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S2` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1

### Step 3: BOUND_SEARCH

**Source span:** Thus, $3+7+4+n$, or $14+n$, must be divisible by 9.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1

**Arguments:** `{}`

**Warrant:** Use n∈{0,…,9} to bound the possible multiples of 9. (`finite_digit_domain`, source `derived`)

**Preconditions:**
- 0≤n≤9 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` 14+n ∈ {18,27} under digit bound

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite constraint search is not a kernel operation.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S3` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
- `fact:s3` 14+n ∈ {18,27} under digit bound (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1
- fact:s2

### Step 4: SELECT_CANDIDATE

**Source span:** Since 18 is the smallest multiple of 9 that is greater than 10, $14+n=18$, and $n=18-14=\boxed{4}$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
- `fact:s3` 14+n ∈ {18,27} under digit bound (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1
- fact:s2

**Arguments:** `{}`

**Warrant:** Select the digit-compatible multiple and compute n. (`minimal_candidate`, source `derived`)

**Preconditions:**
- 374n divisible by 2 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** fact:s3

**Result:** `fact:s4` n=4

**Verification:** `verified` / `VERIFIED_EXACT` — The source omits the final explicit evenness check; 3744 is even and divisible by 9, so the conclusion is valid.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Divisibility and finite digit search are library-level.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S4` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
- `fact:s3` 14+n ∈ {18,27} under digit bound (established)
- `fact:s4` n=4 (established)
**Goals:**
- `goal:answer` n=4 (goal_open)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1
- fact:s2
- fact:s3

## Final state

`S4` scope: global
**Objects:**
- digit n
**Declarations:**
- n : Digit
**Types/domains:**
- n∈{0,…,9}
**Facts:**
- `fact:number` 374n (given)
- `fact:divisor` 18=2·3² (given)
- `fact:s1` 374n must be divisible by 9 and by 2 (established)
- `fact:s2` 14+n is divisible by 9 (established)
- `fact:s3` 14+n ∈ {18,27} under digit bound (established)
- `fact:s4` n=4 (established)
**Goals:**
- `goal:answer` n=4 (goal_discharged)
**Dependencies:**
- fact:number
- fact:divisor
- fact:s1
- fact:s2
- fact:s3

**Goal status:** `discharged`

## Operations observed

`APPLY_THEOREM`, `BOUND_SEARCH`, `SELECT_CANDIDATE`

## HML gaps exposed

MATH-GAP-0009
