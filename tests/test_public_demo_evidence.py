"""Public demo claims must match the verified Adaption evidence and limitations."""
from __future__ import annotations

import unittest
from pathlib import Path


class PublicDemoEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Path("demo/index.html").read_text(encoding="utf-8")

    def test_observed_native_quality_and_run_are_explained(self):
        self.assertIn("100/100", self.page)
        self.assertIn("7/10", self.page)
        self.assertIn("9/10", self.page)
        self.assertIn("28.6%", self.page)
        self.assertIn("VERIFIED_ADAPTION_PILOT.md", self.page)

    def test_provider_quality_not_mistaken_for_model_accuracy(self):
        self.assertIn("provider-native", self.page.lower())
        self.assertIn("not trained-model accuracy", self.page.lower())
        self.assertIn("14", self.page)
        self.assertIn("four", self.page.lower())
        self.assertIn("candidate has no adaption grade", self.page.lower())

    def test_no_outdated_unlaunched_language_or_external_script(self):
        self.assertNotIn("improvement caused by Adaption. Real Adaption run identifiers", self.page)
        self.assertNotIn("<script src=", self.page)
        self.assertIn("offline", self.page.lower())


if __name__ == "__main__":
    unittest.main()
