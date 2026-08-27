"""Leakage audit (mission §5). Training is blocked if this fails.

The question is not "is the dataset clean" but "could a model score well without reading the
mathematics". Six channels are checked, each because it has actually gone wrong somewhere in
this project's history or in the literature:

**Answer leakage.** The verdict word appearing in the input. Trivial, catastrophic, and
easy to introduce by rendering an audit field.

**Mutation-name leakage.** The mutation family is the answer with a different spelling.
It is recorded in the audit block and must never reach a render.

**Source-ID leakage.** File paths, theorem names and content hashes identify the source row.
A model that recognises the theorem need not read the state. ``arms.common.project`` strips
these before rendering; this audit checks the stripping held.

**Operation-name leakage.** Measured over ``vnext_10k``, the operation name predicts the
verifier's verdict almost perfectly. The triple construction is designed to destroy that
signal; this measures whether it did.

**Ordering leakage.** If mutated items systematically differ in record order or count, a
model can count instead of read.

**Surface-statistic leakage.** The strongest practical threat to a *linear probe on pooled
embeddings*: if length or character composition separates the classes, the probe can succeed
without any semantics. This is reported as the accuracy a decision stump on each surface
statistic achieves, alongside token-level mutual information.

Mutual information is reported in bits against a 3-class prior of log2(3) = 1.585 bits. A
token carrying an appreciable share of that is a token that answers the question.
"""

from __future__ import annotations

import gzip
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ..arms import ARM_NAMES
from ..mutate.mutations import MUTATIONS

__all__ = ["LeakageReport", "audit_files", "TOKEN"]

TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

LABELS = ("VALID", "INVALID", "UNRESOLVED")

class _NoMatch:
    @staticmethod
    def group(_i): return "?"

_NOMATCH = _NoMatch()

#: Words that name the answer. ``UNKNOWN`` is deliberately **not** here: it is a legitimate
#: status value that the model is supposed to read, and an UNRESOLVED verdict follows from
#: it by a rule the model must learn. Banning it would ban the task.
ANSWER_WORDS = {"VALID", "INVALID", "UNRESOLVED", "ADMISSIBLE", "INADMISSIBLE"}

#: Provenance that identifies the source row rather than describing the mathematics.
SOURCE_MARKERS = ("Mathlib/", ".lean", "mathlib_revision", "tactic_sha256", "theorem_id",
                  "source_example_id", "canonical_transition_sha256", "LEAN_DOJO")


def _entropy(counts) -> float:
    total = sum(counts)
    if not total:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts if c)


@dataclass
class LeakageReport:
    rows: int = 0
    answer_word_hits: Counter = field(default_factory=Counter)
    answer_word_mi: dict = field(default_factory=dict)
    mutation_name_hits: Counter = field(default_factory=Counter)
    source_marker_hits: Counter = field(default_factory=Counter)
    operation_mi: float = 0.0
    domain_area_mi: float = 0.0
    distinct_operations: list = field(default_factory=list)
    label_prior_bits: float = 0.0
    top_token_mi: dict = field(default_factory=dict)
    surface_stump: dict = field(default_factory=dict)
    ordering: dict = field(default_factory=dict)
    label_counts: Counter = field(default_factory=Counter)

    @property
    def passed(self) -> bool:
        return (
            self.rows > 0
            and all(mi < 0.01 for mi in self.answer_word_mi.values())
            and not self.mutation_name_hits
            and not self.source_marker_hits
            and self.operation_mi < 0.01
            and self.domain_area_mi < 0.01
        )

    def to_dict(self) -> dict:
        return {
            "result": "PASS" if self.passed else "FAIL",
            "rows": self.rows,
            "label_counts": dict(self.label_counts),
            "label_prior_entropy_bits": round(self.label_prior_bits, 4),
            "answer_word_rows_containing": dict(self.answer_word_hits),
            "answer_word_mutual_information_bits": {
                w: round(m, 6) for w, m in sorted(self.answer_word_mi.items())
            },
            "mutation_name_leakage": dict(self.mutation_name_hits),
            "source_id_leakage": dict(self.source_marker_hits),
            "operation_name_mutual_information_bits": round(self.operation_mi, 6),
            "distinct_operations": self.distinct_operations,
            "mathlib_area_mutual_information_bits": round(self.domain_area_mi, 6),
            "highest_token_mutual_information_bits": self.top_token_mi,
            "surface_statistic_decision_stump_accuracy": self.surface_stump,
            "ordering": self.ordering,
        }


