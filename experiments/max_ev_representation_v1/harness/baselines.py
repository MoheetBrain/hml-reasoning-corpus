"""Controls that decide whether a probe result means anything (mission §13, §14).

Two baselines, and the second is the one that matters here.

**Class prior.** Predict the training distribution regardless of input. Its cross-entropy is
the zero point of ``StateInformationGain``. If an arm does not beat it, that arm's
representation/model interface extracted nothing and §14A says stop.

**Bag of words.** A multinomial logistic regression over token counts, no model involved.
This is the honest ceiling for "solvable by lexical pattern matching", and the leakage audit
alone cannot establish it: that audit measures *single-token* mutual information, and a
linear combination of many weakly-informative tokens can be far stronger than any one of
them.

Reporting the probe without this number would leave the central objection unanswered. A probe
that beats the class prior but not bag-of-words has demonstrated that the *task* has signal,
not that the *model* is reading mathematical state -- and a representation comparison built on
it would be a comparison of tokenisation. Where the probe sits relative to this line is the
first thing to look at in the Stage 1 result.
"""

from __future__ import annotations

import re
from collections import Counter

import numpy as np

from .probe import ProbeConfig, train_probe

__all__ = ["bag_of_words_features", "run_bag_of_words", "TOKEN"]

TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[^\sA-Za-z0-9_]")


def bag_of_words_features(
    train_texts: list[str], other_texts: dict[str, list[str]], max_features: int = 4000
) -> tuple[np.ndarray, dict[str, np.ndarray], list[str]]:
    """Log-scaled token counts over a vocabulary fixed on the training split.

    The vocabulary comes from training only, for the same reason the probe's scaler does: a
    vocabulary fitted on the evaluation split would carry information about it.
    """
    df = Counter()
    for text in train_texts:
        df.update(set(TOKEN.findall(text)))
    vocab = [t for t, _ in df.most_common(max_features)]
    index = {t: i for i, t in enumerate(vocab)}

    def vectorise(texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), len(vocab)), dtype=np.float32)
        for row, text in enumerate(texts):
            counts = Counter(TOKEN.findall(text))
            for tok, c in counts.items():
                j = index.get(tok)
                if j is not None:
                    out[row, j] = c
        return np.log1p(out)

    return vectorise(train_texts), {k: vectorise(v) for k, v in other_texts.items()}, vocab


def run_bag_of_words(
    train_texts: list[str],
    y_train: np.ndarray,
    dev_texts: list[str],
    y_dev: np.ndarray,
    eval_texts: dict[str, list[str]],
    seed: int = 0,
    max_features: int = 4000,
) -> dict:
    """Train the lexical control with the same head and schedule as the real probe."""
    x_train, others, vocab = bag_of_words_features(
        train_texts, {"__dev__": dev_texts, **eval_texts}, max_features
    )
    x_dev = others.pop("__dev__")
    result = train_probe(
        x_train, y_train, x_dev, y_dev, others,
        ProbeConfig(kind="linear", seed=seed, epochs=120, lr=3e-3),
    )
    result["vocabulary_size"] = len(vocab)
    return result
