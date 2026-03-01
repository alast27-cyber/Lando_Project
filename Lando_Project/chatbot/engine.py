"""Offline chatbot engine with optional local-LLM cognition and no API calls."""

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple

from .autonomous_training import AutonomousIAIIPSTrainer
from .data_sources import DataSourceInjector


@dataclass
class Intent:
    name: str
    patterns: List[str]
    responses: List[str]


@dataclass
class ChatState:
    user_name: Optional[str] = None
    topic_counts: Dict[str, int] = field(default_factory=dict)
    turns: int = 0
    online_mode: bool = False
    last_intent: Optional[str] = None


class CognitionBackend(Protocol):
    name: str

    def generate(self, prompt: str, state: ChatState) -> str:
        ...


class TrainedIntentModel:
    """Tiny Naive Bayes inference model trained offline from local samples."""

    TOKEN_RE = re.compile(r"[a-zA-Z']+")

    def __init__(self, model_path: Optional[Path] = None) -> None:
        path = model_path or Path(__file__).with_name("intent_model.json")
        self._available = path.exists()
        self._classes: List[str] = []
        self._priors: Dict[str, float] = {}
        self._likelihoods: Dict[str, Dict[str, float]] = {}
        self._vocab: set[str] = set()

        if self._available:
            try:
                payload = json.loads(path.read_text())
            except json.JSONDecodeError:
                self._available = False
                payload = {}

            self._classes = payload.get("classes", [])
            self._priors = payload.get("priors", {})
            self._likelihoods = payload.get("likelihoods", {})
            self._vocab = set(payload.get("vocab", []))

    @property
    def available(self) -> bool:
        return self._available

    def predict(self, text: str) -> Optional[str]:
        if not self._available or not text.strip():
            return None

        tokens = [t.lower() for t in self.TOKEN_RE.findall(text)]
        if not tokens:
            return None

        best_label = None
        best_score = -10e9
        for label in self._classes:
            score = float(self._priors.get(label, -10e9))
            lmap = self._likelihoods.get(label, {})
            for token in tokens:
                if token in self._vocab:
                    score += float(lmap.get(token, -12.0))
            if score > best_score:
                best_score = score
                best_label = label
        return best_label


class RuleBasedCognition:
    """Deterministic local cognition with trained-intent assist."""

    name = "rule-based"

    def __init__(self, intents: List[Intent], rng: random.Random) -> None:
        self._intents = intents
        self._rng = rng
        self._trained_model = TrainedIntentModel()

    def generate(self, prompt: str, state: ChatState) -> str:
        lowered = prompt.lower()
        intent = self._match_intent(lowered)

        # fallback to trained predictor if keyword matcher misses
        if not intent and self._trained_model.available:
            predicted = self._trained_model.predict(prompt)
            if predicted:
                intent = next((i for i in self._intents if i.name == predicted), None)

        if intent:
            state.topic_counts[intent.name] = state.topic_counts.get(intent.name, 0) + 1
            state.last_intent = intent.name
            msg = self._rng.choice(intent.responses)
            return msg.replace("{name}", state.user_name or "there")

        state.last_intent = "unknown"

        if "?" in prompt:
            return (
                "I run fully offline. Ask about greetings, productivity, coding, "
                "or motivation, or use /help."
            )

        return (
            "Thanks for sharing. Try /help to see what I can do, "
            "or tell me your name so I can personalize replies."
        )

    def _match_intent(self, lowered: str) -> Optional[Intent]:
        scored: List[Tuple[int, Intent]] = []
        for intent in self._intents:
            hits = sum(1 for pattern in intent.patterns if pattern in lowered)
            if hits:
                scored.append((hits, intent))

        if not scored:
            return None
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]


class LocalLLMCognition:
    """Local generative cognition (transformers), no external API usage."""

    name = "local-llm"

    def __init__(self, model_name: str) -> None:
        from transformers import pipeline  # type: ignore

        self._generator = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=model_name,
        )

    def generate(self, prompt: str, state: ChatState) -> str:
        user_name = state.user_name or "there"
        preface = (
            "You are Lando, a concise and helpful offline assistant. "
            f"The user's name is {user_name}. "
            "Answer in 1-3 sentences.\n"
            f"User: {prompt}\nAssistant:"
        )
        out = self._generator(
            preface,
            max_new_tokens=60,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            num_return_sequences=1,
        )
        generated = out[0]["generated_text"]
        answer = generated.split("Assistant:", maxsplit=1)[-1].strip()
        return answer or "I am thinking locally, but couldn't craft a response this turn."


