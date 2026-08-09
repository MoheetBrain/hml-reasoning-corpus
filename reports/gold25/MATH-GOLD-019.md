# MATH-GOLD-019

## Original problem

If $x + \frac{1}{x} = \sqrt{3}$, then find $x^{18}$.

## Original solution

Solution 1: We can rewrite the given equation as $x^2 - \sqrt{3} x + 1 = 0$, so by the quadratic formula,
\[x = \frac{\sqrt{3} \pm \sqrt{3 - 4}}{2} = \frac{\sqrt{3} \pm i}{2},\]which means $x = e^{\pi i/6}$ or $x = e^{11 \pi i/6}$.

If $x = e^{\pi i/6}$, then
\[x^{18} = e^{3 \pi i} = -1,\]and if $x = e^{11 \pi i/6}$, then
\[x^{18} = e^{33 \pi i} = -1.\]In either case, $x^{18} = \boxed{-1}$.

Solution 2: Squaring the given equation, we get
\[x^2 + 2 + \frac{1}{x^2} = 3,\]which simplifies to $x^4 - x^2 + 1 = 0$.  Then $(x^2 + 1)(x^4 - x^2 + 1) = 0$, which expands as $x^6 + 1 = 0$.  Therefore, $x^6 = -1$, so $x^{18} = (x^6)^3 = (-1)^3 = \boxed{-1}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)

## Trajectory

### Step 1: CLEAR_DENOMINATOR

**Source span:** We can rewrite the given equation as $x^2 - \sqrt{3} x + 1 = 0$

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)

**Arguments:** `{}`

**Warrant:** Multiply by x, using x≠0. (`denominator_clearing`, source `derived`)

**Preconditions:**
- x≠0 — `satisfied`; The original expression 1/x requires x≠0.

**Obligations created:**
- none

**Dependencies:** fact:reciprocal

**Result:** `fact:s1` x²-√3x+1=0

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: multiply_both_sides, partiality. Multiplication and denominator obligations exist; complex quadratic solving is absent.

**Semantic gaps:** MATH-GAP-0003, MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

### Step 2: SOLVE

**Source span:** so by the quadratic formula,

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

**Arguments:** `{}`

**Warrant:** Apply the quadratic formula over the complex numbers. (`quadratic_formula`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:reciprocal

**Result:** `fact:s2` x=(√3±i)/2

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Quadratic formula and complex-number solving require a library.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

### Step 3: APPLY_IDENTITY

**Source span:** which means $x = e^{\pi i/6}$ or $x = e^{11 \pi i/6}$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

**Arguments:** `{}`

**Warrant:** Convert the two complex roots to exponential/polar form. (`polar_form`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:reciprocal

**Result:** `fact:s3` two unit-complex candidate forms

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Complex polar conversion is not a core HML rule.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S3` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

### Step 4: CASE_SPLIT

**Source span:** If $x = e^{\pi i/6}$, then

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

**Arguments:** `{}`

**Warrant:** Evaluate the target power in the first root branch. (`case_evaluation`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:reciprocal

**Result:** `fact:s4` branch 1 x¹⁸=e^{3πi}=-1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: scope. Scope exists but no complex-power case evaluator.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0007

**State after:**

`S4` scope: global, branch:root 1
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

### Step 5: CASE_SPLIT

**Source span:** and if $x = e^{11 \pi i/6}$, then

**Explicitness:** `explicit`

**State before:**

`S4` scope: global, branch:root 1
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

**Arguments:** `{}`

**Warrant:** Evaluate the target power in the second root branch. (`case_evaluation`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:reciprocal

**Result:** `fact:s5` branch 2 x¹⁸=e^{33πi}=-1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: scope. Scope exists but no complex-power case evaluator.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0007

**State after:**

`S5` scope: global, branch:root 1, branch:root 2
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
- `fact:s5` branch 2 x¹⁸=e^{33πi}=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

### Step 6: COMBINE_CASES

**Source span:** In either case, $x^{18} = \boxed{-1}$.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global, branch:root 1, branch:root 2
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
- `fact:s5` branch 2 x¹⁸=e^{33πi}=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Dependencies:**
- fact:reciprocal

**Arguments:** `{}`

**Warrant:** Merge the two complete root cases because their target values agree. (`case_invariant`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- `obl:root_case_join` both complex-root branches are covered before the invariant is global — `discharged`

**Dependencies:** fact:root_1, fact:root_2

**Result:** `fact:s6` both branches give x¹⁸=-1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: goal. No branch-merge or complex-equality rule.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0004, MATH-GAP-0007

**State after:**

`S6` scope: global, branch:root 1, branch:root 2
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
- `fact:s5` branch 2 x¹⁸=e^{33πi}=-1 (established)
- `fact:s6` both branches give x¹⁸=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_open)
**Discharged obligations:**
- `obl:root_case_join` both complex-root branches are covered before the invariant is global (discharged)
**Dependencies:**
- fact:reciprocal
- fact:root_1
- fact:root_2

## Final state

`S6` scope: global, branch:root 1, branch:root 2
**Objects:**
- x
**Declarations:**
- x : Complex
**Types/domains:**
- x≠0
**Facts:**
- `fact:reciprocal` x+1/x=√3 (given)
- `fact:s1` x²-√3x+1=0 (established)
- `fact:s2` x=(√3±i)/2 (established)
- `fact:s3` two unit-complex candidate forms (established)
- `fact:s4` branch 1 x¹⁸=e^{3πi}=-1 (established)
- `fact:s5` branch 2 x¹⁸=e^{33πi}=-1 (established)
- `fact:s6` both branches give x¹⁸=-1 (established)
**Goals:**
- `goal:answer` x¹⁸=-1 (goal_discharged)
**Discharged obligations:**
- `obl:root_case_join` both complex-root branches are covered before the invariant is global (discharged)
**Dependencies:**
- fact:reciprocal
- fact:root_1
- fact:root_2

**Goal status:** `discharged`

## Operations observed

`APPLY_IDENTITY`, `CASE_SPLIT`, `CLEAR_DENOMINATOR`, `COMBINE_CASES`, `SOLVE`

## HML gaps exposed

MATH-GAP-0001, MATH-GAP-0003, MATH-GAP-0004, MATH-GAP-0007
