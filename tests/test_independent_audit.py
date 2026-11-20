"""Independent answer-key audit tests; no call to the generator's oracle formulas."""
import copy
import unittest
from proofbench.benchmark import make_cases
from proofbench.independent_audit import audit_cases, verify_case


class IndependentAuditTests(unittest.TestCase):
    def test_covers_all_split_cases(self):
        cases = (
            make_cases("train", pairs_per_family=20)
            + make_cases("dev", pairs_per_family=10)
            + make_cases("stress", pairs_per_family=8)
        )
        report = audit_cases(cases)
        self.assertEqual(report["checked"], 456)
        self.assertEqual(report["failures"], 0)
        self.assertEqual(report["families_checked"], 6)

    def test_tampered_numeric_label_is_caught(self):
        row = next(
            x for x in make_cases("dev", 2)
            if x["gold"]["kind"] == "numeric" and x["gold"]["unit"] == "USD"
        )
        altered = copy.deepcopy(row)
        altered["gold"]["value"] = "999999.99"
        self.assertFalse(verify_case(altered))
        self.assertEqual(audit_cases([altered])["failures"], 1)

    def test_unjustified_clarification_is_caught(self):
        row = next(
            x for x in make_cases("stress", 2)
            if x["gold"]["kind"] == "numeric"
        )
        altered = copy.deepcopy(row)
        altered["gold"].update({"kind": "clarify", "value": None})
        self.assertFalse(verify_case(altered))

    def test_false_numeric_answer_when_rate_missing_is_caught(self):
        row = next(
            x for x in make_cases("dev", 2)
            if x["family"] == "fx_missing" and x["gold"]["kind"] == "clarify"
        )
        altered = copy.deepcopy(row)
        altered["gold"].update({"kind": "numeric", "value": "250"})
        self.assertFalse(verify_case(altered))


if __name__ == "__main__":
    unittest.main()
