import json
import tempfile
import unittest
from pathlib import Path

from Lando_Project.chatbot.engine import OfflineChatbot
from Lando_Project.chatbot.training import run_training


class OfflineChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_training()

    def test_greeting_intent(self):
        bot = OfflineChatbot(seed=1, use_llm=False)
        response = bot.respond("hello")
        self.assertTrue(
            "hello" in response.lower()
            or "hi" in response.lower()
            or "hey" in response.lower()
        )

    def test_name_capture_and_summary(self):
        bot = OfflineChatbot(seed=1, use_llm=False)
        bot.respond("my name is Alex")
        summary = bot.respond("/summary")
        self.assertIn("Alex", summary)

    def test_coding_intent(self):
        bot = OfflineChatbot(seed=1, use_llm=False)
        response = bot.respond("I need to debug this python bug")
        self.assertTrue(
            "debug" in response.lower()
            or "test" in response.lower()
            or "coding" in response.lower()
        )

    def test_mode_command_available(self):
        bot = OfflineChatbot(seed=1, use_llm=False)
        response = bot.respond("/mode")
        self.assertIn("rule-based", response)

    def test_trained_intent_model_assists_matching(self):
        bot = OfflineChatbot(seed=1, use_llm=False)
        response = bot.respond("there is a software issue in my app")
        self.assertTrue(
            "debug" in response.lower()
            or "test" in response.lower()
            or "refactor" in response.lower()
        )

    def test_online_mode_injects_data_source_context(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            doc_path = td_path / "notes.txt"
            doc_path.write_text("Lando knows Kubernetes autoscaling and HPA tuning best practices.")
            cfg_path = td_path / "sources.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "type": "local_file",
                                "name": "notes",
                                "path": str(doc_path),
                            }
                        ]
                    }
                )
            )

            bot = OfflineChatbot(seed=1, use_llm=False, data_sources_config=cfg_path)
            self.assertIn("enabled", bot.respond("/online").lower())
            self.assertIn("notes", bot.respond("/sources").lower())
            out = bot.respond("Tell me about autoscaling")
            self.assertIn("[Injected knowledge]", out)
            self.assertIn("notes:", out)


if __name__ == "__main__":
    unittest.main()
