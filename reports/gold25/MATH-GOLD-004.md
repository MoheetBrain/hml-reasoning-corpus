# MATH-GOLD-004

## Original problem

Find the largest value of $x$ that satisfies the equation $|5x-1|=x+3$.

## Original solution

We can split the expression $|5x-1|=x+3$ into two separate cases. In the first case, \begin{align*} 5x-1&=x+3
\\\Rightarrow \qquad 4x&=4
\\\Rightarrow \qquad x&=1
\end{align*}If we plug this value of $x$ back into the original equation in order to check our answer, we see that $|5(1)-1|=1+3$ or $4=4$. Since this is true, we can accept $x=1$ as a valid solution.

In the second case, \begin{align*} 5x-1&=-(x+3)
\\ 5x-1&=-x-3
\\\Rightarrow \qquad 6x&=-2
\\\Rightarrow \qquad x&=-\frac13.
\end{align*}If we plug $-\frac13$ back into the initial equation, we get that $\left|5\left(-\frac13\right)-1\right|=-\frac13+3$, which simplifies to $\left|-\frac{8}{3}\right|=\frac{8}{3}$, or $\frac{8}{3}=\frac{8}{3}$. Since this is also a true statement, we can accept $x=-\frac13$ as a valid solution as well. Since both $x=1$ and $x=-\frac13$ are possible values of $x$, the final answer is the larger of the two: $x=\boxed{1}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)

## Trajectory

### Step 1: CASE_SPLIT

**Source span:** We can split the expression $|5x-1|=x+3$ into two separate cases.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)

**Arguments:** `{"branches": ["case 1", "case 2"]}`

**Warrant:** Apply the two-branch definition of absolute value. (`absolute_value_definition`, source `core`)

**Preconditions:**
- x+3≥0 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint — `discharged`

**Dependencies:** none

**Result:** `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: scope. Lexical scope exists, but no case-split rule proves branch exhaustiveness or manages branch joins.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0002, MATH-GAP-0004

**State after:**

`S1` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)

### Step 2: SOLVE_CASE

**Source span:** 5x-1&=x+3

**Explicitness:** `implicit`

**State before:**

`S1` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)

**Arguments:** `{"branch": "x≥1/5"}`

**Warrant:** Solve the branch equation under the branch condition 5x-1≥0. (`equality_preservation`, source `derived`)

**Preconditions:**
- 5x-1≥0 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` case 1 yields x=1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: subtract_both_sides, divide_both_sides. Local algebra is available, but branch-scoped derivation is not a single current rule.

**Semantic gaps:** MATH-GAP-0001

**State after:**

`S2` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1

### Step 3: VERIFY_CANDIDATE

**Source span:** If we plug this value of $x$ back into the original equation in order to check our answer, we see that $|5(1)-1|=1+3$ or $4=4$.

**Explicitness:** `explicit`

**State before:**

`S2` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Re-evaluate the original equation at the generated candidate. (`substitution_check`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s2

**Result:** `fact:s3` candidate x=1 satisfies the original equation

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed candidate checks can be certified, but candidate-generation/branch linkage is not kernel-native.

**Semantic gaps:** MATH-GAP-0002

**State after:**

`S3` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2

### Step 4: SOLVE_CASE

**Source span:** 5x-1&=-(x+3)

**Explicitness:** `implicit`

**State before:**

`S3` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2

**Arguments:** `{"branch": "x<1/5"}`

**Warrant:** Solve the second branch equation under the branch condition 5x-1<0. (`equality_preservation`, source `derived`)

**Preconditions:**
- 5x-1<0 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s4` case 2 yields x=-1/3

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: add_both_sides, divide_both_sides. Local algebra is available; branch proof remains partial.

**Semantic gaps:** MATH-GAP-0001

**State after:**

`S4` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2

### Step 5: VERIFY_CANDIDATE

**Source span:** If we plug $-\frac13$ back into the initial equation, we get that

**Explicitness:** `explicit`

**State before:**

`S4` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2

**Arguments:** `{}`

**Warrant:** Re-evaluate the original equation at the second generated candidate. (`substitution_check`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s4

**Result:** `fact:s5` candidate x=-1/3 satisfies the original equation

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. Closed candidate checks can be certified; branch bookkeeping is external.

**Semantic gaps:** MATH-GAP-0002

**State after:**

`S5` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
- `fact:s5` candidate x=-1/3 satisfies the original equation (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s4

### Step 6: SELECT_EXTREMUM

**Source span:** the final answer is the larger of the two

**Explicitness:** `explicit`

**State before:**

`S5` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
- `fact:s5` candidate x=-1/3 satisfies the original equation (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s4

**Arguments:** `{}`

**Warrant:** Compare the verified finite candidate set. (`finite_order`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s3, fact:s5

**Result:** `fact:s6` largest valid solution is x=1

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: goal. HML has goals but no finite-candidate selection rule.

**Semantic gaps:** MATH-GAP-0002

**State after:**

`S6` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
- `fact:s5` candidate x=-1/3 satisfies the original equation (established)
- `fact:s6` largest valid solution is x=1 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_open)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s4
- fact:s3
- fact:s5

## Final state

`S6` scope: global, branch:case 1, branch:case 2
**Objects:**
- x
**Declarations:**
- x : Real
**Types/domains:**
- x ∈ Real
**Facts:**
- `fact:abs` |5x-1|=x+3 (given)
- `fact:s1` case 1: 5x-1=x+3; case 2: 5x-1=-(x+3) (established)
- `fact:s2` case 1 yields x=1 (established)
- `fact:s3` candidate x=1 satisfies the original equation (established)
- `fact:s4` case 2 yields x=-1/3 (established)
- `fact:s5` candidate x=-1/3 satisfies the original equation (established)
- `fact:s6` largest valid solution is x=1 (established)
**Goals:**
- `goal:answer` largest solution x=1 (goal_discharged)
**Discharged obligations:**
- `obl:abs_case_cover` the absolute-value branches are exhaustive and disjoint (discharged)
**Dependencies:**
- fact:s1
- fact:s2
- fact:s4
- fact:s3
- fact:s5

**Goal status:** `discharged`

## Operations observed

`CASE_SPLIT`, `SELECT_EXTREMUM`, `SOLVE_CASE`, `VERIFY_CANDIDATE`

## HML gaps exposed

MATH-GAP-0001, MATH-GAP-0002, MATH-GAP-0004
