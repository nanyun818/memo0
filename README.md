# AI 应用与产品实践学习记录

围绕一个知识与办事助手，逐步学习 Python、模型 API、RAG、长期记忆、Agent、评测、数据分析和产品设计。

仓库名是 `memo0`，这是个人学习仓库；Mem0 官方项目另见 [mem0ai/mem0](https://github.com/mem0ai/mem0)。当前代码尚未集成 Mem0。

## 当前进度

| 知识块 | 实践状态 | 记录 |
|---|---|---|
| 01 环境、配置、检索与 Git | 配置修改、JSON 排错和 Git 提交已验证；概念解释待补充 | [学习记录](docs/learning/001-environment-config.md) |
| 02 模型 API 与请求响应 | 请求预览和一次真实 DeepSeek 调用已验证；对照练习待完成 | [学习记录](docs/learning/002-model-api.md) |
| 03 会话上下文与长期记忆 | 同会话召回与新进程无历史已验证；独立原理解释继续学习 | [实验记录与原理](docs/learning/003-context-vs-memory.md) |
| 后续模块 | 计划中，尚未完成 | [路线图](docs/ROADMAP.md) |

## 运行

要求 Python 3.10+，当前示例仅使用 Python 标准库。

```bash
python3 -m venv .venv
source .venv/bin/activate
python app.py 'Mem0 是什么？'
python day2.py '用一个例子解释 Mem0 的用途' --dry-run
python -m unittest -v test_day2
```

真实调用需要在当前终端设置 `DEEPSEEK_API_KEY`。隐藏输入方式见 [API 学习记录](docs/learning/002-model-api.md)。

`config.json` 是公开演示配置；个人运行配置和原始对话日志不发布。模型回答需要验证；一次成功调用不代表模型质量或整个课程已验收。

## 每个知识块如何留痕

1. 说明目标、核心概念和代码入口。
2. 保存运行命令、相关代码与可公开的验证结果。
3. 记录遇到的问题、原因与修复。
4. 由学习者填写自己的解释与独立练习结果。
5. 做一次对应主题的提交，核对 GitHub 上的文件与提交。

状态区分：计划中 / 已准备 / 已实践 / 已验证 / 已完成。代码由 AI 协助准备、学习者执行与修改；独立理解和独立编码分别验收，不根据文件存在推定已经掌握。

开始下一块：[会话上下文与长期记忆](docs/learning/003-context-vs-memory.md)。

模板：[知识块记录模板](docs/templates/knowledge-block.md)。
