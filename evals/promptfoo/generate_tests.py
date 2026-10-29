"""Freeze the existing k=2 retrieval into a prompt-comparison development set."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from app import lookup

raw = (ROOT / "datasets" / "retrieval_dev.json").read_bytes()
data = json.loads(raw)
by_answer = {doc["answer"]: doc["id"] for doc in data["documents"]}
labels = {"q03": ["mem0"], "q05": [], "q08": ["mem0", "langfuse"], "q09": [], "q10": []}
tests = []
for case in data["cases"]:
    if case["id"] not in labels:
        continue
    references = lookup(case["question"], data["documents"], 2)
    tests.append({"description": f"{case['id']} {case['category']}", "vars": {
        "question": case["question"],
        "context_text": "\n".join(f"[{by_answer[text]}] {text}" for text in references) or "（无资料）"
    }, "metadata": {"source_case_id": case["id"], "retrieval_top_k": 2,
                    "expected_supported": bool(labels[case["id"]]), "expected_sources": labels[case["id"]],
                    "dataset_sha256": hashlib.sha256(raw).hexdigest(), "provenance": "synthetic development data"}})
(HERE / "tests.json").write_text(json.dumps(tests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(tests)} tests; no API calls. Expected labels are not included in prompts.")
