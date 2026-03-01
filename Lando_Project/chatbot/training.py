"""Local training utilities for Lando chatbot intent cognition.

This module trains a tiny multinomial Naive Bayes classifier for intent prediction
using built-in offline samples. No external API calls are required.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


TOKEN_RE = re.compile(r"[a-zA-Z']+")
MODEL_PATH = Path(__file__).with_name("intent_model.json")


@dataclass
class Sample:
    text: str
    label: str


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def default_samples() -> List[Sample]:
    raw: List[Tuple[str, str]] = [
        ("hello there", "greeting"),
        ("hey good morning", "greeting"),
        ("hi how are you", "greeting"),
        ("can you help me focus", "productivity"),
        ("i need a productivity plan", "productivity"),
        ("create a schedule for today", "productivity"),
        ("i need to debug python tests", "coding"),
        ("help me refactor this code", "coding"),
        ("there is a software bug", "coding"),
        ("i feel stressed and overwhelmed", "motivation"),
        ("i'm tired and stuck", "motivation"),
        ("motivate me to continue", "motivation"),
        ("goodbye for now", "farewell"),
        ("bye see you later", "farewell"),
        ("talk to you later", "farewell"),
    ]
    return [Sample(text=t, label=l) for t, l in raw]


def train(samples: Iterable[Sample]) -> Dict[str, object]:
    class_counts: Counter[str] = Counter()
    token_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    vocab: Counter[str] = Counter()

    samples = list(samples)
    for sample in samples:
        class_counts[sample.label] += 1
        tokens = tokenize(sample.text)
        token_counts[sample.label].update(tokens)
        vocab.update(tokens)

    classes = sorted(class_counts)
    total_docs = sum(class_counts.values())
    vocab_size = len(vocab)

    priors = {c: math.log(class_counts[c] / total_docs) for c in classes}
    likelihoods: Dict[str, Dict[str, float]] = {}
    token_totals = {c: sum(token_counts[c].values()) for c in classes}

    for c in classes:
        likelihoods[c] = {}
        denom = token_totals[c] + vocab_size
        for tok in vocab:
            # Laplace smoothing
            likelihoods[c][tok] = math.log((token_counts[c][tok] + 1) / denom)

    model: Dict[str, object] = {
        "classes": classes,
        "priors": priors,
        "likelihoods": likelihoods,
        "vocab": sorted(vocab.keys()),
        "meta": {"docs": total_docs, "vocab_size": vocab_size},
    }
    return model


def save_model(model: Dict[str, object], path: Path = MODEL_PATH) -> Path:
    path.write_text(json.dumps(model, indent=2))
    return path


def run_training() -> Path:
    model = train(default_samples())
    return save_model(model)


if __name__ == "__main__":
    out = run_training()
    print(f"trained_model={out}")
