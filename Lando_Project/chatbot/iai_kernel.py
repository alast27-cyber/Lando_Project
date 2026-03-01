"""IAI three-layer kernel with an energy-minimization decision driver.

Layer order:
- Reflex (predefined mapping)
- Instinct (retrieval from learned memory)
- Cognition (fallback synthesis + compile-down)
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")


@dataclass
class EMDDecision:
    """Metadata for the selected inference layer."""

    layer: str
    confidence: float
    energy_cost: float


class IAIKernel:
    """Prototype IAI kernel that routes through Reflex -> Instinct -> Cognition."""

    def __init__(
        self,
        reflex_map: Optional[Dict[str, str]] = None,
        instinct_threshold: float = 0.78,
    ) -> None:
        self.reflex_map = reflex_map or {
            "hello": "Hello! Nice to meet you.",
            "hi": "Hi there!",
            "help": "Try asking me about productivity, coding, or motivation.",
        }
        self.instinct_threshold = instinct_threshold
        self._memory: List[Dict[str, str]] = []

    @property
    def memory_size(self) -> int:
        return len(self._memory)

    def respond(self, query: str) -> Dict[str, object]:
        """Return response payload with selected layer and EMD metadata."""
        text = query.strip()
        if not text:
            decision = EMDDecision(layer="reflex", confidence=1.0, energy_cost=0.05)
            return self._payload("Please enter a message.", decision)

        reflex_hit = self._match_reflex(text)
        if reflex_hit is not None:
            decision = EMDDecision(layer="reflex", confidence=1.0, energy_cost=0.1)
            return self._payload(reflex_hit, decision)

        instinct_hit, score = self._retrieve_instinct(text)
        if instinct_hit is not None and score >= self.instinct_threshold:
            decision = EMDDecision(layer="instinct", confidence=score, energy_cost=0.35)
            return self._payload(instinct_hit["answer"], decision)

        answer = self._cognition(text)
        self._memory.append({"query": text, "answer": answer})
        decision = EMDDecision(layer="cognition", confidence=0.55, energy_cost=1.0)
        return self._payload(answer, decision)

    def save_memory(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"memory": self._memory}, indent=2), encoding="utf-8")

    def load_memory(self, path: Path) -> None:
        if not path.exists():
            self._memory = []
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._memory = [
            {"query": item["query"], "answer": item["answer"]}
            for item in payload.get("memory", [])
            if isinstance(item, dict) and "query" in item and "answer" in item
        ]

    def _match_reflex(self, text: str) -> Optional[str]:
        lowered = text.lower()
        for key, value in self.reflex_map.items():
            if key in lowered:
                return value
        return None

    def _retrieve_instinct(self, text: str) -> Tuple[Optional[Dict[str, str]], float]:
        if not self._memory:
            return None, 0.0

        # Preferred path with sklearn TF-IDF for semantic-ish sparse retrieval.
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            from sklearn.metrics.pairwise import cosine_similarity  # type: ignore

            docs = [item["query"] for item in self._memory]
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(docs + [text])
            sims = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
            idx = int(sims.argmax())
            return self._memory[idx], float(sims[idx])
        except Exception:
            # Fallback: token-overlap cosine.
            q_tokens = self._token_counts(text)
            best_item: Optional[Dict[str, str]] = None
            best_score = 0.0
            for item in self._memory:
                score = self._cosine_counts(q_tokens, self._token_counts(item["query"]))
                if score > best_score:
                    best_score = score
                    best_item = item
            return best_item, best_score

    def _cognition(self, text: str) -> str:
        return (
            "I don't have a direct reflex or instinct match yet. "
            f"Based on your message, here's a first-pass answer: {text[:180]}"
        )

    def _token_counts(self, text: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for tok in TOKEN_RE.findall(text.lower()):
            counts[tok] = counts.get(tok, 0) + 1
        return counts

    def _cosine_counts(self, left: Dict[str, int], right: Dict[str, int]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(left[t] * right.get(t, 0) for t in left)
        ln = math.sqrt(sum(v * v for v in left.values()))
        rn = math.sqrt(sum(v * v for v in right.values()))
        if ln == 0 or rn == 0:
            return 0.0
        return dot / (ln * rn)

    def _payload(self, answer: str, decision: EMDDecision) -> Dict[str, object]:
        return {
            "answer": answer,
            "layer": decision.layer,
            "confidence": round(decision.confidence, 4),
            "energy_cost": decision.energy_cost,
            "memory_size": self.memory_size,
        }


__all__ = ["IAIKernel"]
