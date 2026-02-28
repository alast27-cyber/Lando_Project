"""Offline chatbot engine with no external API dependencies."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple


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


class OfflineChatbot:
    """Rule-based chatbot designed to run entirely locally."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self.state = ChatState()
        self._intents = self._build_intents()

    def respond(self, message: str) -> str:
        text = message.strip()
        if not text:
            return "I didn't catch that. Could you type something?"

        self.state.turns += 1
        self._capture_name(text)

        # command-style helpers
        lowered = text.lower()
        if lowered in {"/help", "help"}:
            return self._help_message()
        if lowered in {"/summary", "summary"}:
            return self._summary_message()
        if lowered in {"/time", "time"}:
            return f"Local time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

        intent = self._match_intent(text)
        if intent:
            self.state.topic_counts[intent.name] = self.state.topic_counts.get(intent.name, 0) + 1
            response = self._rng.choice(intent.responses)
            return self._personalize(response)

        return self._fallback(text)

    def _capture_name(self, text: str) -> None:
        match = re.search(r"\b(?:i am|i'm|my name is)\s+([A-Za-z][A-Za-z\-']{1,30})", text, re.IGNORECASE)
        if match:
            self.state.user_name = match.group(1)

    def _personalize(self, response: str) -> str:
        if "{name}" in response:
            return response.format(name=self.state.user_name or "there")
        return response

    def _match_intent(self, text: str) -> Optional[Intent]:
        lowered = text.lower()
        scored: List[Tuple[int, Intent]] = []
        for intent in self._intents:
            hits = sum(1 for pattern in intent.patterns if pattern in lowered)
            if hits:
                scored.append((hits, intent))

        if not scored:
            return None
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def _fallback(self, text: str) -> str:
        if "?" in text:
            return (
                "I run fully offline, so I answer best with topics like: "
                "greetings, productivity, coding, weather preferences, or motivation."
            )
        return (
            "Thanks for sharing. Try /help to see what I can do, "
            "or tell me your name so I can personalize replies."
        )

    def _help_message(self) -> str:
        return (
            "Commands: /help, /summary, /time, quit. "
            "I am an offline chatbot with built-in intent matching and session memory."
        )

    def _summary_message(self) -> str:
        name = self.state.user_name or "Unknown"
        topics = ", ".join(
            f"{k}:{v}" for k, v in sorted(self.state.topic_counts.items())
        ) or "none"
        return f"Session summary -> user: {name}, turns: {self.state.turns}, topics: {topics}."

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
