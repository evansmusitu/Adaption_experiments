"""Guard the public submission checklist from contradicted provider evidence."""
import unittest
from pathlib import Path


class SubmissionReadinessDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Path("docs/HACKATHON_SUBMISSION.md").read_text(encoding="utf-8")

    def test_review_export_recorded_with_both_actual_hashes(self):
        self.assertNotIn("Improved export: still unavailable", self.page)
        self.assertIn("46f3ddb18efa5869b8dcd0b01839d1056397b3f14f690779c2faa1562a2a0c6b", self.page)
        self.assertIn("7127b6f681392ed43e63093ec371254c486c4e442f62d918d20944669dbeadb1", self.page)

    def test_review_candidate_does_not_inherit_provider_grade(self):
        self.assertIn("15 exact", self.page)
        self.assertIn("85", self.page)
        self.assertIn("no Adaption grade", self.page)
        self.assertIn("redistribution", self.page)

    def test_demo_state_is_tracked_without_claiming_video_submission(self):
        self.assertIn("demo/index.html", self.page)
        self.assertIn("not recorded", self.page)
        self.assertIn("Not submitted", self.page)


if __name__ == "__main__":
    unittest.main()
