# Hard-negative audit

The two largest source transitions in each semantic family were selected
deterministically and re-audited from their exact source payload and verifier finding.

## Independent-review result

Mechanical acceptance did not imply mathematical hardness. The review corrected
the initial all-hard interpretation to 20 semantic-hard, 60 structural and 20
ambiguous pairs. No parser failures were found. Dependency/warrant/epistemic probes
use obvious missing identities; precondition and effect probes directly contradict
status/materialisation fields; scope and type also raise FRAME. The branch and
candidate probes isolate certificate coverage, but their imported trusted evidence
does not independently re-prove the opaque MATH text. Therefore this is a harness
checkpoint, not production-ready mathematical counterfactual data.

## 1. CF-SF-FINAL-BRN-001-B — BRANCH_JOIN

- Source: `train-row-03488` — Let $f$ be a function taking the nonnegative integers to the nonnegative integers, such that \[2f(a^2 + b^2) = [f(a)]^2 + [f(b)]^2\]for all nonnegative integers $a$ and $b.$ Let $n$ be the number of possible values of $f(25),$ and let $s$ b
- Exact changed field: `$.evidence.e_coverage.branch_ids[1]`
- Change: `"b2"` → `null`
- Verifier: `INVALID_BRANCH_JOIN` / `BRANCH_JOIN`
- Grounded explanation: the partition certificate does not cover branch(es) b2
- Causal audit: The partition certificate no longer covers one joined branch; agreement among the remaining branches does not establish exhaustiveness. The changed certificate content is well formed and the target invariant, rather than parsing or frame drift, explains rejection.
- Revised class: `SEMANTIC_HARD_PAIR`

## 2. CF-SF-FINAL-BRN-008-B — BRANCH_JOIN

- Source: `train-row-01964` — Each of five, standard, six-sided dice is rolled once. What is the probability that there is at least one pair but not a three-of-a-kind (that is, there are two dice showing the same value, but no three dice show the same value)?
- Exact changed field: `$.evidence.e_coverage.branch_ids[1]`
- Change: `"b2"` → `null`
- Verifier: `INVALID_BRANCH_JOIN` / `BRANCH_JOIN`
- Grounded explanation: the partition certificate does not cover branch(es) b2
- Causal audit: The partition certificate no longer covers one joined branch; agreement among the remaining branches does not establish exhaustiveness. The changed certificate content is well formed and the target invariant, rather than parsing or frame drift, explains rejection.
- Revised class: `SEMANTIC_HARD_PAIR`

## 3. CF-SF-FINAL-CAN-003-A — CANDIDATES

- Source: `train-row-03410` — There are $24$ different complex numbers $z$ such that $z^{24}=1$. For how many of these is $z^6$ a real number?
- Exact changed field: `$.evidence.e_candidate.checked_constraints[0]`
- Change: `"p0"` → `null`
- Verifier: `CANDIDATE_PROMOTION` / `CANDIDATES`
- Grounded explanation: promotion evidence does not check original constraint(s) p0
- Causal audit: Promotion evidence checks a strict subset of the candidate's original constraints, so it certifies a different candidate claim. The changed certificate content is well formed and the target invariant, rather than parsing or frame drift, explains rejection.
- Revised class: `SEMANTIC_HARD_PAIR`

## 4. CF-SF-FINAL-CAN-004-A — CANDIDATES

- Source: `train-row-03412` — Let $S$ be the set of all nonzero real numbers. Let $f : S \to S$ be a function such that \[f(x) + f(y) = f(xyf(x + y))\]for all $x,$ $y \in S$ such that $x + y \neq 0.$ Let $n$ be the number of possible values of $f(4),$ and let $s$ be the
- Exact changed field: `$.evidence.e_candidate.checked_constraints[0]`
- Change: `"p0"` → `null`
- Verifier: `CANDIDATE_PROMOTION` / `CANDIDATES`
- Grounded explanation: promotion evidence does not check original constraint(s) p0
- Causal audit: Promotion evidence checks a strict subset of the candidate's original constraints, so it certifies a different candidate claim. The changed certificate content is well formed and the target invariant, rather than parsing or frame drift, explains rejection.
- Revised class: `SEMANTIC_HARD_PAIR`

## 5. CF-SF-DEV-DEP-002-B — DEPENDENCY