class OfflineChatbot:
    """Rule-based chatbot with optional local LLM cognition."""

    def __init__(
        self,
        seed: int = 42,
        use_llm: bool = True,
        llm_model_name: str = "distilgpt2",
        data_sources_config: Optional[Path] = None,
        autonomous_training: bool = True,
        training_interval_s: int = 20,
    ) -> None:
        self._rng = random.Random(seed)
        self.state = ChatState()
        self._intents = self._build_intents()
        self._rule_backend = RuleBasedCognition(self._intents, self._rng)
        self._backend: CognitionBackend = self._rule_backend

        if use_llm:
            try:
                self._backend = LocalLLMCognition(model_name=llm_model_name)
            except Exception:
                self._backend = self._rule_backend

        config_path = data_sources_config or Path(__file__).with_name("data_sources.json")
        self._injector = DataSourceInjector.from_config(config_path)

        model_path = Path(__file__).with_name("intent_model.json")
        events_path = Path(__file__).with_name("iai_ips_events.json")
        self._trainer = AutonomousIAIIPSTrainer(
            model_path=model_path,
            events_path=events_path,
            interval_s=training_interval_s,
        )
        if autonomous_training:
            self._trainer.start()

    @property
    def cognition_mode(self) -> str:
        return self._backend.name

    def respond(self, message: str) -> str:
        text = message.strip()
        if not text:
            return "I didn't catch that. Could you type something?"

        self.state.turns += 1
        self._capture_name(text)

        lowered = text.lower()
        if lowered in {"/help", "help"}:
            return self._help_message()
        if lowered in {"/summary", "summary"}:
            return self._summary_message()
        if lowered in {"/time", "time"}:
            return f"Local time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        if lowered in {"/mode", "mode"}:
            return f"Active cognition mode: {self.cognition_mode}."
        if lowered in {"/online", "online"}:
            self.state.online_mode = True
            return "Online mode enabled. I can inject configured external knowledge sources."
        if lowered in {"/offline", "offline"}:
            self.state.online_mode = False
            return "Online mode disabled. I am now using core local cognition only."
        if lowered in {"/sources", "sources"}:
            sources = ", ".join(self._injector.list_sources()) or "none"
            return f"Configured data sources: {sources}."
        if lowered in {"/trainer", "trainer"}:
            return self._trainer.status()
        if lowered in {"/train-now", "train-now"}:
            ok = self._trainer.train_once()
            return "manual_train=updated" if ok else "manual_train=skipped (not enough events)"

        base_response = self._backend.generate(text, self.state)
        self._trainer.record(text, self.state.last_intent or "unknown")

        if self.state.online_mode:
            injected = self._injector.query(text)
            if injected:
                return f"{base_response}\n\n[Injected knowledge]\n{injected}"
        return base_response

    def _capture_name(self, text: str) -> None:
        match = re.search(
            r"\b(?:i am|i'm|my name is)\s+([A-Za-z][A-Za-z\-']{1,30})",
            text,
            re.IGNORECASE,
        )
        if match:
            self.state.user_name = match.group(1)

    def _help_message(self) -> str:
        return (
            "Commands: /help, /summary, /time, /mode, /online, /offline, /sources, /trainer, /train-now, quit. "
            "I run fully offline with optional local LLM cognition."
        )

    def _summary_message(self) -> str:
        name = self.state.user_name or "Unknown"
        topics = ", ".join(
            f"{k}:{v}" for k, v in sorted(self.state.topic_counts.items())
        ) or "none"
        return (
            f"Session summary -> user: {name}, turns: {self.state.turns}, "
            f"topics: {topics}, mode: {self.cognition_mode}, online: {self.state.online_mode}."
        )

    def _build_intents(self) -> List[Intent]:
        return [
            Intent(
                name="greeting",
                patterns=["hello", "hi", "hey", "good morning", "good evening"],
                responses=[
                    "Hello {name}! Great to chat with you.",
                    "Hey {name}, how can I help today?",
                    "Hi {name}! Tell me what's on your mind.",
                ],
            ),
            Intent(
                name="productivity",
                patterns=["focus", "productive", "plan", "schedule", "todo"],
                responses=[
                    "A quick win: pick 1 priority, set a 25-minute timer, then review.",
                    "Try a 3-step plan: define goal, break into tasks, do the first task now.",
                ],
            ),
            Intent(
                name="coding",
                patterns=["code", "python", "bug", "debug", "test", "refactor"],
                responses=[
                    "For debugging, reproduce consistently, isolate scope, then verify with tests.",
                    "A good coding loop: write a tiny test, implement minimal fix, then refactor.",
                ],
            ),
            Intent(
                name="motivation",
                patterns=["tired", "motivate", "stuck", "stress", "overwhelmed"],
                responses=[
                    "You're doing better than you think. Start tiny and build momentum.",
                    "When stuck, reduce the problem size by 10x and complete one small step.",
                ],
            ),
            Intent(
                name="farewell",
                patterns=["bye", "goodbye", "see you", "later"],
                responses=[
                    "Take care {name}!",
                    "Goodbye {name}. Come back anytime.",
                ],
            ),
        ]
