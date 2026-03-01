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


    def test_vercel_root_compatibility_files_exist(self):
        self.assertTrue(Path('index.html').exists())
        self.assertTrue(Path('training.html').exists())
        self.assertTrue(Path('vercel.json').exists())
        self.assertTrue(Path('Lando_Project/index.html').exists())
        self.assertTrue(Path('Lando_Project/training.html').exists())
        self.assertTrue(Path('Lando_Project/vercel.json').exists())

    def test_training_page_exists_and_is_linked(self):
        training = Path('training.html')
        index = Path('index.html').read_text()
        self.assertTrue(training.exists())
        self.assertIn('/training.html', index)


if __name__ == '__main__':
    unittest.main()
