"""Data source injection infrastructure for Lando chatbot knowledge expansion."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol


class KnowledgeSource(Protocol):
    name: str

    def query(self, prompt: str) -> Optional[str]:
        ...


@dataclass
class LocalFileSource:
    name: str
    path: Path
    max_chars: int = 600

    def query(self, prompt: str) -> Optional[str]:
        if not self.path.exists():
            return None

        text = self.path.read_text(errors="ignore")
        lowered = prompt.lower()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        matches = [ln for ln in lines if any(tok in ln.lower() for tok in lowered.split() if len(tok) > 3)]
        snippet = " ".join(matches[:3]) if matches else text[: self.max_chars]
        snippet = snippet.strip()
        if not snippet:
            return None
        return f"{self.name}: {snippet[:self.max_chars]}"


@dataclass
class WikipediaSource:
    name: str = "wikipedia"
    language: str = "en"

    def query(self, prompt: str) -> Optional[str]:
        topic = self._extract_topic(prompt)
        if not topic:
            return None
        try:
            import requests  # type: ignore

            url = f"https://{self.language}.wikipedia.org/api/rest_v1/page/summary/{topic}"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                return None
            data = resp.json()
            extract = data.get("extract")
            if not extract:
                return None
            return f"Wikipedia ({topic}): {extract[:500]}"
        except Exception:
            return None

    def _extract_topic(self, prompt: str) -> Optional[str]:
        lowered = prompt.lower().strip()
        trigger = "about "
        idx = lowered.find(trigger)
        if idx == -1:
            return None
        raw = prompt[idx + len(trigger) :].strip()
        if not raw:
            return None
        return raw.split()[0].capitalize()


class DataSourceInjector:
    """Container to query multiple sources and inject external knowledge context."""

    def __init__(self, sources: Optional[List[KnowledgeSource]] = None) -> None:
        self.sources: List[KnowledgeSource] = sources or []

    def register(self, source: KnowledgeSource) -> None:
        self.sources.append(source)

    def list_sources(self) -> List[str]:
        return [s.name for s in self.sources]

    def query(self, prompt: str) -> Optional[str]:
        chunks: List[str] = []
        for src in self.sources:
            val = src.query(prompt)
            if val:
                chunks.append(val)
        if not chunks:
            return None
        return "\n".join(chunks[:3])

    @classmethod
    def from_config(cls, config_path: Path) -> "DataSourceInjector":
        if not config_path.exists():
            return cls([])
        payload = json.loads(config_path.read_text())
        sources: List[KnowledgeSource] = []
        for item in payload.get("sources", []):
            kind = item.get("type")
            name = item.get("name", kind)
            if kind == "local_file":
                path = Path(item.get("path", ""))
                sources.append(LocalFileSource(name=name, path=path))
            elif kind == "wikipedia":
                lang = item.get("language", "en")
                sources.append(WikipediaSource(name=name, language=lang))
        return cls(sources)
