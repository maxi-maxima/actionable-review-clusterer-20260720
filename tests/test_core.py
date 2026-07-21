import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reviewcluster.core import load_comments, summarize_comments, to_json_summary


class ReviewClusterTests(unittest.TestCase):
    def test_clusters_common_review_themes(self):
        comments = load_comments(json.dumps([
            {"file": "app.py", "line": 1, "body": "Add a test for this branch"},
            {"file": "app.py", "line": 2, "body": "This could leak a token"},
            {"file": "docs.md", "line": 3, "body": "Update README wording"},
        ]))
        report = summarize_comments(comments)
        self.assertIn("Tests (1)", report)
        self.assertIn("Security (1)", report)
        self.assertIn("Docs (1)", report)
        self.assertIn("app.py: tests", report)

    def test_json_summary_includes_priority_and_owner_suggestions(self):
        comments = load_comments(json.dumps([
            {"file": "auth.py", "line": "10", "body": "Auth token can leak"},
            {"file": "auth.py", "line": 12, "body": "Add regression test"},
            {"file": "ui.py", "line": 3, "body": "Fix typo in comment"},
        ]))
        summary = to_json_summary(comments)
        self.assertEqual(summary["bucket_order"][0], "security")
        self.assertEqual(summary["owners_by_file"], {"auth.py": "security", "ui.py": "docs"})
        self.assertEqual(summary["buckets"]["security"]["priority"], "P0")
        self.assertEqual(summary["buckets"]["security"]["comments"][0]["line"], 10)


if __name__ == "__main__":
    unittest.main()
