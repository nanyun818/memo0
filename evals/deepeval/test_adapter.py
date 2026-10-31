"""Offline checks for schema, credentials, request cap and real GEval integration."""
import json
import os
import unittest
from unittest.mock import patch
from pydantic import BaseModel
from lesson import DeepSeekJudge, OfflineJudge, make_metric, make_test, load_cases, parse_verdict


class Verdict(BaseModel):
    score: float
    reason: str


class AdapterTests(unittest.TestCase):
    def test_schema_contract(self):
        value = parse_verdict('{"score": 1, "reason": "有依据"}', Verdict)
        self.assertIsInstance(value, Verdict)
        self.assertEqual(value.score, 1)

    def test_malformed_or_nonbinary_is_error(self):
        for value in ('not json', '[]', '{"score": 0.5,"reason":"x"}', '{"score": true,"reason":"x"}', '{"score": 1,"reason":""}'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_verdict(value, Verdict)

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""})
    @patch("lesson.urlopen")
    def test_missing_key_no_request(self, request):
        with self.assertRaises(RuntimeError):
            DeepSeekJudge().generate("x", Verdict)
        request.assert_not_called()

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-placeholder"})
    @patch("lesson.urlopen")
    def test_request_cap(self, request):
        with self.assertRaises(RuntimeError):
            DeepSeekJudge(max_calls=0).generate("x", Verdict)
        request.assert_not_called()

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-placeholder"})
    @patch("lesson.urlopen")
    def test_payload_and_schema(self, request):
        request.return_value.__enter__.return_value.read.return_value = json.dumps({
            "choices": [{"finish_reason": "stop", "message": {"content": '{"score":0,"reason":"无依据"}'}}],
            "usage": {"total_tokens": 10},
        }).encode()
        judge = DeepSeekJudge(max_calls=1)
        value = judge.generate("sample prompt", Verdict)
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(value.score, 0)
        self.assertEqual(judge.calls, 1)
        self.assertEqual(payload["model"], "deepseek-flash")
        self.assertNotIn("reference_judge_pass", request.call_args.args[0].data.decode())

    @patch("lesson.urlopen", side_effect=TimeoutError())
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-placeholder"})
    def test_failure_does_not_retry(self, request):
        judge = DeepSeekJudge()
        with self.assertRaises(RuntimeError):
            judge.generate("x", Verdict)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(judge.calls, 1)

    @patch("lesson.urlopen", side_effect=AssertionError("Network forbidden in offline test"))
    def test_actual_geval_uses_mock_score_not_reference(self, request):
        judge = OfflineJudge()
        for case in load_cases():
            metric = make_metric(judge)
            metric.measure(make_test(case), _show_indicator=False)
            self.assertEqual(metric.score, 0)
            self.assertFalse(metric.is_successful())
        self.assertEqual(judge.calls, 6)
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