- Source: `train-row-03944` — Define $L(x) = x - \frac{x^2}{2}$ for every real number $x$. If $n$ is a positive integer, define $a_n$ by \[ a_n = L \Bigl( L \Bigl( L \Bigl( \cdots L \Bigl( \frac{17}{n} \Bigr) \cdots \Bigr) \Bigr) \Bigr), \]where there are $n$ iterations
- Exact changed field: `$.action.dependencies[0]`
- Change: `"p0"` → `"__cf_missing_dependency__"`
- Verifier: `DEPENDENCY_VIOLATION` / `DEPENDENCY`
- Grounded explanation: action cites '__cf_missing_dependency__', which is not present in the prior state
- Causal audit: The action now cites one unavailable premise; no mathematical conclusion may acquire ancestry from a fact absent from state_before. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 6. CF-SF-FINAL-DEP-004-B — DEPENDENCY

- Source: `train-row-04689` — If $n$ is a positive integer, then let $f(n)$ be the sum of the digits of $\frac{1}{5^{{}^n}}$ that are to the right of the decimal point. What is the smallest positive integer $n$ such that $f(n) > 10$?
- Exact changed field: `$.action.dependencies[0]`
- Change: `"p0"` → `"__cf_missing_dependency__"`
- Verifier: `DEPENDENCY_VIOLATION` / `DEPENDENCY`
- Grounded explanation: action cites '__cf_missing_dependency__', which is not present in the prior state
- Causal audit: The action now cites one unavailable premise; no mathematical conclusion may acquire ancestry from a fact absent from state_before. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 7. CF-SF-DEV-EPI-002-A — EPISTEMIC_STATUS

- Source: `train-row-02416` — A bag contains 3 tan, 2 pink and 4 violet chips. If the 9 chips are randomly drawn from the bag, one at a time and without replacement, what is the probability that the chips are drawn in such a way that the 3 tan chips are drawn consecutiv
- Exact changed field: `$.action.epistemic_effect.evidence_id`
- Change: `"e_verify"` → `"__cf_missing_evidence__"`
- Verifier: `EPISTEMIC_PROMOTION` / `EPISTEMIC_STATUS`
- Grounded explanation: status was raised to VERIFIED with no existing supporting evidence
- Causal audit: The action still requests the same epistemic promotion but no longer points to existing evidence that can license that status increase. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 8. CF-SF-FINAL-EPI-002-B — EPISTEMIC_STATUS

