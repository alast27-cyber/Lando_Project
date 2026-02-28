# Lando Project - Offline Chatbot

This repository now includes a **fully offline chatbot** implementation that does not depend on any external API calls.

## Features
- Local rule-based intent matching (greeting, coding, productivity, motivation, farewell)
- Session memory (name capture and topic counters)
- CLI commands:
  - `/help`
  - `/summary`
  - `/time`
  - `quit`
- Deterministic behavior via local RNG seed

## Run the chatbot
```bash
python3 -m Lando_Project.chatbot.app
```

## Run tests
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Notes
- No network calls are used for chat responses.
- Existing autoscaling and monitoring files remain intact.
