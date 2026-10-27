"""Offline checks only: no real provider calls, no real credentials."""

import io
import json
import os
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import day2


class DeepSeekClientTests(unittest.TestCase):
    def test_missing_key_prevents_network_call(self):
        with patch.dict(os.environ, {}, clear=True), patch("day2.urlopen") as network:
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                day2.call_deepseek([], day2.DEFAULT_MODEL)
            network.assert_not_called()

    def test_request_and_response_contract(self):
        response = {"model": "test-model", "choices": [{
            "message": {"content": "test-answer"}, "finish_reason": "stop"
        }], "usage": {"prompt_tokens": 10, "completion_tokens": 3}}
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-test-only"}), patch(
            "day2.urlopen", return_value=io.BytesIO(json.dumps(response).encode())
        ) as network:
            result = day2.call_deepseek([{"role": "user", "content": "test"}], "test-model")
        request = network.call_args.args[0]
        self.assertEqual(request.full_url, day2.API_URL)
        self.assertEqual(request.get_header("Authorization"), "Bearer offline-test-only")
        payload = json.loads(request.data)
        self.assertEqual(payload["max_tokens"], 600)
        self.assertEqual(payload["thinking"]["type"], "disabled")
        self.assertFalse(payload["stream"])
        self.assertEqual(result["answer"], "test-answer")
        self.assertEqual(result["usage"]["prompt_tokens"], 10)

    def test_http_errors_do_not_expose_response_body(self):
        for status in (401, 402, 429, 503):
            with self.subTest(status=status):
                error = HTTPError(day2.API_URL, status, "error", {}, io.BytesIO(b"private-body"))
                with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-test-only"}), patch(
                    "day2.urlopen", side_effect=error
                ):
                    with self.assertRaises(ValueError) as raised:
                        day2.call_deepseek([], "test-model")
                self.assertIn(str(status), str(raised.exception))
                self.assertNotIn("private-body", str(raised.exception))
                self.assertNotIn("offline-test-only", str(raised.exception))

    def test_network_error_is_actionable(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "offline-test-only"}), patch(
            "day2.urlopen", side_effect=URLError("test-only")
        ):
            with self.assertRaisesRegex(ValueError, "网络"):
                day2.call_deepseek([], "test-model")

    def test_malformed_responses_are_reported(self):
        for raw in (b"not-json", b"{}", b'{"choices": []}',
                    b'{"choices":[{"message":{"content":null}}]}'):
            with self.subTest(raw=raw), patch.dict(
                os.environ, {"DEEPSEEK_API_KEY": "offline-test-only"}
            ), patch("day2.urlopen", return_value=io.BytesIO(raw)):
                with self.assertRaises(ValueError):
                    day2.call_deepseek([], "test-model")

    def test_dry_run_needs_no_key_and_preserves_retrieval(self):
        config = {"top_k": 1, "knowledge": [{"keywords": ["memory"], "answer": "source"}]}
        args = SimpleNamespace(no_context=False, dry_run=True)
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), patch("day2.urlopen") as network, redirect_stdout(output):
            history = day2.run_question("memory?", config, [], args)
        network.assert_not_called()
        self.assertEqual(history, [])
        self.assertIn("source", output.getvalue())

    def test_chat_history_and_references_are_separate(self):
        history = [{"role": "user", "content": "earlier"},
                   {"role": "assistant", "content": "earlier-answer"}]
        messages = day2.build_messages("question", ["reference"], history, True)
        self.assertEqual(messages[1:3], history)
        user_data = json.loads(messages[-1]["content"])
        self.assertEqual(user_data["reference_documents"], ["reference"])
        self.assertEqual(user_data["question"], "question")


if __name__ == "__main__":
    unittest.main()
