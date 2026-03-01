"""CLL (Cognition Layer) LoRA/PEFT training helpers.

This module provides a practical prototype workflow for fine-tuning a local
cognition model with PEFT + LoRA using Unsloth and TRL.

Design goals:
- Keep core logic importable even when heavy ML deps are absent.
- Provide small, testable helpers for dataset formatting and config.
- Expose a single `run_prototype_training` entrypoint for script usage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


@dataclass
class LoRAConfig:
    """LoRA adapter parameters for CLL training."""

    r: int = 16
    target_modules: Sequence[str] = ("q_proj", "k_proj", "v_proj", "o_proj")
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    bias: str = "none"


@dataclass
class PrototypeTrainingConfig:
    """Prototype training configuration for fast local experimentation."""

    model_name: str = "unsloth/llama-3-8b-bnb-4bit"
    max_seq_length: int = 2048
    load_in_4bit: bool = True
    output_dir: str = "outputs"
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 5
    max_steps: int = 60
    learning_rate: float = 2e-4
    logging_steps: int = 1
    dataset_text_field: str = "text"
    gguf_output_dir: str = "model_for_web"
    gguf_quantization_method: str = "q4_k_m"


def _import_training_stack() -> Dict[str, Any]:
    """Import heavy training dependencies lazily."""
    try:
        import torch  # type: ignore
        from transformers import TrainingArguments  # type: ignore
        from trl import SFTTrainer  # type: ignore
        from unsloth import FastLanguageModel  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Missing optional deps for CLL LoRA training. "
            "Install with: pip install unsloth trl transformers datasets peft"
        ) from exc

    return {
        "torch": torch,
        "TrainingArguments": TrainingArguments,
        "SFTTrainer": SFTTrainer,
        "FastLanguageModel": FastLanguageModel,
    }


def load_complex_state_dataset(path: Path) -> List[Dict[str, str]]:
    """Load JSONL dataset containing complex-state samples.

    Each line must include:
    - `prompt`: user/system context for an unsolved Layer1/Layer2 case
    - `response`: desired cognition-layer answer
    """
    rows: List[Dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        prompt = str(item.get("prompt", "")).strip()
        response = str(item.get("response", "")).strip()
        if prompt and response:
            rows.append({"prompt": prompt, "response": response})
    return rows


def to_sft_text_samples(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert prompt/response rows into SFT plain-text records."""
    out: List[Dict[str, str]] = []
    for row in rows:
        prompt = row["prompt"].strip()
        response = row["response"].strip()
        text = (
            "<|system|>You are Lando CLL, solving complex queries after reflex/instinct fail.</s>"
            f"<|user|>{prompt}</s>"
            f"<|assistant|>{response}</s>"
        )
        out.append({"text": text})
    return out


def run_prototype_training(
    dataset_path: Path,
    config: PrototypeTrainingConfig | None = None,
    lora: LoRAConfig | None = None,
) -> Dict[str, Any]:
    """Execute prototype CLL LoRA training and export GGUF artifacts."""
    cfg = config or PrototypeTrainingConfig()
    lcfg = lora or LoRAConfig()

    deps = _import_training_stack()
    torch = deps["torch"]
    TrainingArguments = deps["TrainingArguments"]
    SFTTrainer = deps["SFTTrainer"]
    FastLanguageModel = deps["FastLanguageModel"]

    rows = load_complex_state_dataset(dataset_path)
    samples = to_sft_text_samples(rows)
    if not samples:
        raise ValueError("Dataset is empty after filtering; provide prompt/response rows.")

    from datasets import Dataset  # type: ignore

    train_dataset = Dataset.from_list(samples)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg.model_name,
        max_seq_length=cfg.max_seq_length,
        load_in_4bit=cfg.load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=lcfg.r,
        target_modules=list(lcfg.target_modules),
        lora_alpha=lcfg.lora_alpha,
        lora_dropout=lcfg.lora_dropout,
        bias=lcfg.bias,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        dataset_text_field=cfg.dataset_text_field,
        max_seq_length=cfg.max_seq_length,
        args=TrainingArguments(
            per_device_train_batch_size=cfg.per_device_train_batch_size,
            gradient_accumulation_steps=cfg.gradient_accumulation_steps,
            warmup_steps=cfg.warmup_steps,
            max_steps=cfg.max_steps,
            learning_rate=cfg.learning_rate,
            fp16=not torch.cuda.is_bf16_supported(),
            logging_steps=cfg.logging_steps,
            output_dir=cfg.output_dir,
        ),
    )

    train_stats = trainer.train()
    model.save_pretrained_gguf(
        cfg.gguf_output_dir,
        tokenizer,
        quantization_method=cfg.gguf_quantization_method,
    )

    return {
        "rows": len(rows),
        "output_dir": cfg.output_dir,
        "gguf_output_dir": cfg.gguf_output_dir,
        "train_runtime": getattr(train_stats, "metrics", {}).get("train_runtime"),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prototype CLL LoRA trainer (Unsloth + TRL)")
    parser.add_argument("dataset", type=Path, help="Path to JSONL with prompt/response rows")
    args = parser.parse_args()

    result = run_prototype_training(args.dataset)
    print(json.dumps(result, indent=2))
