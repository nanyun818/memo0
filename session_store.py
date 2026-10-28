"""Small single-process session store for the learning CLI (no API calls)."""

import json
import os
import re
import tempfile
from pathlib import Path


MAX_TURNS = 20


def session_path(root, session_id):
    # IDs are names, not paths. Keep every session in the intended directory.
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", session_id):
        raise ValueError("会话名称只能包含英文字母、数字、下划线和短横线，长度 1–40。")
    return Path(root) / "logs" / "sessions" / f"{session_id}.json"


def validate_history(history):
    if not isinstance(history, list) or len(history) % 2 or len(history) > MAX_TURNS * 2:
        raise ValueError("会话文件必须包含完整问答，最多 20 轮；请保留原文件并检查。")
    for index, message in enumerate(history):
        role = "user" if index % 2 == 0 else "assistant"
        if (not isinstance(message, dict) or set(message) != {"role", "content"}
                or message["role"] != role or not isinstance(message["content"], str)
                or not message["content"].strip()):
            raise ValueError("会话消息格式不正确；请保留原文件并检查。")
    return history


def load_session(path):
    try:
        with path.open(encoding="utf-8") as file:
            return validate_history(json.load(file))
    except FileNotFoundError:
        return []  # A previously unused ID starts a new conversation.
    except (json.JSONDecodeError, UnicodeError):
        raise ValueError("会话文件无法解析；不会自动清空或覆盖，请检查文件。") from None


def save_session(path, history):
    validate_history(history)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace only after a complete write; a failed write preserves the old file.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as file:
            temporary = Path(file.name)
            json.dump(history, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
