import tempfile
import unittest
from pathlib import Path

from tools.verify_architecture import ADR_HEADINGS, review


class ArchitecturePackageTests(unittest.TestCase):
    def test_repository_package(self):
        self.assertEqual(review(), [])

    def test_reports_missing_documents_and_adr_headings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs/adrs").mkdir(parents=True)
            (root / "docs/adrs/0001-example.md").write_text("## Context\n", encoding="utf-8")
            failures = review(root)
            self.assertTrue(any("Missing required document" in x for x in failures))
            self.assertTrue(any("missing ## Decision" in x for x in failures))
            self.assertEqual(len(ADR_HEADINGS), 6)


if __name__ == "__main__":
    unittest.main()
