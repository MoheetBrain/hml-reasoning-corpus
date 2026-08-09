# MATH-GOLD-007

## Original problem

Two real numbers $x$ and $y$ satisfy $x-y=4$ and $x^3-y^3=28$.  Compute $xy$.

## Original solution

Solution 1. The first equation gives $x = y+4$. Substituting into the second equation, we get \[(y+4)^3 - y^3 = 28 \implies 12y^2 + 48y + 36 = 0.\]Thus, $y^2 + 4y + 3 = 0$, so $(y+1)(y+3) = 0$. Therefore, either $y=-1$ and $x=y+4=3$, or $y=-3$ and $x=y+4=1$. Either way, $xy = \boxed{-3}$.

Solution 2. The second equation factors via difference of cubes, as \[(x-y)(x^2+xy+y^2) = 28.\]Since $x-y=4$, we have $x^2+xy+y^2=\frac{28}{4} =7$. Now, squaring the first equation, we get $x^2-2xy+y^2=16$. Thus, \[3xy = (x^2+xy+y^2) - (x^2-2xy+y^2) = 7-16=-9,\]so $xy = \frac{-9}{3} = \boxed{-3}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
**Goals:**
- `goal:answer` xy=-3 (goal_open)

## Trajectory

### Step 1: SUBSTITUTE

**Source span:** The first equation gives $x = y+4$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
**Goals:**
- `goal:answer` xy=-3 (goal_open)

**Arguments:** `{}`

**Warrant:** Add y to both sides of x-y=4. (`equality_preservation`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:diff

**Result:** `fact:s1` x=y+4

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: add_both_sides. Native equality transformation can express this local step.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff

### Step 2: SUBSTITUTE

**Source span:** Substituting into the second equation, we get

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff

**Arguments:** `{}`

**Warrant:** Replace x by y+4 in the cubic equation. (`equality_substitution`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:diff, fact:cubes

**Result:** `fact:s2` (y+4)³-y³=28

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: substitute. Current HML has the corresponding trusted rule.

**Semantic gaps:** none

**State after:**

`S2` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

### Step 3: EXPAND

**Source span:** 12y^2 + 48y + 36 = 0.

**Explicitness:** `implicit`

**State before:**

`S2` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

**Arguments:** `{}`

**Warrant:** Expand and collect polynomial terms. (`polynomial_expansion`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:cubes

**Result:** `fact:s3` 12y²+48y+36=0

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. No trusted symbolic polynomial expansion rule.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S3` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

### Step 4: FACTOR

**Source span:** Thus, $y^2 + 4y + 3 = 0$, so $(y+1)(y+3) = 0$.

**Explicitness:** `implicit`

**State before:**

`S3` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

**Arguments:** `{}`

**Warrant:** Scale the equation and factor the quadratic. (`factorization`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:cubes

**Result:** `fact:s4` (y+1)(y+3)=0

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Symbolic factorization is not trusted in current HML.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S4` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

### Step 5: CASE_SPLIT

**Source span:** Therefore, either $y=-1$ and $x=y+4=3$, or $y=-3$ and $x=y+4=1$.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

**Arguments:** `{}`

**Warrant:** A product is zero only when at least one factor is zero, then recover x by substitution. (`zero_product_property`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:diff, fact:cubes

**Result:** `fact:s5` candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: scope. Case scopes exist, but no zero-product/case coverage rule is in the kernel.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0007

**State after:**

`S5` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
- `fact:s5` candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3) (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

### Step 6: EVALUATE

**Source span:** Either way, $xy = \boxed{-3}$.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
- `fact:s5` candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3) (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes

**Arguments:** `{}`

**Warrant:** Evaluate the requested expression in every surviving branch. (`case_invariant`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:candidate_1, fact:candidate_2

**Result:** `fact:s6` both candidates yield xy=-3

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed branch-local arithmetic is checkable; branch merge is not native.

**Semantic gaps:** MATH-GAP-0001

**State after:**

`S6` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
- `fact:s5` candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3) (established)
- `fact:s6` both candidates yield xy=-3 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_open)
**Dependencies:**
- fact:diff
- fact:cubes
- fact:candidate_1
- fact:candidate_2

## Final state

`S6` scope: global
**Objects:**
- x
- y
**Declarations:**
- x : Real
- y : Real
**Types/domains:**
- x,y ∈ Real
**Facts:**
- `fact:diff` x-y=4 (given)
- `fact:cubes` x³-y³=28 (given)
- `fact:s1` x=y+4 (established)
- `fact:s2` (y+4)³-y³=28 (established)
- `fact:s3` 12y²+48y+36=0 (established)
- `fact:s4` (y+1)(y+3)=0 (established)
- `fact:s5` candidate 1 (x,y)=(3,-1); candidate 2 (x,y)=(1,-3) (established)
- `fact:s6` both candidates yield xy=-3 (established)
**Goals:**
- `goal:answer` xy=-3 (goal_discharged)
**Dependencies:**
- fact:diff
- fact:cubes
- fact:candidate_1
- fact:candidate_2

**Goal status:** `discharged`

## Operations observed

`CASE_SPLIT`, `EVALUATE`, `EXPAND`, `FACTOR`, `SUBSTITUTE`

## HML gaps exposed

MATH-GAP-0001, MATH-GAP-0006, MATH-GAP-0007
