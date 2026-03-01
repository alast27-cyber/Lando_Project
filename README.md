# Lando Project - Offline/Online Hybrid Chatbot

Lando now supports a hybrid chat runtime:
- **offline cognition** (default)
- optional **online mode** with data-source injection

No paid API integration is required.

## Features
- Local rule-based intent matching + trained intent model
- Session memory (name capture + topic counters)
- Communication cognition modes:
  - `rule-based` (deterministic)
  - `local-llm` (optional local Transformers backend)
- **Online mode commands**:
  - `/online` enable knowledge injection
  - `/offline` disable knowledge injection
  - `/sources` list configured data sources
- Existing commands:
  - `/help`, `/summary`, `/time`, `/mode`, `quit`

## Run chatbot (CLI)
```bash
python3 -m Lando_Project.chatbot.app
```

## Run local AI training
Train/update Lando's offline intent model:
```bash
python3 -m Lando_Project.chatbot.training
```
Model output:
- `Lando_Project/chatbot/intent_model.json`

## Configure data source injection
Data sources are defined in:
- `Lando_Project/chatbot/data_sources.json`

Built-in source types:
- `local_file`: injects matching content from local files
- `wikipedia`: fetches summary context in online mode

Example chat sequence:
```text
/online
/sources
Tell me about autoscaling
```

## Optional local LLM backend (still local)
```bash
pip install transformers torch
python3 -m Lando_Project.chatbot.app
```
Check current cognition mode with:
```text
/mode
```

## Browser interface
Open `index.html` (or deploy on Vercel) to use:
- enhanced chat bubbles
- quick command/topic chips
- mode switcher (`rule-based` / `local-llm-lite`)
- typing indicator

## Run tests
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Vercel deployment
- Entrypoint: `index.html`
- Rewrites: configured in `vercel.json` so all routes resolve to `index.html`
