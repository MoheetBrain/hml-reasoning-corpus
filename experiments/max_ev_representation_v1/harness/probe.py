"""Frozen-model probes: linear (Stage 1) and matched MLP (Stage 2).

The base model is never updated. A probe measures what a representation makes *linearly
available* to a reader that has no capacity to compute anything itself; if the information is
there and a linear map can find it, the representation surfaced it. Stage 2 replaces the
linear head with a small MLP to ask the follow-up question -- is the structure present but
not linearly separable? -- and nothing else about the pipeline changes, so the two stages are
comparable.

Every hyperparameter is identical across arms, by construction: :func:`train_probe` takes one
config and is called once per arm with the same object. An arm-specific learning rate would
make the comparison a comparison of tuning effort.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import torch
from torch import nn

__all__ = ["ProbeConfig", "train_probe", "standardise"]


@dataclass(frozen=True)
class ProbeConfig:
    kind: str = "linear"          # "linear" | "mlp"
    hidden: int = 256
    dropout: float = 0.1
    epochs: int = 120
    lr: float = 3e-3
    weight_decay: float = 1e-2
    batch_size: int = 256
    seed: int = 0
    #: Stop when dev cross-entropy has not improved for this many epochs. Selection is on
    #: dev only; the test split is read once, after everything is fixed.
    patience: int = 20

    def to_dict(self) -> dict:
        return asdict(self)


def standardise(train: np.ndarray, *others: np.ndarray):
    """Zero-mean unit-variance using **training** statistics only.

    Fitting the scaler on the evaluation split would leak its distribution into the probe --
    a small effect that nonetheless differs by arm, which is exactly the kind of asymmetry
    this experiment cannot afford.
    """
    mu = train.mean(axis=0, keepdims=True)
    sd = train.std(axis=0, keepdims=True)
    sd[sd < 1e-6] = 1.0
    return ((train - mu) / sd, *[(o - mu) / sd for o in others])


class _Linear(nn.Module):
    def __init__(self, d_in: int, k: int):
        super().__init__()
        self.net = nn.Linear(d_in, k)

    def forward(self, x):
        return self.net(x)


class _MLP(nn.Module):
    def __init__(self, d_in: int, k: int, hidden: int, dropout: float):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, k),
        )

    def forward(self, x):
        return self.net(x)


def train_probe(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_dev: np.ndarray,
    y_dev: np.ndarray,
    evals: dict[str, np.ndarray],
    config: ProbeConfig,
    n_classes: int = 3,
    device: str = "cpu",
) -> dict:
    """Train one probe and return predicted probabilities for every evaluation split."""
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    x_train_s, x_dev_s, *eval_s = standardise(
        x_train, x_dev, *[evals[k] for k in sorted(evals)]
    )
    eval_map = dict(zip(sorted(evals), eval_s))

    dev = torch.device(device)
    xt = torch.tensor(x_train_s, dtype=torch.float32, device=dev)
    yt = torch.tensor(y_train, dtype=torch.long, device=dev)
    xd = torch.tensor(x_dev_s, dtype=torch.float32, device=dev)
    yd = torch.tensor(y_dev, dtype=torch.long, device=dev)

    model = (
        _Linear(xt.shape[1], n_classes)
        if config.kind == "linear"
        else _MLP(xt.shape[1], n_classes, config.hidden, config.dropout)
    ).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    best_dev = float("inf")
    best_epoch = -1
    since = 0

    n = len(xt)
    for epoch in range(config.epochs):
        model.train()
        perm = torch.randperm(n, device=dev)
        for start in range(0, n, config.batch_size):
            idx = perm[start : start + config.batch_size]
            opt.zero_grad()
            loss = loss_fn(model(xt[idx]), yt[idx])
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            dev_loss = float(loss_fn(model(xd), yd))
        if dev_loss < best_dev - 1e-5:
            best_dev, best_epoch, since = dev_loss, epoch, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            since += 1
            if since >= config.patience:
                break

    model.load_state_dict(best_state)
    model.eval()
    out = {}
    with torch.no_grad():
        for name, arr in eval_map.items():
            logits = model(torch.tensor(arr, dtype=torch.float32, device=dev))
            out[name] = torch.softmax(logits, dim=1).cpu().numpy()
    return {
        "probs": out,
        "best_epoch": best_epoch,
        "best_dev_loss_nats": round(best_dev, 5),
        "config": config.to_dict(),
        "n_parameters": int(sum(p.numel() for p in model.parameters())),
    }
