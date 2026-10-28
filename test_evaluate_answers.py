import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import evaluate_answers as evaluation


class AnswerEvaluationTests(unittest.TestCase):
    def test_preview_never_calls_provider(self):
        with patch("sys.argv", ["evaluate_answers.py"]), patch.object(evaluation, "call_deepseek") as provider, redirect_stdout(io.StringIO()):
            evaluation.main()
        provider.assert_not_called()

    def test_success_preserves_evidence_and_leaves_scores_pending(self):
        _, cases = evaluation.prepare(2)
        result = {"answer": "offline simulated answer", "model": "offline", "usage": {"prompt_tokens": 12}, "finish_reason": "stop"}
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            with patch.object(evaluation, "call_deepseek", return_value=result) as provider, redirect_stdout(io.StringIO()):
                self.assertTrue(evaluation.run_cases(cases, "offline", directory))
            rows = [json.loads(line) for line in (directory / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 5)
            self.assertEqual(provider.call_count, 5)
            self.assertTrue(all(len(row["messages"]) == 2 for row in rows))
            self.assertIn("待评分", (directory / "review.md").read_text(encoding="utf-8"))
            self.assertEqual(rows[2]["retrieved_ids"], ["langfuse", "mem0"])

    def test_error_retains_prior_results_and_stops_without_retry(self):
        _, cases = evaluation.prepare(1)
        result = {"answer": "offline", "model": "offline", "usage": {}, "finish_reason": "stop"}
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            with patch.object(evaluation, "call_deepseek", side_effect=[result, ValueError("test error")]) as provider, redirect_stdout(io.StringIO()):
                self.assertFalse(evaluation.run_cases(cases, "offline", directory))
            rows = [json.loads(line) for line in (directory / "results.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["status"] for row in rows], ["ok", "error"])
            self.assertEqual(provider.call_count, 2)


if __name__ == "__main__":
    unittest.main()