def _stump_accuracy(values: list[float], labels: list[str]) -> float:
    """Best 3-way accuracy from thresholding one scalar. The honest ceiling for that feature.

    Both threshold and per-region label are chosen on the same data, so this *over*-states
    what a real classifier could do -- which is what a leakage bound should do.
    """
    if not values:
        return 0.0
    order = sorted(range(len(values)), key=lambda i: values[i])
    uniq = sorted(set(values))
    if len(uniq) == 1:
        return max(Counter(labels).values()) / len(labels)
    best = 0.0
    cuts = uniq[:: max(1, len(uniq) // 64)]
    for cut in cuts:
        left = Counter(labels[i] for i in order if values[i] <= cut)
        right = Counter(labels[i] for i in order if values[i] > cut)
        hit = (max(left.values()) if left else 0) + (max(right.values()) if right else 0)
        best = max(best, hit / len(labels))
    return best


def audit_files(paths, max_tokens: int = 30) -> dict[str, LeakageReport]:
    """One report per arm. Every arm is audited separately: leakage can be arm-specific."""
    reports = {arm: LeakageReport() for arm in ARM_NAMES}
    rows: list[dict] = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f)

    labels = [r["label"] for r in rows]
    prior_bits = _entropy(Counter(labels).values())

    for arm, rep in reports.items():
        rep.rows = len(rows)
        rep.label_counts = Counter(labels)
        rep.label_prior_bits = prior_bits

        token_label = defaultdict(Counter)
        doc_count = Counter()
        lengths, alpha_frac, line_counts, non_ascii = [], [], [], []

        for row in rows:
            text = row["renders"][arm]
            label = row["label"]

            for word in ANSWER_WORDS:
                if re.search(rf"\b{word}\b", text):
                    rep.answer_word_hits[word] += 1
            for family in MUTATIONS:
                if family in text:
                    rep.mutation_name_hits[family] += 1
            for marker in SOURCE_MARKERS:
                if marker in text:
                    rep.source_marker_hits[marker] += 1

            seen = set(TOKEN.findall(text))
            for tok in seen:
                token_label[tok][label] += 1
                doc_count[tok] += 1

            lengths.append(len(text))
            line_counts.append(text.count("\n"))
            alpha_frac.append(sum(c.isalpha() for c in text) / max(1, len(text)))
            non_ascii.append(sum(ord(c) > 127 for c in text))

        # Token mutual information: I(present ; label) for each token, in bits.
        n = len(rows)
        label_counts = Counter(labels)
        mi_scores = {}
        for tok, dist in token_label.items():
            present = doc_count[tok]
            absent = n - present
            if present < 20 or absent < 20:
                continue
            mi = 0.0
            for lab in LABELS:
                p_lab = label_counts[lab] / n
                if not p_lab:
                    continue
                for count, total in ((dist[lab], present), (label_counts[lab] - dist[lab], absent)):
                    if not count:
                        continue
                    p_joint = count / n
                    p_feat = total / n
                    mi += p_joint * math.log2(p_joint / (p_feat * p_lab))
            mi_scores[tok] = mi
        # An answer word present in *every* row carries zero bits, so raw hit counts cannot
        # decide this. ``VALID`` is the case in point: it is the evidence status on every
        # item by construction, and flagging it as leakage would be flagging the mathematics.
        rep.answer_word_mi = {
            w: mi_scores.get(w, 0.0) for w in ANSWER_WORDS if w in doc_count
        }
        rep.top_token_mi = {
            t: round(m, 5)
            for t, m in sorted(mi_scores.items(), key=lambda kv: -kv[1])[:max_tokens]
        }

        # Categorical channels the mission names explicitly. Both are read off the item
        # itself rather than assumed: the operation from the rendered action envelope, the
        # Mathlib area from the recorded features. The triple construction should drive both
        # to ~0 bits, and measuring is how we find out whether it did.
        def _mi(values: list[str]) -> float:
            joint = defaultdict(Counter)
            for v, lab in zip(values, labels):
                joint[v][lab] += 1
            total = 0.0
            for _v, dist in joint.items():
                p_v = sum(dist.values()) / n
                for lab, c in dist.items():
                    p_joint = c / n
                    total += p_joint * math.log2(p_joint / (p_v * (label_counts[lab] / n)))
            return total

        op_re = re.compile(r'\(operation "([^"]*)"\)')
        operations = [
            (op_re.search(r["renders"]["R_TYPED_AST"]) or _NOMATCH).group(1)
            if op_re.search(r["renders"]["R_TYPED_AST"]) else "?"
            for r in rows
        ]
        rep.operation_mi = _mi(operations)
        rep.domain_area_mi = _mi([r["features"].get("domain_area", "?") for r in rows])
        rep.distinct_operations = sorted(set(operations))

        rep.surface_stump = {
            "characters": round(_stump_accuracy(lengths, labels), 4),
            "lines": round(_stump_accuracy(line_counts, labels), 4),
            "alphabetic_fraction": round(_stump_accuracy(alpha_frac, labels), 4),
            "non_ascii_codepoints": round(_stump_accuracy(non_ascii, labels), 4),
            "majority_class_baseline": round(max(label_counts.values()) / n, 4),
        }
        rep.ordering = {
            "mean_characters_by_label": {
                lab: round(
                    sum(len(r["renders"][arm]) for r in rows if r["label"] == lab)
                    / max(1, label_counts[lab])
                )
                for lab in LABELS
            }
        }
    return reports
