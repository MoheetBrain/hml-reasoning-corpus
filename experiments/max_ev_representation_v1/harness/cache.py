"""Frozen-feature cache (mission §6).

The base model is frozen, so its hidden states are a pure function of

    model SHA, tokenizer SHA, dataset hash, renderer hash, max_length, dtype, pooling rule

and there is no reason to buy them twice. Stage 2's MLP probe, alternate regularisation,
bootstrap re-analysis and any diagnostic head can all run from this cache on CPU.

Correctness rules
-----------------
**The key is the whole provenance, not a filename.** Every input that could change the
tensors is hashed into the key and written into the sidecar metadata; a load with any
mismatch is a miss, never a silent reuse. A cache that returns stale features is worse than
no cache, because the run still produces a plausible number.

**float16 on disk, float32 in the probe.** Halves the footprint. `verify_precision` measures
what that costs on real vectors rather than assuming it is nothing -- the round trip must
leave probe-relevant statistics unchanged to the tolerance recorded in the metadata.

**Token lengths travel with the features.** They are needed for the §19 length interaction
and the §20 cost accounting, and recomputing them later would require the tokenizer back.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

__all__ = ["CacheKey", "FeatureCache", "verify_precision"]

TOKEN_KEY = "__token_lengths__"


@dataclass(frozen=True)
class CacheKey:
    """Everything that could change the tensors. Anything omitted here is a correctness bug."""

    model_sha: str
    tokenizer_sha: str
    dataset_sha: str
    renderer_commit: str
    code_sha: str
    max_length: int
    dtype: str
    poolings: tuple[str, ...]

    def digest(self) -> str:
        payload = json.dumps(
            {
                "model_sha": self.model_sha, "tokenizer_sha": self.tokenizer_sha,
                "dataset_sha": self.dataset_sha, "renderer_commit": self.renderer_commit,
                "code_sha": self.code_sha, "max_length": self.max_length,
                "dtype": self.dtype, "poolings": list(self.poolings),
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "model_sha": self.model_sha, "tokenizer_sha": self.tokenizer_sha,
            "dataset_sha": self.dataset_sha, "renderer_commit": self.renderer_commit,
            "code_sha": self.code_sha, "max_length": self.max_length, "dtype": self.dtype,
            "poolings": list(self.poolings), "digest": self.digest(),
        }


class FeatureCache:
    def __init__(self, root: str | Path, key: CacheKey, storage_dtype: str = "float16"):
        self.key = key
        self.storage_dtype = storage_dtype
        self.root = Path(root) / key.model_sha[:16] / key.dataset_sha[:16]
        self.hits = 0
        self.misses = 0
        self.written = 0

    def _path(self, arm: str, split: str) -> Path:
        return self.root / arm / f"{split}.npz"

    def _meta_path(self, arm: str, split: str) -> Path:
        return self.root / arm / f"{split}.meta.json"

    def load(self, arm: str, split: str) -> dict[str, np.ndarray] | None:
        path, meta_path = self._path(arm, split), self._meta_path(arm, split)
        if not path.exists() or not meta_path.exists():
            self.misses += 1
            return None
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:  # noqa: BLE001
            self.misses += 1
            return None
        if meta.get("key", {}).get("digest") != self.key.digest():
            # Provenance changed. Refuse rather than reuse: this is the whole point.
            self.misses += 1
            return None
        with np.load(path) as data:
            out = {k: data[k] for k in data.files}
        for name in list(out):
            if name != TOKEN_KEY:
                out[name] = out[name].astype(np.float32)
        self.hits += 1
        return out

    def store(self, arm: str, split: str, features: dict[str, np.ndarray], stats: dict) -> None:
        path = self._path(arm, split)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {}
        for name, arr in features.items():
            payload[name] = (
                arr.astype(np.int32) if name == TOKEN_KEY
                else arr.astype(self.storage_dtype)
            )
        np.savez_compressed(path, **payload)
        self._meta_path(arm, split).write_text(
            json.dumps(
                {
                    "key": self.key.to_dict(),
                    "arm": arm,
                    "split": split,
                    "storage_dtype": self.storage_dtype,
                    "shapes": {k: list(v.shape) for k, v in payload.items()},
                    "hidden_size": int(features["mean_last"].shape[1]),
                    "extraction_stats": stats,
                    "written_unix": int(time.time()),
                },
                indent=1, sort_keys=True,
            ),
            encoding="utf-8",
        )
        self.written += 1

    def size_bytes(self) -> int:
        return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())

    def report(self) -> dict:
        return {
            "root": str(self.root),
            "hits": self.hits,
            "misses": self.misses,
            "written": self.written,
            "size_bytes": self.size_bytes() if self.root.exists() else 0,
            "storage_dtype": self.storage_dtype,
            "key": self.key.to_dict(),
        }


def verify_precision(array: np.ndarray, storage_dtype: str = "float16") -> dict:
    """Measure what the float16 round trip costs on real vectors.

    Reported rather than assumed. The quantities that matter are the ones a standardised
    linear probe consumes: per-feature mean and standard deviation, and the relative error of
    the values themselves.
    """
    round_tripped = array.astype(storage_dtype).astype(np.float32)
    denom = np.abs(array).mean() or 1.0
    return {
        "storage_dtype": storage_dtype,
        "max_abs_error": float(np.abs(round_tripped - array).max()),
        "mean_abs_error": float(np.abs(round_tripped - array).mean()),
        "mean_relative_error": float(np.abs(round_tripped - array).mean() / denom),
        "max_mean_shift": float(np.abs(round_tripped.mean(0) - array.mean(0)).max()),
        "max_std_shift": float(np.abs(round_tripped.std(0) - array.std(0)).max()),
    }
