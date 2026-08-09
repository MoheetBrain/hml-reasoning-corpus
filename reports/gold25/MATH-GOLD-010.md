# MATH-GOLD-010

## Original problem

Tom has a red marble, a green marble, a blue marble, and three identical yellow marbles. How many different groups of two marbles can Tom choose?

## Original solution

There are two cases here: either Tom chooses two yellow marbles (1 result), or he chooses two marbles of different colors ($\binom{4}{2}=6$ results). The total number of distinct pairs of marbles Tom can choose is $1+6=\boxed{7}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)

## Trajectory

### Step 1: CASE_SPLIT

**Source span:** There are two cases here: either Tom chooses two yellow marbles (1 result), or he chooses two marbles of different colors

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)

**Arguments:** `{"branches": ["case Y/Y", "case colors"]}`

**Warrant:** Partition the outcomes by whether the indistinguishable yellow multiplicity is used twice. (`combinatorial_partition`, source `explicit`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` case Y/Y; case two distinct colors

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: scope. Scope exists, but HML has no combinatorial case partition or branch coverage rule.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0008

**State after:**

`S1` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)

### Step 2: COUNT_CASES

**Source span:** $\binom{4}{2}=6$ results

**Explicitness:** `explicit`

**State before:**

`S1` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)

**Arguments:** `{}`

**Warrant:** Choose two colors from the four available color classes. (`combination_count`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1

**Result:** `fact:s2` six distinct-color pairs

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. No combinatorial counting library is trusted by current HML.

**Semantic gaps:** MATH-GAP-0008

**State after:**

`S2` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
- `fact:s2` six distinct-color pairs (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)
**Dependencies:**
- fact:s1

### Step 3: COMBINE_CASE_COUNTS

**Source span:** The total number of distinct pairs of marbles Tom can choose is

**Explicitness:** `implicit`

**State before:**

`S2` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
- `fact:s2` six distinct-color pairs (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)
**Dependencies:**
- fact:s1

**Arguments:** `{}`

**Warrant:** Add counts of disjoint cases. (`disjoint_sum`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:s1, fact:s2

**Result:** `fact:s3` total=7

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `PARTIAL`; constructs: closed_eval_v1. The closed addition is checkable; the case semantics are not native.

**Semantic gaps:** MATH-GAP-0001, MATH-GAP-0008

**State after:**

`S3` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
- `fact:s2` six distinct-color pairs (established)
- `fact:s3` total=7 (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_open)
**Dependencies:**
- fact:s1
- fact:s2

## Final state

`S3` scope: global, branch:case Y/Y, branch:case colors
**Objects:**
- red marble
- green marble
- blue marble
- three identical yellow marbles
**Declarations:**
- multiset of 6 marbles
**Types/domains:**
- yellow marbles indistinguishable; other colors distinguishable
**Facts:**
- `fact:inventory` R,G,B,Y,Y,Y (given)
- `fact:s1` case Y/Y; case two distinct colors (established)
- `fact:s2` six distinct-color pairs (established)
- `fact:s3` total=7 (established)
**Goals:**
- `goal:answer` number of distinct 2-marble groups=7 (goal_discharged)
**Dependencies:**
- fact:s1
- fact:s2

**Goal status:** `discharged`

## Operations observed

`CASE_SPLIT`, `COMBINE_CASE_COUNTS`, `COUNT_CASES`

## HML gaps exposed

MATH-GAP-0001, MATH-GAP-0008
