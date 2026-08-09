# MATH-GOLD-015

## Original problem

What is the smallest positive integer that leaves a remainder of 4 when divided by 5 and a remainder of 6 when divided by 7?

## Original solution

Let the desired number be $a$. Then \begin{align*}
a\equiv 4\pmod 5,\\
a\equiv 6\pmod 7.
\end{align*} The first congruence means that there exists a non-negative integer $n$ such that $a=4+5n$. Substituting this into the second congruence yields \[4+5n\equiv 6\pmod 7\implies n\equiv 6\pmod 7\] So $n$ has a lower bound of $6$. Then $n\ge 6\implies a=4+5n\ge 34$. $\boxed{34}$ is the smallest solution since it is a lower bound of $a$ and satisfies both original congruences.

## Canonical initial state

`S0` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)

## Trajectory

### Step 1: INTRODUCE_VARIABLE

**Source span:** Let the desired number be $a$.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)

**Arguments:** `{}`

**Warrant:** Name the unknown integer. (`variable_binding`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` a names the desired positive integer

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `FULL`; constructs: var. Typed declaration is native.

**Semantic gaps:** none

**State after:**

`S1` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)

### Step 2: PARAMETERIZE_CONGRUENCE

**Source span:** The first congruence means that there exists a non-negative integer $n$ such that $a=4+5n$.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)

**Arguments:** `{}`

**Warrant:** Unpack a≡4 (mod 5) into an integer parameterization. (`congruence_definition`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:congruence_5

**Result:** `fact:s2` a=4+5n for n≥0

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Congruence parameterization is not a core rule.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S2` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5

### Step 3: SUBSTITUTE

**Source span:** Substituting this into the second congruence yields \[4+5n\equiv 6\pmod 7\implies n\equiv 6\pmod 7\]

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5

**Arguments:** `{}`

**Warrant:** Substitute the parameterization and reduce modulo 7. (`modular_substitution`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:congruence_5, fact:congruence_7

**Result:** `fact:s3` n≡6 mod 7

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. No trusted modular arithmetic rule.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S3` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

### Step 4: BOUND_SEARCH

**Source span:** So $n$ has a lower bound of $6$.

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

**Arguments:** `{}`

**Warrant:** Use n≥0 and n≡6 mod 7 to identify the least admissible n. (`least_residue`, source `derived`)

**Preconditions:**
- n≥0 — `satisfied`; Given or established in the current state.

**Obligations created:**
- none

**Dependencies:** fact:congruence_7

**Result:** `fact:s4` n≥6

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Minimality over congruence classes is not native.

**Semantic gaps:** MATH-GAP-0009

**State after:**

`S4` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

### Step 5: EVALUATE

**Source span:** Then $n\ge 6\implies a=4+5n\ge 34$.

**Explicitness:** `explicit`

**State before:**

`S4` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

**Arguments:** `{}`

**Warrant:** The affine expression increases with n. (`monotonicity`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:congruence_5

**Result:** `fact:s5` a≥34

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Symbolic monotonicity is not a core rule.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S5` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
- `fact:s5` a≥34 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

### Step 6: VERIFY_CANDIDATE

**Source span:** $\boxed{34}$ is the smallest solution since it is a lower bound of $a$ and satisfies both original congruences.

**Explicitness:** `explicit`

**State before:**

`S5` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
- `fact:s5` a≥34 (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

**Arguments:** `{}`

**Warrant:** Check the lower-bound candidate against both original modular constraints. (`candidate_verification`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:congruence_5, fact:congruence_7

**Result:** `fact:s6` a=34 is minimal and satisfies both congruences

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Candidate verification over congruences is not a trusted checker.

**Semantic gaps:** MATH-GAP-0002, MATH-GAP-0009

**State after:**

`S6` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
- `fact:s5` a≥34 (established)
- `fact:s6` a=34 is minimal and satisfies both congruences (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_open)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

## Final state

`S6` scope: global
**Objects:**
- a
- n
**Declarations:**
- a : Natural
- n : Natural
**Types/domains:**
- a>0, n≥0
**Facts:**
- `fact:congruence_5` a≡4 mod 5 (given)
- `fact:congruence_7` a≡6 mod 7 (given)
- `fact:s1` a names the desired positive integer (established)
- `fact:s2` a=4+5n for n≥0 (established)
- `fact:s3` n≡6 mod 7 (established)
- `fact:s4` n≥6 (established)
- `fact:s5` a≥34 (established)
- `fact:s6` a=34 is minimal and satisfies both congruences (established)
**Goals:**
- `goal:answer` smallest a=34 (goal_discharged)
**Dependencies:**
- fact:congruence_5
- fact:congruence_7

**Goal status:** `discharged`

## Operations observed

`BOUND_SEARCH`, `EVALUATE`, `INTRODUCE_VARIABLE`, `PARAMETERIZE_CONGRUENCE`, `SUBSTITUTE`, `VERIFY_CANDIDATE`

## HML gaps exposed

MATH-GAP-0002, MATH-GAP-0006, MATH-GAP-0009
