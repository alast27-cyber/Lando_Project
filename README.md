# Lando Project - Offline/Online Hybrid Chatbot

Lando now supports a hybrid runtime with:
- offline cognition (default)
- optional online knowledge injection
- autonomous background IAI-IPS training

## Features
- Local rule-based intent matching + trained intent model
- Session memory (name capture + topic counters)
- Communication cognition modes:
  - `rule-based`
  - `local-llm` (optional local Transformers backend)
- Online mode commands:
  - `/online`, `/offline`, `/sources`
- Trainer commands:
  - `/trainer` status
  - `/train-now` trigger immediate training cycle
- Existing commands:
  - `/help`, `/summary`, `/time`, `/mode`, `quit`

## Run chatbot (CLI)
```bash
python3 -m Lando_Project.chatbot.app
```

## Autonomous IAI-IPS training
Lando continuously records intent-labeled events and retrains in the background.

Artifacts:
- model: `Lando_Project/chatbot/intent_model.json`
- events log: `Lando_Project/chatbot/iai_ips_events.json`

Manual training:
```bash
python3 -m Lando_Project.chatbot.training
```

In-chat controls:
```text
/trainer
/train-now
```

## Configure data source injection
Data sources config:
- `Lando_Project/chatbot/data_sources.json`

Built-in source types:
- `local_file`
- `wikipedia`

Example:
```text
/online
/sources
Tell me about autoscaling
```

## Browser interface
Open `index.html` (or deploy on Vercel) to use a minimalistic UI with:
- compact message panel
- quick chips
- mode toggle
- online knowledge commands
- dedicated training page (`training.html`) for progress, data sources, and ETA


## IAI Training Kernel Prototype (Python)
A local-first three-layer kernel is available at:
- `Lando_Project/chatbot/iai_kernel.py`

It implements:
- Reflex map responses (lowest energy path)
- Instinct retrieval from learned memory (TF-IDF cosine similarity with fallback)
- Cognition fallback generation for unseen queries
- Compile-down behavior (new cognition answers are stored as instinct memory)
- JSON persistence for saving/loading memory state
- Bounded memory and duplicate-query compile-down handling

Quick example:
```python
from Lando_Project.chatbot import IAIKernel

k = IAIKernel()
print(k.respond("hello"))
print(k.respond("How do I tune an HPA?"))
print(k.respond("How do I tune an HPA?"))
```

## Advanced CLL Training (PEFT + LoRA)
For Layer-3 Cognition (CLL), the repo includes a prototype LoRA fine-tuning module:
- `Lando_Project/chatbot/cll_lora_training.py`

Why LoRA for CLL:
- train only lightweight adapter weights instead of full-model updates
- adapter artifacts are much smaller than full checkpoints
- export path is aligned with local/browser loading workflows

Expected dataset format (`.jsonl`):
```json
{"prompt": "Complex state query not solved by reflex/instinct", "response": "Desired CLL answer"}
```

Run prototype training:
```bash
python3 -m Lando_Project.chatbot.cll_lora_training path/to/complex_states.jsonl
```

Notes:
- dependencies are optional and loaded lazily (`unsloth`, `trl`, `transformers`, `datasets`, `peft`)
- module exports GGUF with `q4_k_m` quantization for lightweight local deployment
- recommended workflow: collect Layer1/2 failures -> SFT with LoRA -> export GGUF -> store/load via local-first runtime

## Run tests
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Vercel deployment
- Entrypoint: `index.html`
- Rewrites: `vercel.json` routes all paths to `index.html`


## WebGPU Local-First IAI Blueprint
A browser-first architecture blueprint and boilerplate are provided under:
- `Lando_Project/web/README_IAI_WEBGPU.md`
- `Lando_Project/web/iai-kernel.js`
- `Lando_Project/web/service-worker.js`
- `Lando_Project/web/opfs-store.js`
- `Lando_Project/web/data-ingestion-worker.js`
- `Lando_Project/web/main.js`

This package implements:
- Energy Minimization Driver-based layer selection (IRL -> ILL -> CLL)
- Service Worker persistence hooks for background training/sync
- OPFS storage initialization for model/tensor persistence
- Worker-based data ingestion pipeline for autonomous knowledge injection


### Vercel root-directory compatibility
This repo includes deployment entry files in both:
- repo root (`index.html`, `training.html`, `vercel.json`)
- `Lando_Project/` subfolder (`Lando_Project/index.html`, `Lando_Project/training.html`, `Lando_Project/vercel.json`)

So Vercel works whether project root is configured as `/` or `Lando_Project/`.
