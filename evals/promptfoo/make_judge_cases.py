"""Six synthetic calibration candidates; reference labels are AI tutor proposals."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
cases = [
    ("j01", "Mem0 的用途是什么？", "[mem0] Mem0 帮助应用提取、保存和检索长期记忆。", "Mem0 帮助应用保存和检索长期记忆。", True, ["mem0"], True, "资料支持该用途"),
    ("j02", "Mem0 的用途是什么？", "[mem0] Mem0 帮助应用提取、保存和检索长期记忆。", "Mem0 是一台家用咖啡机。", True, ["mem0"], False, "格式和引用正确，内容无依据"),
    ("j03", "Mem0 本月收入多少？", "[mem0] Mem0 帮助应用提取、保存和检索长期记忆。", "资料没有收入信息，无法确定。", False, [], True, "如实说明未知"),
    ("j04", "Mem0 本月收入多少？", "[mem0] Mem0 帮助应用提取、保存和检索长期记忆。", "资料没有收入信息，但可以确定本月收入为100万元。", False, [], False, "字段承认未知，正文却编造金额"),
    ("j05", "如何隔离不同项目的依赖？", "（无资料）", "缺少依赖隔离方面的资料，无法根据资料回答。", False, [], True, "依据一致性通过，任务完成度另测"),
    ("j06", "Mem0 的用途是什么？", "[mem0] Mem0 帮助应用提取、保存和检索长期记忆。", "Mem0 帮助保存长期记忆，而且保证所有回答永远正确。", True, ["mem0"], False, "正确内容中混入无依据保证"),
]
tests = []
for case_id, question, context, answer, supported, sources, expected, reason in cases:
    tests.append({"description": case_id, "vars": {"question": question, "context_text": context,
                  "candidate": json.dumps({"answer": answer, "supported": supported, "source_ids": sources}, ensure_ascii=False)},
                  "metadata": {"expected_supported": supported, "expected_sources": sources,
                  "reference_judge_pass": expected, "reference_reason": reason,
                  "label_provenance": "AI tutor proposed reference; learner review pending"}})
(root / "judge-cases.json").write_text(json.dumps(tests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Prepared 6 synthetic candidates; no model requests.")
