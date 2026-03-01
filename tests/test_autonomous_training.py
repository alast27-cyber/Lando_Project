import tempfile
import unittest
from pathlib import Path

from Lando_Project.chatbot.autonomous_training import AutonomousIAIIPSTrainer


class AutonomousTrainingTests(unittest.TestCase):
    def test_manual_train_once_updates_model_after_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            model_path = td_path / "intent_model.json"
            events_path = td_path / "events.json"
            trainer = AutonomousIAIIPSTrainer(
                model_path=model_path,
                events_path=events_path,
                interval_s=999,
                min_events_to_train=2,
            )
            trainer.record("debug python code", "coding")
            trainer.record("hello there", "greeting")
            self.assertTrue(trainer.train_once())
            self.assertTrue(model_path.exists())

    def test_status_reports_runtime_fields(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            trainer = AutonomousIAIIPSTrainer(
                model_path=td_path / "m.json",
                events_path=td_path / "e.json",
            )
            st = trainer.status()
            self.assertIn("trainer=running", st)
            self.assertIn("events:", st)


if __name__ == "__main__":
    unittest.main()
