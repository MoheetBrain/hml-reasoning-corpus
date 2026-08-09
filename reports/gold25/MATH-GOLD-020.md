# MATH-GOLD-020

## Original problem

If $\|\mathbf{a}\| = 3$ and $\|\mathbf{b}\| = 6,$ then find $(\mathbf{a} + \mathbf{b}) \cdot (\mathbf{a} - \mathbf{b}).$

## Original solution

Expanding the dot product, we get
\begin{align*}
(\mathbf{a} + \mathbf{b}) \cdot (\mathbf{a} - \mathbf{b}) &= (\mathbf{a} + \mathbf{b}) \cdot \mathbf{a} - (\mathbf{a} + \mathbf{b}) \cdot \mathbf{b} \\
&= \mathbf{a} \cdot \mathbf{a} + \mathbf{b} \cdot \mathbf{a} - \mathbf{a} \cdot \mathbf{b} - \mathbf{b} \cdot \mathbf{b} \\
&= \mathbf{a} \cdot \mathbf{a} - \mathbf{b} \cdot \mathbf{b} \\
&= \|\mathbf{a}\|^2 - \|\mathbf{b}\|^2 \\
&= 3^2 - 6^2 = \boxed{-27}.
\end{align*}

## Canonical initial state

`S0` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)

## Trajectory

### Step 1: EXPAND

**Source span:** Expanding the dot product, we get

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply bilinearity of the dot product. (`bilinearity`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Vector bilinearity is not in the HML kernel.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)

### Step 2: CANCEL_SYMMETRIC_TERMS

**Source span:** = \mathbf{a} \cdot \mathbf{a} - \mathbf{b} \cdot \mathbf{b}

**Explicitness:** `implicit`

**State before:**

`S1` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)

**Arguments:** `{}`

**Warrant:** Use a·b=b·a to cancel the cross terms. (`dot_product_symmetry`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` cross terms cancel

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Vector symmetry/cancellation is library-level.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)
**Dependencies:**
- fact:s1

### Step 3: APPLY_DEFINITION

**Source span:** = \|\mathbf{a}\|^2 - \|\mathbf{b}\|^2

**Explicitness:** `implicit`

**State before:**

`S2` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Use a·a=||a||² and b·b=||b||². (`norm_definition`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` ||a||²-||b||²

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Vector norm definitions are not trusted core constructs.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S3` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
- `fact:s3` ||a||²-||b||² (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2

### Step 4: EVALUATE

**Source span:** = 3^2 - 6^2 = \boxed{-27}.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
- `fact:s3` ||a||²-||b||² (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2

**Arguments:** `{}`

**Warrant:** Substitute the given norms and evaluate. (`exact_arithmetic`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s3, fact:norm_a, fact:norm_b

**Result:** `fact:s4` (a+b)·(a-b)=-27

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. The closed scalar arithmetic is checkable after vector identities are supplied.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S4` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
- `fact:s3` ||a||²-||b||² (established)
- `fact:s4` (a+b)·(a-b)=-27 (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:norm_a
- fact:norm_b

## Final state

`S4` scope: global
**Objects:**
- vectors a,b
**Declarations:**
- a,b : Vector
**Types/domains:**
- ||a||=3, ||b||=6
**Facts:**
- `fact:norm_a` ||a||=3 (given)
- `fact:norm_b` ||b||=6 (given)
- `fact:s1` (a+b)·(a-b)=a·a+b·a-a·b-b·b (established)
- `fact:s2` cross terms cancel (established)
- `fact:s3` ||a||²-||b||² (established)
- `fact:s4` (a+b)·(a-b)=-27 (established)
**Goals:**
- `goal:answer` (a+b)·(a-b)=-27 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:norm_a
- fact:norm_b

**Goal status:** `discharged`

## Operations observed

`APPLY_DEFINITION`, `CANCEL_SYMMETRIC_TERMS`, `EVALUATE`, `EXPAND`

## HML gaps exposed

MATH-GAP-0007
