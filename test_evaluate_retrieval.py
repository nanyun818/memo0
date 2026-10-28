import unittest

from evaluate_retrieval import evaluate


class RetrievalMetricTests(unittest.TestCase):
    def test_partial_coverage_and_irrelevant_result(self):
        data = {"version": "test", "documents": [
            {"id": "a", "keywords": ["hit"], "answer": "a"},
            {"id": "b", "keywords": ["hit"], "answer": "b"},
            {"id": "c", "keywords": ["miss"], "answer": "c"}],
            "cases": [{"id": "1", "question": "hit", "relevant_ids": ["a", "c"]},
                      {"id": "2", "question": "hit", "relevant_ids": []}]}
        report = evaluate(data, 2)
        self.assertEqual(report["macro_recall"], 0.5)
        self.assertEqual(report["macro_precision"], 0.5)
        self.assertEqual(report["complete_coverage_rate"], 0)
        self.assertEqual(report["unanswerable_false_retrieval_rate"], 1)

    def test_absent_denominators_are_not_reported_as_perfect(self):
        data = {"version": "test", "documents": [],
                "cases": [{"id": "1", "question": "x", "relevant_ids": []}]}
        report = evaluate(data, 1)
        self.assertIsNone(report["macro_recall"])
        self.assertIsNone(report["macro_precision"])
        self.assertEqual(report["unanswerable_false_retrieval_rate"], 0)


if __name__ == "__main__":
    unittest.main()
