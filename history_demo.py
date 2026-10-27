"""Offline exercise: save messages to disk, then load them in a new process."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SAMPLE_HISTORY = [
    {"role": "user", "content": "项目代号是蓝鲸"},
    {"role": "assistant", "content": "好的，项目代号是蓝鲸。"},
]


def save_history(path, history):
    path.parent.mkdir(parents=True, exist_ok=True)
    # x means create a new file; refuse to overwrite an existing exercise.
    with path.open("x", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)


def load_history(path):
    with path.open(encoding="utf-8") as file:
        history = json.load(file)
    if not isinstance(history, list):
        raise ValueError("历史文件的最外层必须是列表。")
    for message in history:
        if not isinstance(message, dict):
            raise ValueError("每条历史消息必须是对象。")
        if message.get("role") not in ("user", "assistant"):
            raise ValueError("本练习只允许 user 或 assistant 消息。")
        if not isinstance(message.get("content"), str):
            raise ValueError("消息的 content 必须是字符串。")
    return history


def main():
    parser = argparse.ArgumentParser(description="离线保存/加载练习，不调用模型")
    parser.add_argument("action", choices=("save", "load"))
    parser.add_argument("--file", type=Path, default=ROOT / "logs" / "history_demo.json")
    args = parser.parse_args()
    try:
        if args.action == "save":
            save_history(args.file, SAMPLE_HISTORY)
            print(f"已把 {len(SAMPLE_HISTORY)} 条示例消息保存到：{args.file}")
            print("本次程序即将结束。接下来单独执行 load，会启动一个新进程。")
        else:
            history = load_history(args.file)
            print(f"已从磁盘加载 {len(history)} 条消息：")
            print(json.dumps(history, ensure_ascii=False, indent=2))
            messages = [*history, {"role": "user", "content": "刚才的项目代号是什么？"}]
            print(f"加上新问题后，共有 {len(messages)} 条消息可作为模型输入。")
        print("本练习没有发送 API 请求，也没有产生模型用量。")
    except FileExistsError:
        parser.exit(1, "示例文件已存在，请直接执行 load，或用 --file 指定新的文件名。\n")
    except FileNotFoundError:
        parser.exit(1, "历史文件不存在，请先对相同文件执行 save。\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"运行失败：{error}\n")


if __name__ == "__main__":
    main()
