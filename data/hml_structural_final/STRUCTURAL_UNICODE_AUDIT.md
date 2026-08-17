# Structural Unicode Audit

Status: **NOT APPLICABLE TO MODEL VIEWS — none were emitted**.

The two machine census artifacts are UTF-8 JSON written with
`ensure_ascii=False`. Their literal mathematical symbols (including `⊢`, `¬`, and
`∞`) remain UTF-8. The manifest verifier rejects literal JSON `\\uXXXX` escapes in
all mission JSON except the manifest itself.

No HML/neutral output strings exist, so there is no model-view character, byte, or
mathematical-symbol percentage to report and no claim that the historical escaping
defect has been tested on a benchmark. Model-view mathematical escape count: **not
applicable**.

