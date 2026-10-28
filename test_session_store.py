"""Offline persistence checks: provider responses are simulated, never billed."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import day2
from session_store import load_session, save_session, session_path


class SessionTests(unittest.TestCase):
    def test_restart_restores_messages_and_new_session_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {"assistant_name": "test", "top_k": 1, "knowledge": []}
            result = {"answer": "示例答案", "model": "offline", "usage": {}, "finish_reason": "stop"}
            with patch.object(day2, "ROOT", root), patch.object(day2, "load_config", return_value=config), patch.dict(
                os.environ, {"DEEPSEEK_API_KEY": "offline-test-only"}
            ), patch.object(day2, "call_deepseek", return_value=result) as provider, redirect_stdout(io.StringIO()):
                for session, question in (("whale", "代号是蓝鲸"), ("whale", "代号是什么？"), ("fresh", "代号是什么？")):
                    with patch("sys.argv", ["day2.py", "--chat", "--no-context", "--session", session]), patch(
                        "builtins.input", side_effect=[question, "/exit"]
                    ):
                        day2.main()  # Independent main() runs share only saved files.
            requests = [call.args[0] for call in provider.call_args_list]
            self.assertEqual([len(messages) for messages in requests], [2, 4, 2])
            self.assertEqual(json.loads(requests[1][1]["content"])["question"], "代号是蓝鲸")
            self.assertEqual(requests[1][2]["content"], "示例答案")
            self.assertEqual(len(load_session(session_path(root, "whale"))), 4)

    def test_invalid_ids_cannot_escape_session_directory(self):
        for name in ("../x", "/tmp/x", "a/b", "", "a" * 41):
            with self.subTest(name=name), self.assertRaises(ValueError):
                session_path(Path("."), name)

    def test_corrupt_history_is_not_silently_discarded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            for content in ("broken", '[{"role":"system","content":"x"}]', '{}',
                            '[{"role":"assistant","content":"x"},{"role":"user","content":"y"}]'):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_session(path)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_failed_replace_keeps_previous_history(self):
        history = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
        with tempfile.TemporaryDirectory() as directory:
            path = session_path(Path(directory), "whale")
            save_session(path, history)
            with patch("session_store.os.replace", side_effect=OSError("offline failure")), self.assertRaises(OSError):
                save_session(path, history * 2)
            self.assertEqual(load_session(path), history)
            self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_limit_rejects_oversize_history(self):
        history = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}] * 21
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            save_session(session_path(Path(directory), "whale"), history)


if __name__ == "__main__":
    unittest.main()
