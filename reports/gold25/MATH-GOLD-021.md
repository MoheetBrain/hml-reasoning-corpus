# MATH-GOLD-021

## Original problem

The hypotenuse of a right triangle whose legs are consecutive whole numbers is 29 units. What is the sum of the lengths of the two legs?

## Original solution

Let's call the length of the shorter leg $x$. Then the length of the longer leg is $x + 1$. Using the Pythagorean Theorem, we write the equation $x^2 + (x + 1)^2 = 29^2$ and solve for $x$. Expanding $(x + 1)^2$, we get $x
^2 + x^2 + 2x + 1 = 841$. This can be simplified to $2x^2 + 2x = 840$, or $x^2 + x = 420$. Factoring out $x$ on the left, we can rewrite it as $x(x + 1) = 420$. In other words, the product of these two consecutive numbers is 420, which means they must each be close to the square root of 420. Indeed, $20 \times 21 = 420$, so the legs must be 20 and 21. Their sum is $20 + 21 = \boxed{41}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** Let's call the length of the shorter leg $x$. Then the length of the longer leg is $x + 1$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)

**Arguments:** `{}`

**Warrant:** Parameterize consecutive whole-number legs by x and x+1. (`consecutive_integer_definition`, source `explicit`)

**Preconditions:**
- x≥1 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` legs x and x+1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: var. Variable declarations are native; consecutiveness is a constraint.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)

### Step 2: FORMULATE_EQUATION

**Source span:** Using the Pythagorean Theorem, we write the equation $x^2 + (x + 1)^2 = 29^2$

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply the Pythagorean theorem to a right triangle. (`pythagorean_theorem`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:hypotenuse, fact:consecutive

**Result:** `fact:s2` x²+(x+1)²=29²

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. The theorem is not a trusted HML rule.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive

### Step 3: EXPAND

**Source span:** Expanding $(x + 1)^2$, we get

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive

**Arguments:** `{}`

**Warrant:** Expand the square and evaluate 29². (`polynomial_expansion`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` 2x²+2x+1=841

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Symbolic expansion is not a trusted kernel rule.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S3` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2

### Step 4: FACTOR

**Source span:** This can be simplified to $2x^2 + 2x = 840$, or $x^2 + x = 420$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2

**Arguments:** `{}`

**Warrant:** Collect terms, divide by 2, and factor out x. (`factorization`, source `derived`)

**Preconditions:**
- 2≠0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:s3

**Result:** `fact:s4` x(x+1)=420

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: divide_both_sides. The scalar division is native; symbolic factoring is not.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S4` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3

### Step 5: SELECT_CANDIDATE

**Source span:** Indeed, $20 \times 21 = 420$, so the legs must be 20 and 21.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3

**Arguments:** `{}`

**Warrant:** Select the consecutive positive factor pair solving x(x+1)=420. (`finite_factor_search`, source `derived`)

**Preconditions:**
- x and x+1 are positive consecutive integers — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:s4

**Result:** `fact:s5` legs=(20,21)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite factor search has no trusted HML rule.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S5` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
- `fact:s5` legs=(20,21) (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3
- fact:s4

### Step 6: EVALUATE

**Source span:** Their sum is $20 + 21 = \boxed{41}$.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
- `fact:s5` legs=(20,21) (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3
- fact:s4

**Arguments:** `{}`

**Warrant:** Add the two established leg lengths. (`exact_arithmetic`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s5

**Result:** `fact:s6` leg sum=41

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed arithmetic is checkable.

**Semantic gaps:** none

**State after:**

`S6` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
- `fact:s5` legs=(20,21) (established)
- `fact:s6` leg sum=41 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_open)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3
- fact:s4
- fact:s5

## Final state

`S6` scope: global
**Objects:**
- right triangle
- x
**Declarations:**
- x : Natural
**Types/domains:**
- legs x and x+1; hypotenuse 29
**Facts:**
- `fact:hypotenuse` c=29 (given)
- `fact:consecutive` legs are x and x+1 (given)
- `fact:s1` legs x and x+1 (established)
- `fact:s2` x²+(x+1)²=29² (established)
- `fact:s3` 2x²+2x+1=841 (established)
- `fact:s4` x(x+1)=420 (established)
- `fact:s5` legs=(20,21) (established)
- `fact:s6` leg sum=41 (established)
**Goals:**
- `goal:answer` leg sum=41 (goal_discharged)
**Dependencies:**
- fact:hypotenuse
- fact:consecutive
- fact:s2
- fact:s3
- fact:s4
- fact:s5

**Goal status:** `discharged`

## Operations observed

`EVALUATE`, `EXPAND`, `FACTOR`, `FORMULATE_EQUATION`, `INTRODUCE_VARIABLE`, `SELECT_CANDIDATE`

## HML gaps exposed

MATH-GAP-0006, MATH-GAP-0007, MATH-GAP-0009
