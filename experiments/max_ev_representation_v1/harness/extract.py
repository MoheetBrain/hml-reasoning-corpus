"""Frozen-model feature extraction (mission §12).

The base model's weights are never updated and never see a gradient. For every item, in
every arm, the identical procedure runs: tokenise, forward, pool. Identical means the same
function, not "the same idea" -- an arm-specific prompt template or pooling rule would make
the comparison a comparison of prompts.

Two pooling rules and two depths are extracted, giving four candidate feature sets. Which one
Stage 1 reports is chosen on **dev, from the control arms only**, before the HML test
comparison is looked at (§13). Extracting all four costs one forward pass, so the choice
costs no extra GPU time and does not have to be guessed in advance.

Truncation is recorded, never silently accepted. Arms differ in length by up to 2x here, so a
context that clipped the longest arm would penalise it for being verbose rather than for
being unreadable, and the result would be uninterpretable.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

__all__ = ["ExtractConfig", "extract_arm", "POOLINGS"]

POOLINGS = ("mean_last", "last_token_last", "mean_mid", "last_token_mid")


@dataclass
class ExtractConfig:
    model_id: str = "Qwen/Qwen3-8B"
    revision: str | None = None
    dtype: str = "bfloat16"
    max_length: int = 8192
    batch_tokens: int = 16384
    device: str = "cuda"
    trust_remote_code: bool = False
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id, "revision": self.revision, "dtype": self.dtype,
            "max_length": self.max_length, "batch_tokens": self.batch_tokens,
            "device": self.device, **self.stats,
        }


def _load(config: ExtractConfig):
    import torch
    from transformers import AutoModel, AutoTokenizer

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[
        config.dtype
    ]
    tok = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, trust_remote_code=config.trust_remote_code
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModel.from_pretrained(
        config.model_id,
        revision=config.revision,
        dtype=dtype,
        trust_remote_code=config.trust_remote_code,
    )
    model.eval().to(config.device)
    for p in model.parameters():
        p.requires_grad_(False)
    return tok, model


def extract_arm(
    texts: list[str], config: ExtractConfig, tok=None, model=None, progress_every: int = 200
) -> dict[str, np.ndarray]:
    """Pooled hidden states for one arm. Returns one array per pooling rule."""
    import torch

    if tok is None or model is None:
        tok, model = _load(config)

    n_layers = model.config.num_hidden_layers
    mid = n_layers // 2

    # Length-sorted batching: padding is wasted computation and the arms have very different
    # length distributions, so unsorted batching would spend a different amount of waste on
    # each arm. Original order is restored before returning.
    encoded = [tok(t, truncation=True, max_length=config.max_length)["input_ids"] for t in texts]
    truncated = sum(1 for e in encoded if len(e) >= config.max_length)
    lengths = [len(e) for e in encoded]
    order = sorted(range(len(encoded)), key=lambda i: lengths[i])

    out = {p: None for p in POOLINGS}
    pad_id = tok.pad_token_id
    started = time.time()
    done = 0
    batch: list[int] = []

    def flush(batch_idx: list[int]) -> None:
        nonlocal out, done
        if not batch_idx:
            return
        width = max(lengths[i] for i in batch_idx)
        ids = torch.full((len(batch_idx), width), pad_id, dtype=torch.long)
        mask = torch.zeros((len(batch_idx), width), dtype=torch.long)
        for row, i in enumerate(batch_idx):
            seq = encoded[i]
            ids[row, : len(seq)] = torch.tensor(seq, dtype=torch.long)
            mask[row, : len(seq)] = 1
        ids, mask = ids.to(config.device), mask.to(config.device)
        with torch.no_grad():
            hs = model(input_ids=ids, attention_mask=mask, output_hidden_states=True).hidden_states
        m = mask.unsqueeze(-1).to(hs[-1].dtype)
        last_pos = mask.sum(dim=1) - 1
        for name, layer in (("last", -1), ("mid", mid)):
            h = hs[layer]
            mean = (h * m).sum(dim=1) / m.sum(dim=1).clamp(min=1)
            last_tok = h[torch.arange(h.shape[0], device=h.device), last_pos]
            for key, tensor in ((f"mean_{name}", mean), (f"last_token_{name}", last_tok)):
                arr = tensor.float().cpu().numpy()
                if out[key] is None:
                    out[key] = np.zeros((len(texts), arr.shape[1]), dtype=np.float32)
                for row, i in enumerate(batch_idx):
                    out[key][i] = arr[row]
        done += len(batch_idx)
        if progress_every and done % progress_every < len(batch_idx):
            rate = done / max(1e-6, time.time() - started)
            print(f"    {done}/{len(texts)}  {rate:.1f} items/s", flush=True)

    for i in order:
        projected = (len(batch) + 1) * max([lengths[j] for j in batch] + [lengths[i]])
        if batch and projected > config.batch_tokens:
            flush(batch)
            batch = []
        batch.append(i)
    flush(batch)

    config.stats = {
        "items": len(texts),
        "tokens_total": int(sum(lengths)),
        "tokens_mean": round(float(np.mean(lengths)), 1),
        "tokens_p99": int(np.percentile(lengths, 99)),
        "tokens_max": int(max(lengths)),
        "truncated_items": truncated,
        "wall_seconds": round(time.time() - started, 2),
        "hidden_size": int(out["mean_last"].shape[1]),
        "layers": n_layers,
        "mid_layer": mid,
    }
    return out
