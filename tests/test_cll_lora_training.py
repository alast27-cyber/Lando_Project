import json
import tempfile
import unittest
from pathlib import Path

from Lando_Project.chatbot.cll_lora_training import (
    LoRAConfig,
    PrototypeTrainingConfig,
    load_complex_state_dataset,
    to_sft_text_samples,
)


class CLLLoRATrainingTests(unittest.TestCase):
    def test_dataset_loader_filters_invalid_rows(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "complex.jsonl"
            p.write_text(
                "\n".join(
                    [
                        json.dumps({"prompt": "p1", "response": "r1"}),
                        json.dumps({"prompt": "", "response": "r2"}),
                        json.dumps({"prompt": "p3", "response": ""}),
                    ]
                )
            )
            rows = load_complex_state_dataset(p)
            self.assertEqual(rows, [{"prompt": "p1", "response": "r1"}])

    def test_sft_format_contains_role_tokens(self):
        samples = to_sft_text_samples([{"prompt": "What is HPA drift?", "response": "Use metrics."}])
        self.assertEqual(len(samples), 1)
        text = samples[0]["text"]
        self.assertIn("<|system|>", text)
        self.assertIn("<|user|>", text)
        self.assertIn("<|assistant|>", text)

    def test_config_defaults_are_browser_export_friendly(self):
        cfg = PrototypeTrainingConfig()
        lora = LoRAConfig()
        self.assertEqual(cfg.gguf_quantization_method, "q4_k_m")
        self.assertGreater(cfg.max_steps, 0)
        self.assertGreater(lora.r, 0)


if __name__ == "__main__":
    unittest.main()
