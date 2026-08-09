# MATH-GOLD-008

## Original problem

If $f(x)$ is an even function and $g(x)$ is an odd function, find if $f(g(x^3))$ is even, odd, or neither.

Enter "odd", "even", or "neither".

## Original solution

Substituting $-x$ for $x$ gives us $f(g(-x^3)) = f(-g(x^3)) = f(g(x^3))$ so $f(g(x^3))$ is $\boxed{\text{even}}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_open)

## Trajectory

### Step 1: APPLY_DEFINITION

**Source span:** Substituting $-x$ for $x$ gives us $f(g(-x^3)) = f(-g(x^3)) = f(g(x^3))$

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_open)

**Arguments:** `{}`

**Warrant:** Apply oddness of g and evenness of f to the transformed input. (`parity_definition`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:parity_f, fact:parity_g

**Result:** `fact:s1` h(-x)=h(x) for h(x)=f(g(x³))

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. HML can state the parity claims but has no registered function-parity theorem.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
- `fact:s1` h(-x)=h(x) for h(x)=f(g(x³)) (established)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_open)
**Dependencies:**
- fact:parity_f
- fact:parity_g

### Step 2: DISCHARGE_GOAL

**Source span:** so $f(g(x^3))$ is $\boxed{\text{even}}$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
- `fact:s1` h(-x)=h(x) for h(x)=f(g(x³)) (established)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_open)
**Dependencies:**
- fact:parity_f
- fact:parity_g

**Arguments:** `{}`

**Warrant:** The transformed expression equals the original under x↦-x. (`definition_matching`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:parity_f, fact:parity_g

**Result:** `fact:s2` goal parity even discharged

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: goal, evidence. Goal syntax exists; the functional extensionality/parity proof is library-level.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
- `fact:s1` h(-x)=h(x) for h(x)=f(g(x³)) (established)
- `fact:s2` goal parity even discharged (established)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_open)
**Dependencies:**
- fact:parity_f
- fact:parity_g

## Final state

`S2` scope: global
**Objects:**
- f
- g
- x
**Declarations:**
- f : Function
- g : Function
- x : Real
**Types/domains:**
- f even: f(-u)=f(u)
- g odd: g(-u)=-g(u)
**Facts:**
- `fact:parity_f` f is even (given)
- `fact:parity_g` g is odd (given)
- `fact:s1` h(-x)=h(x) for h(x)=f(g(x³)) (established)
- `fact:s2` goal parity even discharged (established)
**Goals:**
- `goal:answer` f(g(x³)) is even (goal_discharged)
**Dependencies:**
- fact:parity_f
- fact:parity_g

**Goal status:** `discharged`

## Operations observed

`APPLY_DEFINITION`, `DISCHARGE_GOAL`

## HML gaps exposed

MATH-GAP-0007
