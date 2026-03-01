import tempfile
import unittest
from pathlib import Path

from Lando_Project.chatbot.iai_kernel import IAIKernel


class IAIKernelTests(unittest.TestCase):
    def test_reflex_routing(self):
        kernel = IAIKernel(reflex_map={"hello": "hi reflex"})
        out = kernel.respond("hello there")
        self.assertEqual(out["layer"], "reflex")
        self.assertEqual(out["answer"], "hi reflex")

    def test_cognition_then_instinct_reuse(self):
        kernel = IAIKernel(reflex_map={})
        first = kernel.respond("How do I optimize kubernetes autoscaling?")
        self.assertEqual(first["layer"], "cognition")

        second = kernel.respond("How do I optimize kubernetes autoscaling?")
        self.assertEqual(second["layer"], "instinct")

    def test_memory_persistence(self):
        kernel = IAIKernel(reflex_map={})
        kernel.respond("first novel query")

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "memory.json"
            kernel.save_memory(p)

            restored = IAIKernel(reflex_map={})
            restored.load_memory(p)
            self.assertEqual(restored.memory_size, 1)

    def test_repeated_cognition_does_not_duplicate_memory(self):
        kernel = IAIKernel(reflex_map={}, instinct_threshold=1.1)
        kernel.respond("repeat me")
        kernel.respond("repeat me")
        self.assertEqual(kernel.memory_size, 1)

    def test_memory_cap_is_enforced(self):
        kernel = IAIKernel(reflex_map={}, max_memory_items=2)
        kernel.respond("q1")
        kernel.respond("q2")
        kernel.respond("q3")
        self.assertEqual(kernel.memory_size, 2)


if __name__ == "__main__":
    unittest.main()
