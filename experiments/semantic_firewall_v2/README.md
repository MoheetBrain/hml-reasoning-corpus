# Semantic Firewall — second-generation suite (FX2)

**Additive. The frozen thirty in `../semantic_firewall/acceptance/fixtures.json` are not
modified, renumbered or restated.** FX2 ids are prefixed `FX2-`, so no id can collide.

## Read this before citing a green FX2 run

FX2 is **weaker evidence than the frozen thirty and must never be presented as equivalent.**

The original fixtures were authored on the corpus side, against a reference checker, *before*
the implementation existed. They are external criteria. FX2 was authored by the integrator
*after* the defects it covers were already known. It cannot show the implementation was
right — only that a defect found once cannot return unnoticed.

## Why it exists

Four consecutive audits found real defects the frozen thirty could not detect. Every one of
those thirty has at most one branch scope active, mapping keys equal to record ids,
well-typed fields, and branch conclusions already present. They are a good sample of
*well-formed* transitions and no sample at all of hostile ones. Two of the defects FX2 now
guards — a duplicated `active_scopes` entry and a join over unconcluded branches — needed no
forged evidence at all.

## Expectations are hand-written

Every expected verdict in `build_fx2.py` is stated from the semantic contract, before any
verifier runs. Generating expectations by execution would make the suite a record of what
the code does rather than of what it should do — the self-validation this project now
forbids. Production is then measured against them; a mismatch is a finding either way.

## 13 of 40 diverge from the frozen reference, deliberately

Production is stricter than the reference on the frame condition (which the reference applies
to claims only), on scope containment (the reference has no scope tree), and on trust modes
(the reference has none). Each diverging fixture records `frozen_reference_checker:
"DIVERGES"` with the reason. **An undeclared divergence would look like agreement**, and this
project has twice published a claim that production matched a reference it had quietly moved
away from.

## Files

| file | role |
|---|---|
| `build_fx2.py` | generator; the expectations and their rationales live here |
| `fixtures_v2.json` | the suite. Strict RFC 8259 — verified with an independent parser |
| `schemas/semantic_case_v2.schema.json` | extends the frozen case schema; `$ref`s its structural `$defs` so there is one definition of a case |
| `manifest.json` | versions, hashes, counts, validation record, limitations |

Regenerate: `python3 experiments/semantic_firewall_v2/build_fx2.py`

## Two schema notes

The suite carries `NaN` as a **`materialise` instruction**, not a literal. An earlier build
embedded the literal; RFC 8259 has no `NaN`, and an independent Ruby parse rejected the whole
file. Caught before commit, which is the point of the independent-validator rule.

The v2 schema makes `domain` **optional** on a claim. The frozen schema requires it, which
makes "this claim carries no domain" inexpressible — and D-048 established that the absence
is semantically meaningful (unavailable evidence, `UNRESOLVED`) and distinct from a wrong
domain (`INVALID`). Recorded as a limitation of the frozen schema rather than repaired there,
because that schema describes an experiment which never exercised the distinction.