- Source: `train-row-03423` — Let $S$ be the set of all nonzero real numbers. The function $f : S \to S$ satisfies the following two properties: (i) First, \[f \left( \frac{1}{x} \right) = xf(x)\]for all $x \in S.$ (ii) Second, \[f \left( \frac{1}{x} \right) + f \left(
- Exact changed field: `$.action.epistemic_effect.evidence_id`
- Change: `"e_verify"` → `"__cf_missing_evidence__"`
- Verifier: `EPISTEMIC_PROMOTION` / `EPISTEMIC_STATUS`
- Grounded explanation: status was raised to VERIFIED with no existing supporting evidence
- Causal audit: The action still requests the same epistemic promotion but no longer points to existing evidence that can license that status increase. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 9. CF-SF-DEV-GOL-001-B — GOAL_DISCHARGE

- Source: `train-row-04498` — The vertices $V$ of a centrally symmetric hexagon in the complex plane are given by \[V=\left\{ \sqrt{2}i,-\sqrt{2}i, \frac{1}{\sqrt{8}}(1+i),\frac{1}{\sqrt{8}}(-1+i),\frac{1}{\sqrt{8}}(1-i),\frac{1}{\sqrt{8}}(-1-i) \right\}.\]For each $j$,
- Exact changed field: `$.state_after.goals.g1.status`
- Change: `"DISCHARGED"` → `"OPEN"`
- Verifier: `FALSE_GOAL_DISCHARGE` / `GOAL_DISCHARGE`
- Grounded explanation: the action discharges goal 'g1', but it is OPEN in the resulting state; a declared discharge must be performed
- Causal audit: The action declares exact-goal discharge while the resulting state leaves the same goal open; a declared effect must materialise. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 10. CF-SF-DEV-GOL-002-B — GOAL_DISCHARGE

- Source: `train-row-05189` — The letters of the alphabet are given numeric values based on the two conditions below. $\bullet$ Only the numeric values of $-2,$ $-1,$ $0,$ $1$ and $2$ are used. $\bullet$ Starting with A and going through Z, a numeric value is assigned t
- Exact changed field: `$.state_after.goals.g1.status`
- Change: `"DISCHARGED"` → `"OPEN"`
- Verifier: `FALSE_GOAL_DISCHARGE` / `GOAL_DISCHARGE`
- Grounded explanation: the action discharges goal 'g1', but it is OPEN in the resulting state; a declared discharge must be performed
- Causal audit: The action declares exact-goal discharge while the resulting state leaves the same goal open; a declared effect must materialise. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 11. CF-SF-DEV-OBL-002-A — OBLIGATIONS

- Source: `train-row-03071` — In acute triangle $ABC$ points $P$ and $Q$ are the feet of the perpendiculars from $C$ to $\overline{AB}$ and from $B$ to $\overline{AC}$, respectively. Line $PQ$ intersects the circumcircle of $\triangle ABC$ in two distinct points, $X$ an
- Exact changed field: `$.action.obligations_created[0].id`
- Change: `"o1"` → `"__cf_missing_obligation__"`
- Verifier: `OBLIGATION_DROP` / `OBLIGATIONS`
- Grounded explanation: obligation '__cf_missing_obligation__' was created by the action but is absent from the resulting state
- Causal audit: The action declares creation of an obligation that is absent from the resulting state, so proof debt is silently dropped. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 12. CF-SF-FINAL-OBL-001-A — OBLIGATIONS

- Source: `train-row-03535` — Let $A,$ $B,$ and $C$ be constants such that the equation \[\frac{(x+B)(Ax+28)}{(x+C)(x+7)} = 2\]has infinitely many solutions for $x.$ For these values of $A,$ $B,$ and $C,$ it turns out that there are only finitely many values of $x$ whic
- Exact changed field: `$.action.obligations_created[0].id`
- Change: `"o1"` → `"__cf_missing_obligation__"`
- Verifier: `OBLIGATION_DROP` / `OBLIGATIONS`
- Grounded explanation: obligation '__cf_missing_obligation__' was created by the action but is absent from the resulting state
- Causal audit: The action declares creation of an obligation that is absent from the resulting state, so proof debt is silently dropped. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 13. CF-SF-FINAL-PRE-001-B — PRECONDITIONS

- Source: `train-row-03397` — Find all real values of $x$ that satisfy $\frac{x^2+x^3-2x^4}{x+x^2-2x^3} \ge -1.$ (Give your answer in interval notation.)
- Exact changed field: `$.action.preconditions[0].status`
- Change: `"SATISFIED"` → `"FAILED"`
- Verifier: `PRECONDITION_VIOLATION` / `PRECONDITIONS`
- Grounded explanation: precondition[0] 'pre0' is 'FAILED'
- Causal audit: One required precondition changes from satisfied to failed; parsing and all other action/state fields remain identical. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 14. CF-SF-FINAL-PRE-004-A — PRECONDITIONS

- Source: `train-row-03406` — An ellipse with equation \[\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1\]contains the circles $(x - 1)^2 + y^2 = 1$ and $(x + 1)^2 +y^2 = 1.$ Then the smallest possible area of the ellipse can be expressed in the form $k \pi.$ Find $k.$
- Exact changed field: `$.action.preconditions[0].status`
- Change: `"SATISFIED"` → `"FAILED"`
- Verifier: `PRECONDITION_VIOLATION` / `PRECONDITIONS`
- Grounded explanation: precondition[0] 'pre0' is 'FAILED'
- Causal audit: One required precondition changes from satisfied to failed; parsing and all other action/state fields remain identical. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 15. CF-SF-DEV-SCP-002-B — SCOPE

- Source: `train-row-04566` — Complex numbers $a,$ $b,$ and $c$ are zeros of a polynomial $P(z) = z^3 + qz + r,$ and $|a|^2 + |b|^2 + |c|^2 = 250.$ The points corresponding to $a,$ $b,$ and $c$ in the complex plane are the vertices of a right triangle with hypotenuse $h
- Exact changed field: `$.state_before.claims.p0.scope`
- Change: `"branch:b1"` → `"branch:cf_inactive"`
- Verifier: `SCOPE_LEAK` / `SCOPE`
- Grounded explanation: 'p0' lives in inactive scope 'branch:cf_inactive' and cannot be cited
- Causal audit: A cited premise is moved to an inactive branch scope while the action is held fixed, so branch-local knowledge is unavailable at the transition. The intended invariant fires, but the one-sided prior-state mutation also causes a frame finding; causal isolation is therefore incomplete.
- Revised class: `AMBIGUOUS`

## 16. CF-SF-FINAL-SCP-005-B — SCOPE

- Source: `train-row-01765` — An o-Pod MP3 player stores and plays entire songs. Celeste has 10 songs stored on her o-Pod. The time length of each song is different. When the songs are ordered by length, the shortest song is only 30 seconds long and each subsequent song
- Exact changed field: `$.state_before.claims.p0.scope`
- Change: `"branch:b1"` → `"branch:cf_inactive"`
- Verifier: `SCOPE_LEAK` / `SCOPE`
- Grounded explanation: 'p0' lives in inactive scope 'branch:cf_inactive' and cannot be cited
- Causal audit: A cited premise is moved to an inactive branch scope while the action is held fixed, so branch-local knowledge is unavailable at the transition. The intended invariant fires, but the one-sided prior-state mutation also causes a frame finding; causal isolation is therefore incomplete.
- Revised class: `AMBIGUOUS`

## 17. CF-SF-FINAL-TYP-002-B — TYPE_DOMAIN

- Source: `train-row-03422` — Let $p(x)$ be a monic polynomial of degree 4, such that $p(1) = 17,$ $p(2) = 34,$ and $p(3) = 51.$ Find $p(0) + p(4).$
- Exact changed field: `$.state_before.claims.p0.domain`
- Change: `"Integer"` → `"Proposition"`
- Verifier: `TYPE_OR_DOMAIN_MISMATCH` / `TYPE_DOMAIN`
- Grounded explanation: 'p0' is 'Proposition' in the state, which does not inhabit the 'Integer' the action requires
- Causal audit: One cited claim is moved to a domain that does not inhabit the action's declared input domain; the proposition text and action are unchanged. The intended invariant fires, but the one-sided prior-state mutation also causes a frame finding; causal isolation is therefore incomplete.
- Revised class: `AMBIGUOUS`

## 18. CF-SF-FINAL-TYP-003-B — TYPE_DOMAIN

- Source: `train-row-03426` — Compute \[\lfloor 1 \rfloor + \lfloor 1.6 \rfloor + \lfloor 2.2 \rfloor + \lfloor 2.8 \rfloor + \dots + \lfloor 99.4 \rfloor + \lfloor 100 \rfloor,\]where the arguments of the floor functions are in arithmetic progression.
- Exact changed field: `$.state_before.claims.p0.domain`
- Change: `"Integer"` → `"Proposition"`
- Verifier: `TYPE_OR_DOMAIN_MISMATCH` / `TYPE_DOMAIN`
- Grounded explanation: 'p0' is 'Proposition' in the state, which does not inhabit the 'Integer' the action requires
- Causal audit: One cited claim is moved to a domain that does not inhabit the action's declared input domain; the proposition text and action are unchanged. The intended invariant fires, but the one-sided prior-state mutation also causes a frame finding; causal isolation is therefore incomplete.
- Revised class: `AMBIGUOUS`

## 19. CF-SF-DEV-WAR-001-B — WARRANT

- Source: `train-row-08913` — For each integer $n$, let $f(n)$ be the sum of the elements of the $n$th row (i.e. the row with $n+1$ elements) of Pascal's triangle minus the sum of all the elements from previous rows. For example, \[f(2) = \underbrace{(1 + 2 + 1)}_{\text
- Exact changed field: `$.action.warrant.evidence_id`
- Change: `"e_source"` → `"__cf_missing_evidence__"`
- Verifier: `WARRANT_MISMATCH` / `WARRANT`
- Grounded explanation: warrant cites evidence '__cf_missing_evidence__', which does not exist
- Causal audit: The mathematical claim and rule are unchanged, but the action now cites an evidence identity that does not exist in the transition envelope. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`

## 20. CF-SF-DEV-WAR-002-B — WARRANT

- Source: `train-row-03299` — The sides of triangle $CAB$ are in the ratio of $2:3:4$. Segment $BD$ is the angle bisector drawn to the shortest side, dividing it into segments $AD$ and $DC$. What is the length, in inches, of the longer subsegment of side $AC$ if the len
- Exact changed field: `$.action.warrant.evidence_id`
- Change: `"e_source"` → `"__cf_missing_evidence__"`
- Verifier: `WARRANT_MISMATCH` / `WARRANT`
- Grounded explanation: warrant cites evidence '__cf_missing_evidence__', which does not exist
- Causal audit: The mathematical claim and rule are unchanged, but the action now cites an evidence identity that does not exist in the transition envelope. This is a useful verifier-harness probe, but its missing identity or direct status/effect inconsistency is too easy to count as a hard mathematical negative.
- Revised class: `STRUCTURAL_PAIR`
