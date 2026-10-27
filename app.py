"""Day 1: a local keyword lookup exercise. No model or external API is used."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_config(path):
    with path.open(encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError("配置的最外层必须是 JSON 对象。")
    if not isinstance(config.get("assistant_name"), str):
        raise ValueError("assistant_name 必须是字符串。")
    top_k = config.get("top_k")
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k 必须是大于 0 的整数。")
    items = config.get("knowledge")
    if not isinstance(items, list):
        raise ValueError("knowledge 必须是列表。")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("每条知识必须是 JSON 对象。")
        if not isinstance(item.get("answer"), str):
            raise ValueError("每条知识的 answer 必须是字符串。")
        keywords = item.get("keywords")
        if not isinstance(keywords, list) or not keywords:
            raise ValueError("每条知识必须有非空 keywords 列表。")
        if any(not isinstance(word, str) or not word.strip() for word in keywords):
            raise ValueError("关键词必须是非空字符串。")
    return config


def lookup(question, items, top_k):
    question = question.casefold()
    matches = []
    for item in items:
        score = sum(word.casefold() in question for word in item["keywords"])
        if score > 0:
            matches.append((score, item["answer"]))
    matches.sort(key=lambda match: match[0], reverse=True)
    return [answer for _, answer in matches[:top_k]]


def main():
    parser = argparse.ArgumentParser(description="第一天：本地关键词检索练习，无模型调用")
    parser.add_argument("question", help="要检索的问题")
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    args = parser.parse_args()
    if not args.question.strip():
        parser.error("问题不能为空。")
    try:
        config = load_config(args.config)
        answers = lookup(args.question, config["knowledge"], config["top_k"])
        answer = "\n".join(answers) if answers else "当前知识中没有匹配项，请补充关键词或知识。"
        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "question": args.question,
            "answer": answer,
            "matches": len(answers),
        }
        log_dir = ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        with (log_dir / "requests.jsonl").open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"运行失败：{error}\n")
    print(f"{config['assistant_name']}（本地关键词检索，未接入大模型）")
    print(answer)


if __name__ == "__main__":
    main()
