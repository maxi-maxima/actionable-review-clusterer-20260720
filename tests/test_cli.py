import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, 'PYTHONPATH': str(ROOT / 'src')}


class ReviewClusterCliTests(unittest.TestCase):
    def test_cli_json_output(self):
        payload = json.dumps([{'file': 'a.py', 'line': 4, 'body': 'Add a regression test'}])
        proc = subprocess.run([sys.executable, '-m', 'reviewcluster', '--json'], input=payload, text=True, capture_output=True, cwd=ROOT, env=ENV, check=True)
        self.assertIn('"total_comments": 1', proc.stdout)


if __name__ == '__main__':
    unittest.main()
