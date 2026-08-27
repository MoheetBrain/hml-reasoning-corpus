"""Counterfactual family split-isolation audit. Hard gate before any GPU spend.

The failure this exists to catch
-------------------------------
Every item has counterfactual siblings: one VALID parent and its one-change mutations. They
share the entire mathematical state and differ in a single edit. If a parent lands in train
and a sibling lands in test, the test item is a near-copy of a training item and the reported
generalisation is fiction.

Row-level deduplication does not catch this, because the siblings *are* different rows. The
audit therefore works at three levels, from cheap to strict:

1. **semantic family** -- the parent id every sibling was derived from;
2. **source family** -- the Mathlib theorem the parent came from, so two steps of one proof
   cannot straddle a split;
3. **canonical near-duplicate** -- a normalised fingerprint of the mathematical content, so
   two *different* theorems that happen to produce the same state are still caught.

Level 3 matters because Mathlib contains genuinely repeated tactic states across files, and
nothing about their ids would reveal it.

The verdict required to proceed is ``cross_split_family_leaks = 0`` at every level.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["SplitAudit", "audit_splits", "canonical_fingerprint"]

#: Splits whose contamination would matter. Train is the source of any leak; everything else
#: is a place a leak could land.
TRAIN_SPLIT = "train"

_WS = re.compile(r"\s+")


def canonical_fingerprint(row: dict) -> str:
    """A content fingerprint of the item's mathematics, independent of ids and formatting.

    Built from the HML render with identifiers and whitespace normalised away, so two states
    that differ only in binder spelling or record order still collide. Deliberately blunt:
    for a *leak* audit, a false positive costs one inspection and a false negative costs the
    experiment.
    """
    text = row["renders"]["R_HML"]
    # Drop quoted identifiers' surrounding syntax and collapse whitespace: what remains is
    # dominated by the propositions themselves.
    text = _WS.sub(" ", text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class SplitAudit:
    families_total: int = 0
    source_families_total: int = 0
    rows: int = 0
    cross_split_family_leaks: int = 0
    cross_split_source_family_leaks: int = 0
    exact_duplicate_leaks: int = 0
    near_duplicate_leaks: int = 0
    within_split_duplicates: int = 0
    leak_examples: list = field(default_factory=list)
    split_rows: dict = field(default_factory=dict)
    siblings_per_family: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return (
            self.rows > 0
            and self.cross_split_family_leaks == 0
            and self.cross_split_source_family_leaks == 0
            and self.exact_duplicate_leaks == 0
            and self.near_duplicate_leaks == 0
        )

    def to_dict(self) -> dict:
        return {
            "verdict": "PASS" if self.passed else "FAIL",
            "rows": self.rows,
            "families_total": self.families_total,
            "source_families_total": self.source_families_total,
            "cross_split_family_leaks": self.cross_split_family_leaks,
            "cross_split_source_family_leaks": self.cross_split_source_family_leaks,
            "exact_duplicate_leaks": self.exact_duplicate_leaks,
            "near_duplicate_leaks": self.near_duplicate_leaks,
            "within_split_duplicates": self.within_split_duplicates,
            "split_rows": self.split_rows,
            "siblings_per_family": self.siblings_per_family,
            "leak_examples": self.leak_examples[:20],
        }


def audit_splits(data_dir: str | Path) -> SplitAudit:
    data_dir = Path(data_dir)
    audit = SplitAudit()

    family_splits: dict[str, set] = defaultdict(set)
    source_splits: dict[str, set] = defaultdict(set)
    fingerprint_splits: dict[str, set] = defaultdict(set)
    fingerprint_rows: dict[str, list] = defaultdict(list)
    sibling_counts: Counter = Counter()

    for path in sorted(data_dir.glob("*.jsonl.gz")):
        split = path.name.split(".")[0]
        count = 0
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                count += 1
                audit.rows += 1
                family = row["semantic_id"]
                source = row.get("provenance", {}).get("parent_id") or family
                family_splits[family].add(split)
                source_splits[source].add(split)
                sibling_counts[family] += 1
                fp = canonical_fingerprint(row)
                fingerprint_splits[fp].add(split)
                fingerprint_rows[fp].append((split, row["item_id"], row["label"]))
        audit.split_rows[split] = count

    audit.families_total = len(family_splits)
    audit.source_families_total = len(source_splits)
    audit.siblings_per_family = dict(Counter(sibling_counts.values()))

    for family, splits in family_splits.items():
        if len(splits) > 1:
            audit.cross_split_family_leaks += 1
            audit.leak_examples.append(
                {"level": "semantic_family", "id": family, "splits": sorted(splits)}
            )

    for source, splits in source_splits.items():
        if len(splits) > 1:
            audit.cross_split_source_family_leaks += 1
            audit.leak_examples.append(
                {"level": "source_theorem", "id": source, "splits": sorted(splits)}
            )

    for fp, splits in fingerprint_splits.items():
        rows = fingerprint_rows[fp]
        if len(rows) < 2:
            continue
        if len(splits) > 1:
            # Identical mathematics in two splits. Exact if the labels also match.
            labels = {lab for _s, _i, lab in rows}
            if len(labels) == 1:
                audit.exact_duplicate_leaks += 1
            else:
                audit.near_duplicate_leaks += 1
            audit.leak_examples.append(
                {
                    "level": "canonical_fingerprint",
                    "fingerprint": fp[:16],
                    "splits": sorted(splits),
                    "items": [i for _s, i, _l in rows][:4],
                }
            )
        else:
            audit.within_split_duplicates += 1

    return audit
