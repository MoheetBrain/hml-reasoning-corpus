# MATH-GOLD-016

## Original problem

What is the 200th term of the increasing sequence of positive integers formed by omitting only the perfect squares?

## Original solution

When 200 is reached in the sequence of non-square positive integers, all the perfect squares from $1^2$ up to $14^2$ have been omitted.  Therefore, 200 is the 186th term.  The 187th term is 201, the 188th term is 202, $\ldots$, the 200th term is $\boxed{214}$.

## Canonical initial state

`S0` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
**Goals:**
- `goal:answer` a_200=214 (goal_open)

## Trajectory

### Step 1: COUNT_EXCLUDED

**Source span:** When 200 is reached in the sequence of non-square positive integers, all the perfect squares from $1^2$ up to $14^2$ have been omitted.

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
**Goals:**
- `goal:answer` a_200=214 (goal_open)

**Arguments:** `{}`

**Warrant:** Count the perfect squares below 200 using 1² through 14². (`counting_exclusions`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:index

**Result:** `fact:s1` 14 squares are omitted before the target value

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Sequence indexing with excluded values is not a core rule.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S1` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
**Goals:**
- `goal:answer` a_200=214 (goal_open)
**Dependencies:**
- fact:index

### Step 2: INDEX_TRANSLATION

**Source span:** Therefore, 200 is the 186th term.

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
**Goals:**
- `goal:answer` a_200=214 (goal_open)
**Dependencies:**
- fact:index

**Arguments:** `{}`

**Warrant:** Subtract the 14 omitted values from the ambient integer index. (`index_shift`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:index

**Result:** `fact:s2` value 200 has sequence index 186

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Index translation is not executable in current HML.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S2` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
- `fact:s2` value 200 has sequence index 186 (established)
**Goals:**
- `goal:answer` a_200=214 (goal_open)
**Dependencies:**
- fact:index

### Step 3: ADVANCE_SEQUENCE

**Source span:** The 187th term is 201

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
- `fact:s2` value 200 has sequence index 186 (established)
**Goals:**
- `goal:answer` a_200=214 (goal_open)
**Dependencies:**
- fact:index

**Arguments:** `{}`

**Warrant:** Advance 14 positions after 200; none of 201–214 is a square. (`successor_iteration`, source `derived`)

**Preconditions:**
- 201,…,214 are nonsquares — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** fact:index

**Result:** `fact:s3` a_200=214

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Finite sequence iteration is not a trusted HML operation.

**Semantic gaps:** MATH-GAP-0010

**State after:**

`S3` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
- `fact:s2` value 200 has sequence index 186 (established)
- `fact:s3` a_200=214 (established)
**Goals:**
- `goal:answer` a_200=214 (goal_open)
**Dependencies:**
- fact:index

## Final state

`S3` scope: global
**Objects:**
- sequence of positive integers excluding squares
**Declarations:**
- a_k : Natural
**Types/domains:**
- a_k is increasing; perfect squares omitted
**Facts:**
- `fact:index` target index k=200 (given)
- `fact:s1` 14 squares are omitted before the target value (established)
- `fact:s2` value 200 has sequence index 186 (established)
- `fact:s3` a_200=214 (established)
**Goals:**
- `goal:answer` a_200=214 (goal_discharged)
**Dependencies:**
- fact:index

**Goal status:** `discharged`

## Operations observed

`ADVANCE_SEQUENCE`, `COUNT_EXCLUDED`, `INDEX_TRANSLATION`

## HML gaps exposed

MATH-GAP-0010
