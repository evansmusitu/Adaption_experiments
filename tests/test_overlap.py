"""Pure overlap tests: normalize and hash strings, report aggregate counts only."""
import unittest
from proofbench.overlap import analyze


class CrossDatasetTests(unittest.TestCase):
    def test_normalized_overlap_and_intra_duplicates(self):
        datasets = [
            [
                {"enhanced_prompt": " Record cash of USD  10 "},
                {"enhanced_prompt": "record cash of usd 10"},
                {"enhanced_prompt": "opening stock is 20"},
            ],
            [
                {"enhanced_prompt": "RECORD CASH OF USD 10"},
                {"enhanced_prompt": "this is a fresh example"},
            ],
            [{"enhanced_prompt": "opening stock is 20"}, {"enhanced_prompt": "another new one"}],
        ]
        report = analyze(datasets)
        self.assertEqual(report["row_counts"], [3, 2, 2])
        self.assertEqual(report["within_duplicate_rows"], [1, 0, 0])
        self.assertEqual(report["pairwise_shared_unique_prompts"], [[0, 1, 1], [1, 0, 0], [1, 0, 0]])
        self.assertEqual(report["global_unique_prompts"], 4)
        self.assertEqual(report["missing_prompts"], [0, 0, 0])
        self.assertNotIn("Record cash", str(report))
        self.assertNotIn("opening stock", str(report))

    def test_missing_prompt_has_count_but_no_leak(self):
        report = analyze([[{"completion": "a private answer"}], []])
        self.assertEqual(report["missing_prompts"], [1, 0])
        self.assertEqual(report["row_counts"], [1, 0])
        self.assertNotIn("private answer", str(report))

    def test_inputs_are_not_modified(self):
        data = [[{"enhanced_prompt": "same"}], [{"enhanced_prompt": "SAME"}]]
        before = repr(data)
        analyze(data)
        self.assertEqual(repr(data), before)

    def test_empty_datasets(self):
        result = analyze([])
        self.assertEqual(result["row_counts"], [])
        self.assertEqual(result["global_unique_prompts"], 0)


if __name__ == "__main__":
    unittest.main()
