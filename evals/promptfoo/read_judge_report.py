"""Compare judge verdicts with proposed reference labels; never infer missing scores."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
files = list((root / "results").glob("judge-*.json"))
if not files:
    raise SystemExit("还没有 judge 实验结果，请先运行 npm run judge。")
path = max(files, key=lambda p: p.stat().st_mtime)
data = json.loads(path.read_text(encoding="utf-8"))
rows = data["results"]["results"]
matched = valid = 0
print("结果文件：", path.name)
for row in rows:
    case = row["testCase"]
    components = (row.get("gradingResult") or {}).get("componentResults", [])
    judge = next((item for item in components if (item.get("assertion") or {}).get("type") == "llm-rubric"), None)
    expected = case["metadata"]["reference_judge_pass"]
    # API or parsing errors are distinct from a semantic FAIL verdict.
    if judge is None or judge.get("error") or not isinstance(judge.get("pass"), bool) or judge.get("score") not in (0, 1) or row.get("failureReason") == 2:
        print(case["description"], "裁判错误或无有效二值判分，请在网页查看详情；不计为有效判分")
        continue
    actual = judge["pass"]
    valid += 1
    matched += actual == expected
    print(f"{case['description']} | 裁判={'通过' if actual else '不通过'} | 助教参考={'通过' if expected else '不通过'} | {'一致' if actual == expected else '有分歧'}")
    print("理由：", judge.get("reason", "未返回"))
print(f"有效判分 {valid}/{len(rows)}；与助教参考一致 {matched}/{valid}。")
print("只有六条合成样例，参考标签尚待学习者核对，不代表已验证裁判可靠性。")
