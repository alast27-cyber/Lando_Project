# Lando Project - Offline Chatbot

This repository includes a **fully offline chatbot** that can run in CLI or browser mode without external API calls.

## Features
- Local rule-based intent matching (greeting, coding, productivity, motivation, farewell)
- Session memory (name capture and topic counters)
- **Communication cognition modes**:
  - `rule-based` (default, deterministic)
  - `local-llm` (Python optional backend using local Transformers model if available)
- CLI commands:
  - `/help`
  - `/summary`
  - `/time`
  - `/mode`
  - `quit`

## Run the chatbot (CLI)
```bash
python3 -m Lando_Project.chatbot.app
```

## Optional local LLM backend (still offline)
`OfflineChatbot` auto-attempts local Transformers loading (`distilgpt2`) and silently falls back to rule-based mode if dependencies or model are unavailable.

If you want true local LLM cognition in CLI:
```bash
pip install transformers torch
python3 -m Lando_Project.chatbot.app
```

Then check mode inside chat:
```text
/mode
```

## Browser interface
Open `index.html` (or deploy on Vercel) to use:
- Enhanced chat bubbles
- Quick command/topic chips
- Mode switcher (`rule-based` / `local-llm-lite`)
- Typing indicator

## Run tests
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Vercel deployment
This repository includes a static `index.html` + `vercel.json` setup so deployments do not return `404: NOT_FOUND`.

- Vercel entrypoint: `index.html`
- Universal rewrite: all paths route to `index.html`
- Chat runs fully in-browser (no API calls)
