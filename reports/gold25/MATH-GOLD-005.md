# MATH-GOLD-005

## Original problem

Addison's age is three times Brenda's age. Janet is six years older than Brenda. Addison and Janet are twins. How old is Brenda?

## Original solution

First, let $A = $ Addison's age, $B = $ Brenda's age, and $J = $ Janet's age. Then, from the statements given, we have the following system of equations:  $$\begin{cases}
A=3B \\
J = B+6 \\
A=J
\end{cases} $$ Since $A=J$, we know that $3B=B+6$. Solving this equation, we have that $2B = 6 \Rightarrow B=3$. Thus, Brenda is $\boxed{3}$ years old.

## Canonical initial state

`S0` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Goals:**
- `goal:answer` B=3 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** First, let $A = $ Addison's age, $B = $ Brenda's age, and $J = $ Janet's age.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Goals:**
- `goal:answer` B=3 (goal_open)

**Arguments:** `{}`

**Warrant:** Name the quantities in the prose problem. (`variable_binding`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` A, B, J are named age variables

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: var. Typed declarations are native; the prose-to-symbol step is external.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
**Goals:**
- `goal:answer` B=3 (goal_open)

### Step 2: FORMULATE_EQUATION

**Source span:** Then, from the statements given, we have the following system of equations:

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
**Goals:**
- `goal:answer` B=3 (goal_open)

**Arguments:** `{}`

**Warrant:** Translate each verbal relation into an equation. (`problem_translation`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` A=3B, J=B+6, A=J

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: assume. HML can record the equations but has no prose relation extractor.

**Semantic gaps:** none

**State after:**

`S2` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1

### Step 3: SUBSTITUTE

**Source span:** Since $A=J$, we know that $3B=B+6$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Replace equal quantities in the first relation using A=J. (`equality_substitution`, source `core`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` 3B=B+6

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: substitute. The trusted substitute rule is structural and local.

**Semantic gaps:** none

**State after:**

`S3` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2

### Step 4: SOLVE

**Source span:** Solving this equation, we have that $2B = 6 \Rightarrow B=3$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2

**Arguments:** `{}`

**Warrant:** Subtract B and divide by the nonzero coefficient 2. (`equality_preservation`, source `derived`)

**Preconditions:**
- 2≠0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:s3

**Result:** `fact:s4` B=3

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: subtract_both_sides, divide_both_sides. Local transformations are native; the full solve trajectory is not.

**Semantic gaps:** none

**State after:**

`S4` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
- `fact:s4` B=3 (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3

### Step 5: DISCHARGE_GOAL

**Source span:** Thus, Brenda is $\boxed{3}$ years old.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
- `fact:s4` B=3 (established)
**Goals:**
- `goal:answer` B=3 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3

**Arguments:** `{}`

**Warrant:** The derived value matches the requested quantity. (`goal_matching`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s4

**Result:** `fact:s5` goal B=3 discharged

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: goal, proved. Goal discharge is native once a matching verified derivation exists.

**Semantic gaps:** none

**State after:**

`S5` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
- `fact:s4` B=3 (established)
- `fact:s5` goal B=3 discharged (established)
**Goals:**
- `goal:answer` B=3 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:s4

## Final state

`S5` scope: global
**Objects:**
- A
- B
- J
**Declarations:**
- A : Natural
- B : Natural
- J : Natural
**Types/domains:**
- ages are nonnegative integers
**Facts:**
- `fact:s1` A, B, J are named age variables (established)
- `fact:s2` A=3B, J=B+6, A=J (established)
- `fact:s3` 3B=B+6 (established)
- `fact:s4` B=3 (established)
- `fact:s5` goal B=3 discharged (established)
**Goals:**
- `goal:answer` B=3 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s3
- fact:s4

**Goal status:** `discharged`

## Operations observed

`DISCHARGE_GOAL`, `FORMULATE_EQUATION`, `INTRODUCE_VARIABLE`, `SOLVE`, `SUBSTITUTE`

## HML gaps exposed

None
