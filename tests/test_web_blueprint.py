import json
import unittest
from pathlib import Path


class WebBlueprintArtifactTests(unittest.TestCase):
    def test_blueprint_files_exist(self):
        base = Path('Lando_Project/web')
        expected = [
            'README_IAI_WEBGPU.md',
            'iai-kernel.js',
            'service-worker.js',
            'opfs-store.js',
            'data-ingestion-worker.js',
            'main.js',
        ]
        for name in expected:
            self.assertTrue((base / name).exists(), f'missing {name}')

    def test_mermaid_diagram_present(self):
        doc = Path('Lando_Project/web/README_IAI_WEBGPU.md').read_text()
        self.assertIn('```mermaid', doc)
        self.assertIn('Energy Minimization Driver', doc)


if __name__ == '__main__':
    unittest.main()
