"""Offline chatbot engine with optional local-LLM cognition and no API calls."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Protocol, Tuple


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


class CognitionBackend(Protocol):
    name: str

    def generate(self, prompt: str, state: ChatState) -> str:
        ...


class RuleBasedCognition:
    """Deterministic local cognition."""

    name = "rule-based"

    def __init__(self, intents: List[Intent], rng: random.Random) -> None:
        self._intents = intents
        self._rng = rng

    def generate(self, prompt: str, state: ChatState) -> str:
        lowered = prompt.lower()
        intent = self._match_intent(lowered)
        if intent:
            state.topic_counts[intent.name] = state.topic_counts.get(intent.name, 0) + 1
            msg = self._rng.choice(intent.responses)
            return msg.replace("{name}", state.user_name or "there")

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
    """Local generative cognition (transformers), no external API usage.

    This backend is optional and only activates when `transformers` + `torch`
    are installed and a local model is loadable.
    """

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
                # Safe offline fallback when model/deps are unavailable.
                self._backend = self._rule_backend

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

        return self._backend.generate(text, self.state)

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
            "Commands: /help, /summary, /time, /mode, quit. "
            "I run fully offline with optional local LLM cognition."
        )

    def _summary_message(self) -> str:
        name = self.state.user_name or "Unknown"
        topics = ", ".join(
            f"{k}:{v}" for k, v in sorted(self.state.topic_counts.items())
        ) or "none"
        return (
            f"Session summary -> user: {name}, turns: {self.state.turns}, "
            f"topics: {topics}, mode: {self.cognition_mode}."
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
