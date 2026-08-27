"""Build DATASET_V1: a small, balanced, verifier-labelled action-validity probe (§6-§9).

The construction in one paragraph
---------------------------------
Take a recorded Lean transition that the frozen verifier accepts. Emit it as the ``VALID``
item. Apply one causal mutation that makes it inadmissible and emit the result as the
``INVALID`` item; apply one that makes it unanswerable and emit that as ``UNRESOLVED``. All
three are rendered in all four representations. Every label is the frozen verifier's, never
a judgement of ours and never an LLM's.

Why one triple per parent
-------------------------
It makes the three classes **exactly balanced** and, more importantly, it makes every
property of the parent uninformative about the label. Domain, Mathlib area, operation name,
state size, dependency depth, goal length and source theorem are *identical* across the three
siblings, so none of them can predict the answer. That matters here specifically: measured
over ``vnext_10k``, the verifier's natural verdict is predicted almost perfectly by the
operation name alone (LEAN_TACTIC 4000/4000 VALID, SOURCE_DERIVATION 2000/2000 UNRESOLVED,
OPEN_BRANCH 61/61 INVALID). A dataset drawn from that distribution would measure a token
lookup and report it as reasoning.

Splitting
---------
Never across siblings, and never across a theorem: every item derived from one Mathlib
theorem lands in one split, so a train item cannot be a near-duplicate of a test item.
Structural OOD splits additionally hold their stratum *out of training entirely* -- an
"unseen depth" test whose depths appear in training is not a test of anything.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from hamiltonian_lang.semantic_state.verify import verify_replay

from ..arms import ARM_NAMES, render
from ..arms.common import project, to_ir
from ..canon.alpha_rename import rename_transition
from ..canon.build_canonical import BuildError, build_canonical
from ..mutate.distractors import add_distractors
from ..mutate.mutations import MUTATIONS, UNRESOLVED_FAMILIES, apply_mutation

DATASET_VERSION = "DATASET_V1-1.0.0"

INVALID_FAMILIES = tuple(f for f in MUTATIONS if f not in UNRESOLVED_FAMILIES)

#: Held out of training entirely, to test familiar primitives in an unseen combination (§9E).
COMPOSITION_HELDOUT = ("TYPE_DOMAIN_MISMATCH", "UNKNOWN_DOMAIN")

#: Mathlib areas withheld from training, to test transfer to unseen mathematics (§9F).
DOMAIN_HELDOUT = ("CategoryTheory", "NumberTheory")

#: Structural strata: an OOD split takes the top decile and training never sees it.
STRUCTURAL_AXES = {
    "ood_binder_depth": "binder_depth",
    "ood_dependency_depth": "max_dependency_depth",
    "ood_state_size": "n_claims",
}

TARGETS = {
    "train": 1000, "dev": 170, "test_iid": 170,
    "ood_alpha_rename": 90, "ood_composition": 90, "ood_domain": 150,
    "ood_binder_depth": 70, "ood_dependency_depth": 70, "ood_state_size": 70,
}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bucket(theorem: str) -> float:
    """Deterministic [0,1) position for a theorem. No RNG state, so splits are reproducible."""
    return int(hashlib.sha256(theorem.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def load_parents(path: Path, limit: int | None) -> list:
    """Every canonical item the frozen verifier accepts, with its features."""
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            rec = json.loads(line)
            try:
                item = build_canonical(rec, semantic_id=f"SEM-{rec['record_id']}")
            except BuildError:
                continue
            if str(verify_replay(item.transition).verdict) != "VALID":
                continue
            out.append(item)
    return out


def choose_family(item, families: tuple[str, ...], rng: random.Random):
    """First family (in a per-parent shuffled order) whose mutation actually flips the verdict."""
    order = list(families)
    rng.shuffle(order)
    for fam in order:
        res = apply_mutation(item.transition, fam, item.semantic_id)
        if res is not None and res.as_expected:
            return res
    return None


def build_triple(item, *, rename: bool, invalid_pool, unresolved_pool):
    """One parent -> up to three items sharing every property except admissibility."""
    rng = random.Random(int(hashlib.sha256(item.semantic_id.encode()).hexdigest()[:8], 16))
    base = rename_transition(item.transition) if rename else item.transition
    if str(verify_replay(base).verdict) != "VALID":
        return None
    bad = choose_family(item, invalid_pool, rng)
    unk = choose_family(item, unresolved_pool, rng)
    if bad is None or unk is None:
        return None

    rows = []
    for label, transition, mtype, diff, ec in (
        ("VALID", base, None, {}, None),
        ("INVALID", bad.transition, bad.mutation_type, bad.semantic_diff, bad.error_class),
        ("UNRESOLVED", unk.transition, unk.mutation_type, unk.semantic_diff, unk.error_class),
    ):
        if rename and mtype is not None:
            transition = rename_transition(transition)
            if str(verify_replay(transition).verdict) != label:
                return None
        item_id = f"{item.semantic_id}::{label}"
        transition, distractors = add_distractors(transition, item_id)
        if str(verify_replay(transition).verdict) != label:
            return None
        ir = to_ir(project(transition))
        renders = {arm: render(arm, ir) for arm in ARM_NAMES}
        rows.append(
            {
                "item_id": item_id,
                "semantic_id": item.semantic_id,
                "label": label,
                "renders": renders,
                "render_sha256": {a: sha(t) for a, t in renders.items()},
                "features": item.features,
                "audit": {
                    "mutation_type": mtype,
                    "semantic_diff": diff,
                    "verifier_error_class": ec,
                    "verifier_verdict": label,
                    "alpha_renamed": rename,
                    "mutation_seed": None if mtype is None else
                        (bad.mutation_seed if label == "INVALID" else unk.mutation_seed),
                    "distractors": distractors,
                    "generator_version": DATASET_VERSION,
                },
                "provenance": item.provenance,
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default="data/hml_50k_final/canonical/records.jsonl.gz")
    ap.add_argument("--out", default="experiments/max_ev_representation_v1/dataset/v1")
    ap.add_argument("--scan-limit", type=int, default=14000)
    args = ap.parse_args()

    src = Path(args.source)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"scanning {src} (limit {args.scan_limit}) ...", flush=True)
    parents = load_parents(src, args.scan_limit)
    print(f"  verifier-VALID canonical parents: {len(parents)}", flush=True)

    # Structural thresholds computed over the whole pool, before any split exists, so no
    # threshold can be tuned to a result.
    thresholds = {
        axis: statistics.quantiles([p.features[axis] for p in parents], n=10)[8]
        for axis in STRUCTURAL_AXES.values()
    }
    print(f"  top-decile thresholds: {thresholds}", flush=True)

    by_theorem = defaultdict(list)
    for p in parents:
        by_theorem[p.provenance["parent_id"] or p.semantic_id].append(p)

    assigned: dict[str, list] = defaultdict(list)
    used_theorems: set[str] = set()

    def extreme(p) -> set[str]:
        return {
            name for name, axis in STRUCTURAL_AXES.items()
            if p.features[axis] >= thresholds[axis]
        }

    # 1. Domain OOD claims its areas outright.
    for th, items in sorted(by_theorem.items()):
        if items[0].features["domain_area"] in DOMAIN_HELDOUT:
            used_theorems.add(th)  # never usable for training, whether or not it is sampled
            if len(assigned["ood_domain"]) < TARGETS["ood_domain"]:
                assigned["ood_domain"].append(items[0])

    # 2. Structural OOD takes theorems in the top decile of each axis.
    for th, items in sorted(by_theorem.items()):
        if th in used_theorems:
            continue
        for name in sorted(extreme(items[0])):
            if len(assigned[name]) < TARGETS[name]:
                assigned[name].append(items[0])
                used_theorems.add(th)
                break

    # 3. Everything else splits by theorem hash. Training additionally excludes the extreme
    #    strata, so the structural OOD sets test depths training never contained.
    for th, items in sorted(by_theorem.items()):
        if th in used_theorems:
            continue
        b = _bucket(th)
        target = (
            "train" if b < 0.70
            else "dev" if b < 0.80
            else "test_iid" if b < 0.90
            else "ood_alpha_rename" if b < 0.95
            else "ood_composition"
        )
        if target == "train" and extreme(items[0]):
            continue
        if len(assigned[target]) < TARGETS[target]:
            assigned[target].append(items[0])
            used_theorems.add(th)

    counts = Counter(); label_counts = Counter(); fam_counts = Counter()
    manifest_splits = {}
    for split, items in sorted(assigned.items()):
        rename = split == "ood_alpha_rename"
        if split == "ood_composition":
            inv_pool = tuple(f for f in COMPOSITION_HELDOUT if f not in UNRESOLVED_FAMILIES)
            unk_pool = tuple(f for f in COMPOSITION_HELDOUT if f in UNRESOLVED_FAMILIES)
        else:
            inv_pool = tuple(f for f in INVALID_FAMILIES if f not in COMPOSITION_HELDOUT)
            unk_pool = tuple(f for f in UNRESOLVED_FAMILIES if f not in COMPOSITION_HELDOUT)

        rows = []
        for item in items:
            triple = build_triple(
                item, rename=rename, invalid_pool=inv_pool, unresolved_pool=unk_pool
            )
            if triple is None:
                continue
            rows.extend(triple)
        path = out_dir / f"{split}.jsonl.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        counts[split] = len(rows)
        for r in rows:
            label_counts[(split, r["label"])] += 1
            if r["audit"]["mutation_type"]:
                fam_counts[r["audit"]["mutation_type"]] += 1
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_splits[split] = {
            "rows": len(rows),
            "parents": len({r["semantic_id"] for r in rows}),
            "labels": {
                lab: sum(1 for r in rows if r["label"] == lab)
                for lab in ("VALID", "INVALID", "UNRESOLVED")
            },
            "sha256": digest,
            "alpha_renamed": rename,
            "mutation_families": sorted({
                r["audit"]["mutation_type"] for r in rows if r["audit"]["mutation_type"]
            }),
        }
        print(f"  {split:22s} rows={len(rows):5d} parents={len(items):5d} sha={digest[:12]}",
              flush=True)

    manifest = {
        "dataset_version": DATASET_VERSION,
        "arms": list(ARM_NAMES),
        "task": "ACTION_VALIDITY",
        "labels": ["VALID", "INVALID", "UNRESOLVED"],
        "label_source": "hamiltonian_lang.semantic_state.verify.verify_replay",
        "structural_thresholds": thresholds,
        "domain_heldout": list(DOMAIN_HELDOUT),
        "composition_heldout": list(COMPOSITION_HELDOUT),
        "splits": manifest_splits,
        "total_rows": sum(counts.values()),
        "mutation_family_usage": dict(sorted(fam_counts.items())),
    }
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8"
    )
    print(f"\ntotal rows: {sum(counts.values())}")
    print(f"manifest: {out_dir / 'MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
