"""Autonomous background training for Lando IAI-IPS intent cognition."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from .training import Sample, default_samples, save_model, train


@dataclass
class IAIIPSEvent:
    text: str
    label: str
    ts: float


class AutonomousIAIIPSTrainer:
    """Continuously improves intent model from interaction events.

    The trainer runs in a daemon thread, periodically consolidating base samples
    + collected runtime events into a refreshed Naive Bayes model.
    """

    def __init__(
        self,
        model_path: Path,
        events_path: Path,
        interval_s: int = 20,
        min_events_to_train: int = 5,
    ) -> None:
        self.model_path = model_path
        self.events_path = events_path
        self.interval_s = interval_s
        self.min_events_to_train = min_events_to_train

        self._lock = threading.Lock()
        self._events: List[IAIIPSEvent] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cycles = 0

        self._load_events()

    def _load_events(self) -> None:
        if not self.events_path.exists():
            return
        try:
            payload = json.loads(self.events_path.read_text())
            self._events = [IAIIPSEvent(**item) for item in payload.get("events", [])]
        except Exception:
            self._events = []

    def _persist_events(self) -> None:
        self.events_path.write_text(json.dumps({"events": [asdict(e) for e in self._events]}, indent=2))

    def record(self, text: str, label: str) -> None:
        if not text.strip() or not label.strip():
            return
        with self._lock:
            self._events.append(IAIIPSEvent(text=text.strip(), label=label.strip(), ts=time.time()))
            self._persist_events()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)

    def status(self) -> str:
        with self._lock:
            return (
                f"trainer=running:{self._running}, cycles:{self._cycles}, "
                f"events:{len(self._events)}, interval_s:{self.interval_s}"
            )

    def train_once(self) -> bool:
        with self._lock:
            if len(self._events) < self.min_events_to_train:
                return False
            runtime_samples = [Sample(text=e.text, label=e.label) for e in self._events]

        merged_samples = default_samples() + runtime_samples
        model = train(merged_samples)
        save_model(model, self.model_path)

        with self._lock:
            self._cycles += 1
        return True

    def _loop(self) -> None:
        while self._running:
            try:
                self.train_once()
            except Exception:
                pass
            time.sleep(self.interval_s)
