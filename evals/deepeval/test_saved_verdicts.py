"""Check saved judge verdicts against proposed labels. Never calls a model."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class SavedJudgeCalibrationTests(unittest.TestCase):
    def test_latest_saved_judgments_match_proposed_labels(self):
        reports = list((ROOT / "results").glob("deepeval-*.json"))
        self.assertTrue(reports, "尚无报告，请先运行lesson.py --run --case j02")
        path = max(reports, key=lambda item: item.stat().st_mtime)
        report = json.loads(path.read_text(encoding="utf-8"))
        case_path = ROOT.parent / "promptfoo" / "judge-cases.json"
        self.assertEqual(report["case_file_sha256"], hashlib.sha256(case_path.read_bytes()).hexdigest(), "样例版本已改变，请核对报告来源")
        reference = {case["description"]: case["metadata"]["reference_judge_pass"]
                     for case in json.loads(case_path.read_text(encoding="utf-8"))}
        rows = report["rows"]
        self.assertGreater(report["planned_cases"], 0)
        self.assertEqual(len(rows), report["planned_cases"], "本轮未获得完整结果")
        self.assertEqual(len({row["id"] for row in rows}), len(rows), "发现重复样例")
        for row in rows:
            with self.subTest(case=row["id"]):
                self.assertEqual(row["status"], "graded", "这是执行错误，不是有效内容判分")
                self.assertIn(row["id"], reference)
                self.assertIs(type(row["pass"]), bool)
                self.assertEqual(row["reference_pass"], reference[row["id"]])
                self.assertEqual(row["pass"], reference[row["id"]], "裁判与建议标签存在分歧，需要复核理由")
                self.assertEqual(row["score"], int(row["pass"]))
                print(f"{row['id']}：候选答案{'通过' if row['pass'] else '不通过'}；符合建议标签，裁判校准检查通过。")
        print(f"只复核已保存的{len(rows)}条结果，模型请求0次；建议标签仍待学习者独立核对。")


if __name__ == "__main__":
    unittest.main()
