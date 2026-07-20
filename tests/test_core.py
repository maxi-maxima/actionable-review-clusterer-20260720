import json
import unittest

from reviewcluster.core import load_comments, summarize_comments


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


if __name__ == "__main__":
    unittest.main()
