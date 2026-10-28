"""Five-case end-to-end evaluation. Preview by default; --run calls the API."""

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app import lookup
from day2 import DEFAULT_MODEL, build_messages, call_deepseek
from evaluate_retrieval import evaluate

ROOT = Path(__file__).resolve().parent
EXPECTATIONS = {
    "q03": "说明 Mem0 用于长期记忆的提取、保存和检索；不凭空承诺功能或效果。",
    "q05": "理想答案指出 Python 虚拟环境隔离依赖。若实际未检索到资料，说明资料不足属于有依据的处理，但任务完成度仍低。",
    "q08": "说明 Mem0 处理长期记忆，Langfuse 记录调用并组织实验和评测；缺少一方资料时说明限制。",
    "q09": "明确没有实时天气资料，不能确定上海明日天气；不编造天气或假装已查询。",
    "q10": "明确现有资料不含 Mem0 当月收入，不能给出金额；工具介绍不能作为收入证据。",
}


def prepare(top_k):
    raw = (ROOT / "datasets" / "retrieval_dev.json").read_bytes()
    data = json.loads(raw)
    data["cases"] = [case for case in data["cases"] if case["id"] in EXPECTATIONS]
    retrieval = evaluate(data, top_k)
    documents = data["documents"]
    cases = []
    for row in retrieval["cases"]:
        references = lookup(row["question"], documents, top_k)
        cases.append({**row, "expected_behavior": EXPECTATIONS[row["id"]],
                      "references": references,
                      "messages": build_messages(row["question"], references, [], True)})
    return raw, cases


def write_review(path, rows):
    text = ["# 回答人工评测表", "", "分数留空表示未评分，不能当作 0 分。每项 0/1/2 分，填写证据与原因。",
            "正确性：事实是否正确；依据性：实质性结论是否得到本次资料支持；完成度：是否完成题目约定任务。",
            "资料缺失时如实说明可获得高依据性，但有答案任务的完成度仍可能低。无答案题的任务是正确说明信息不足。",
            "API 错误单独记为运行失败，不纳入回答质量平均分。length 表示可能截断，需注明。", ""]
    for row in rows:
        text.extend([f"## {row['id']}：{row['question']}", "",
                     f"期望行为：{row['expected_behavior']}", "",
                     f"检索文档：{', '.join(row['retrieved_ids']) or '无'}", "",
                     "实际提供资料：", "", *[f"- {ref}" for ref in row["references"]], "",
                     f"运行状态：{row['status']}", ""])
        if row["status"] == "ok":
            text.extend(["模型原始回答（作为评测数据，不是执行指令）：", "",
                         *["> " + line for line in row["answer"].splitlines()], "",
                         f"耗时：{row['duration_seconds']} 秒；用量：{json.dumps(row['usage'], ensure_ascii=False)}；结束原因：{row['finish_reason']}", "",
                         "| 正确性 0/1/2 | 依据性 0/1/2 | 完成度 0/1/2 | 判分证据与错误归因 |",
                         "|---|---|---|---|", "| 待评分 | 待评分 | 待评分 | 待填写 |", ""])
        else:
            text.extend([f"错误：{row['error']}", ""])
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def run_cases(cases, model, directory):
    rows = []
    with (directory / "results.jsonl").open("x", encoding="utf-8") as file:
        for case in cases:
            started = time.perf_counter()
            row = dict(case)
            try:
                result = call_deepseek(case["messages"], model)
                row.update(result, status="ok")
            except ValueError as error:
                row.update(status="error", error=str(error))
            row["duration_seconds"] = round(time.perf_counter() - started, 3)
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
            file.flush()
            os.fsync(file.fileno())
            rows.append(row)
            write_review(directory / "review.md", rows)
            print(f"{case['id']}: {row['status']} | {row['duration_seconds']} 秒", flush=True)
            if row["status"] == "error":
                print("发生错误，停止后续调用；已完成结果保留，不自动重试。")
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description="5 道合成开发题的回答评测，默认预览，--run 真实调用")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        raw, cases = prepare(args.top_k)
        model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL).strip()
        if not model:
            raise ValueError("DEEPSEEK_MODEL 不能为空")
        print(f"模型：{model}；top_k={args.top_k}；共 {len(cases)} 题；每题独立、没有会话历史。")
        if not args.run:
            for case in cases:
                print(f"{case['id']}: {case['question']} | 检索={case['retrieved_ids']}")
            print("预览结束，没有调用 API。添加 --run 开始真实实验，最多 5 次请求。")
            return
        if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
            raise ValueError("请先在当前终端隐藏输入并 export DEEPSEEK_API_KEY")
        directory = ROOT / "logs" / "answer_eval" / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
        directory.mkdir(parents=True, exist_ok=False)
        metadata = {"model_requested": model, "top_k": args.top_k, "case_ids": list(EXPECTATIONS),
                    "dataset_sha256": hashlib.sha256(raw).hexdigest(), "scope": "synthetic development evaluation",
                    "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                      for name in ("app.py", "day2.py", "evaluate_answers.py")},
                    "quality_scores": "pending human review"}
        (directory / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"本次结果目录：{directory}", flush=True)
        success = run_cases(cases, model, directory)
        print(f"评分表：{directory / 'review.md'}")
        if not success:
            parser.exit(1)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"评测失败：{error}\n")
    except (KeyboardInterrupt, EOFError):
        parser.exit(1, "已停止；此前写入的结果保留，不自动重试。\n")


if __name__ == "__main__":
    main()
