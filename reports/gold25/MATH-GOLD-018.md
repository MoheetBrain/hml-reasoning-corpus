# MATH-GOLD-018

## Original problem

Compute $\tan 75^\circ.$

## Original solution

From the angle addition formula,
\begin{align*}
\tan 75^\circ &= \tan (45^\circ + 30^\circ) \\
&= \frac{\tan 45^\circ + \tan 30^\circ}{1 - \tan 45^\circ \tan 30^\circ} \\
&= \frac{1 + \frac{1}{\sqrt{3}}}{1 - \frac{1}{\sqrt{3}}} \\
&= \frac{\sqrt{3} + 1}{\sqrt{3} - 1} \\
&= \frac{(\sqrt{3} + 1)(\sqrt{3} + 1)}{(\sqrt{3} - 1)(\sqrt{3} + 1)} \\
&= \frac{3 + 2 \sqrt{3} + 1}{2} \\
&= \boxed{2 + \sqrt{3}}.
\end{align*}

## Canonical initial state

`S0` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)

## Trajectory

### Step 1: APPLY_THEOREM

**Source span:** From the angle addition formula,

**Explicitness:** `explicit`

**State before:**

`S0` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)

**Arguments:** `{}`

**Warrant:** Apply the tangent addition formula; denominator must be nonzero. (`tangent_addition`, source `library`)

**Preconditions:**
- 1-tan45°tan30°≠0 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. No trusted trigonometric identity library exists in current HML.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S1` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)

### Step 2: SUBSTITUTE

**Source span:** = \frac{1 + \frac{1}{\sqrt{3}}}{1 - \frac{1}{\sqrt{3}}}

**Explicitness:** `explicit`

**State before:**

`S1` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)

**Arguments:** `{}`

**Warrant:** Substitute exact special-angle values. (`special_value_substitution`, source `library`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** fact:special

**Result:** `fact:s2` tan75°=(1+1/√3)/(1-1/√3)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Exact radicals are representable, but the trig facts are library-level.

**Semantic gaps:** MATH-GAP-0007

**State after:**

`S2` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)
**Dependencies:**
- fact:special

### Step 3: RATIONALIZE

**Source span:** = \frac{\sqrt{3} + 1}{\sqrt{3} - 1}

**Explicitness:** `explicit`

**State before:**

`S2` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)
**Dependencies:**
- fact:special

**Arguments:** `{}`

**Warrant:** Multiply numerator and denominator by √3 to clear the fractional radicals, preserving the ratio because √3-1≠0. (`radical_normalization`, source `derived`)

**Preconditions:**
- √3-1≠0 — `implicit`; The worked solution does not state this condition explicitly.

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s3` tan75°=(√3+1)/(√3-1)

**Verification:** `verified` / `MANUAL_SEMANTIC_CHECK` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Symbolic radical rationalization is not a trusted kernel rule.

**Semantic gaps:** MATH-GAP-0003, MATH-GAP-0006

**State after:**

`S3` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
- `fact:s3` tan75°=(√3+1)/(√3-1) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)
**Dependencies:**
- fact:special

### Step 4: EVALUATE

**Source span:** = \frac{3 + 2 \sqrt{3} + 1}{2}

**Explicitness:** `explicit`

**State before:**

`S3` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
- `fact:s3` tan75°=(√3+1)/(√3-1) (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)
**Dependencies:**
- fact:special

**Arguments:** `{}`

**Warrant:** Expand and normalize the exact radical expression. (`exact_radical_arithmetic`, source `derived`)

**Preconditions:**
- none recorded

**Obligations created:**
- none

**Dependencies:** none

**Result:** `fact:s4` tan75°=2+√3

**Verification:** `verified` / `VERIFIED_EXACT` — The result follows from the recorded premises and the stated warrant.

**HML support:** `REPRESENTABLE_ONLY`; constructs: evidence. Closed exact arithmetic is partly available, but symbolic radical normalization is not.

**Semantic gaps:** MATH-GAP-0006

**State after:**

`S4` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
- `fact:s3` tan75°=(√3+1)/(√3-1) (established)
- `fact:s4` tan75°=2+√3 (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_open)
**Dependencies:**
- fact:special

## Final state

`S4` scope: global
**Objects:**
- angle 75°
**Declarations:**
- angle : Real
**Types/domains:**
- angles in degrees
**Facts:**
- `fact:angle_split` 75°=45°+30° (given)
- `fact:special` tan45°=1, tan30°=1/√3 (given)
- `fact:s1` tan(45°+30°)=(tan45°+tan30°)/(1-tan45°tan30°) (established)
- `fact:s2` tan75°=(1+1/√3)/(1-1/√3) (established)
- `fact:s3` tan75°=(√3+1)/(√3-1) (established)
- `fact:s4` tan75°=2+√3 (established)
**Goals:**
- `goal:answer` tan75°=2+√3 (goal_discharged)
**Dependencies:**
- fact:special

**Goal status:** `discharged`

## Operations observed

`APPLY_THEOREM`, `EVALUATE`, `RATIONALIZE`, `SUBSTITUTE`

## HML gaps exposed

MATH-GAP-0003, MATH-GAP-0006, MATH-GAP-0007
