# MATH-GOLD-001

## Original problem

Let \[f(x) = \left\{
\begin{array}{cl} ax+3, &\text{ if }x>2, \\
x-5 &\text{ if } -2 \le x \le 2, \\
2x-b &\text{ if } x <-2.
\end{array}
\right.\]Find $a+b$ if the piecewise function is continuous (which means that its graph can be drawn without lifting your pencil from the paper).

## Original solution

For the piecewise function to be continuous, the cases must "meet" at $2$ and $-2$. For example, $ax+3$ and $x-5$ must be equal when $x=2$. This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \Rightarrow a=-3$. Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$. Substituting, we get $-2-5=2(-2)-b$, which implies $b=3$. So $a+b=-3+3=\boxed{0}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
**Goals:**
- `goal:answer` a+b=0 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** For the piecewise function to be continuous, the cases must "meet" at $2$ and $-2$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
**Goals:**
- `goal:answer` a+b=0 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply the definition of continuity for a piecewise function at a boundary. (`definition_application`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: def, assume. Definitions and assumptions can state the branches; no continuity theorem is in the kernel.

**Semantic gaps:** MATH-GAP-0005

**State after:**

`S1` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)

### Step 2: FORMULATE_EQUATION

**Source span:** For example, $ax+3$ and $x-5$ must be equal when $x=2$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)

**Arguments:** `{"boundary": 2}`

**Warrant:** Continuity requires equal one-sided branch values at the boundary. (`boundary_matching`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:piecewise

**Result:** `fact:s2` 2a+3=-3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: assume. The equation is representable as an assumption, but boundary-continuity construction is not a rule.

**Semantic gaps:** MATH-GAP-0005

**State after:**

`S2` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

### Step 3: SOLVE

**Source span:** This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \Rightarrow a=-3$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

**Arguments:** `{}`

**Warrant:** Subtract 3 and divide by the nonzero coefficient 2. (`equality_preservation`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:piecewise

**Result:** `fact:s3` a=-3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: subtract_both_sides, divide_both_sides. The transformations are kernel rules; the general solve operation is not.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S3` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

### Step 4: FORMULATE_EQUATION

**Source span:** Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

**Arguments:** `{"boundary": -2}`

**Warrant:** Continuity requires equal adjacent branch values at the second boundary. (`boundary_matching`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:piecewise

**Result:** `fact:s4` -7=-4-b

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: assume. Representable proposition; no continuity/boundary rule.

**Semantic gaps:** MATH-GAP-0005

**State after:**

`S4` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

### Step 5: SOLVE

**Source span:** Substituting, we get $-2-5=2(-2)-b$, which implies $b=3$.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

**Arguments:** `{}`

**Warrant:** Substitute the boundary value and isolate b. (`equality_preservation`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:piecewise

**Result:** `fact:s5` b=3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: substitute, add_both_sides. Only local equality transformations are trusted.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S5` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
- `fact:s5` b=3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

### Step 6: EVALUATE

**Source span:** So $a+b=-3+3=\boxed{0}$.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
- `fact:s5` b=3 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise

**Arguments:** `{}`

**Warrant:** Evaluate the established parameter values exactly. (`exact_arithmetic`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:a, fact:b

**Result:** `fact:s6` a+b=0

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed arithmetic can be checked as evidence; it is not a kernel derivation.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S6` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
- `fact:s5` b=3 (established)
- `fact:s6` a+b=0 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_open)
**Dependencies:**
- fact:piecewise
- fact:a
- fact:b

## Final state

`S6` scope: global
**Objects:**
- piecewise function f
- a
- b
**Declarations:**
- a : Real
- b : Real
- f : PiecewiseFunction
**Types/domains:**
- a,b ∈ Real
**Facts:**
- `fact:piecewise` f(x)=ax+3 for x>2; x-5 for -2≤x≤2; 2x-b for x<-2 (given)
- `fact:s1` continuity reduces to matching adjacent branch values at x=2 and x=-2 (established)
- `fact:s2` 2a+3=-3 (established)
- `fact:s3` a=-3 (established)
- `fact:s4` -7=-4-b (established)
- `fact:s5` b=3 (established)
- `fact:s6` a+b=0 (established)
**Goals:**
- `goal:answer` a+b=0 (goal_discharged)
**Dependencies:**
- fact:piecewise
- fact:a
- fact:b

**Goal status:** `discharged`

## Operations observed

`EVALUATE`, `FORMULATE_EQUATION`, `INTRODUCE_VARIABLE`, `SOLVE`

## HML gaps exposed

MATH-GAP-0005, MATH-GAP-0006
