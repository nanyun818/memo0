"""Evaluate the existing keyword retriever on fixed synthetic development data."""

import argparse
import hashlib
import json
from pathlib import Path

from app import lookup

ROOT = Path(__file__).resolve().parent


def evaluate(data, top_k):
    if top_k < 1:
        raise ValueError("top_k 必须大于 0")
    documents = data["documents"]
    ids = {doc["id"] for doc in documents}
    answers = {doc["answer"]: doc["id"] for doc in documents}
    if len(ids) != len(documents) or len(answers) != len(documents):
        raise ValueError("本评测要求文档 ID 和 answer 唯一")
    if not data["cases"] or len({case["id"] for case in data["cases"]}) != len(data["cases"]):
        raise ValueError("用例不能为空且 ID 必须唯一")
    rows = []
    for case in data["cases"]:
        expected = set(case["relevant_ids"])
        if not expected <= ids:
            raise ValueError("标签引用了不存在的文档")
        found = [answers[answer] for answer in lookup(case["question"], documents, top_k)]
        hits = len(expected & set(found))
        rows.append({
            **case, "retrieved_ids": found,
            "recall": hits / len(expected) if expected else None,
            "precision": hits / len(found) if found and expected else (0.0 if expected else None),
            "complete": expected <= set(found) if expected else None,
            "false_retrieval": bool(found) if not expected else None,
        })
    answerable = [row for row in rows if row["recall"] is not None]
    absent = [row for row in rows if row["recall"] is None]
    def mean(items, key):
        return sum(item[key] for item in items) / len(items) if items else None
    return {"dataset_version": data["version"], "top_k": top_k,
            "scope": "retrieval only; synthetic development data; no model API",
            "answerable_count": len(answerable), "unanswerable_count": len(absent),
            "macro_recall": mean(answerable, "recall"),
            "macro_precision": mean(answerable, "precision"),
            "complete_coverage_rate": mean(answerable, "complete"),
            "unanswerable_false_retrieval_rate": mean(absent, "false_retrieval"),
            "cases": rows}


def main():
    parser = argparse.ArgumentParser(description="关键词检索离线评测，无 API 调用")
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--dataset", type=Path, default=ROOT / "datasets" / "retrieval_dev.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = args.dataset.read_bytes()
        report = evaluate(json.loads(raw), args.top_k)
        report["dataset_sha256"] = hashlib.sha256(raw).hexdigest()
        report["retriever_sha256"] = hashlib.sha256((ROOT / "app.py").read_bytes()).hexdigest()
        for row in report["cases"]:
            print(f"{row['id']} [{row['category']}] 期望={row['relevant_ids']} 检索={row['retrieved_ids']}")
        for key in ("macro_recall", "macro_precision", "complete_coverage_rate", "unanswerable_false_retrieval_rate"):
            value = report[key]
            print(f"{key}: {value:.1%}" if value is not None else f"{key}: N/A")
        output = args.output or ROOT / "logs" / "eval" / f"retrieval-k{args.top_k}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"报告已保存：{output}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"评测失败：{error}\n")


if __name__ == "__main__":
    main()
