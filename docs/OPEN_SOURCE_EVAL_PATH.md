# 两周计划内的开源评测实践路线

2026-10-28 调整。已有学习助手、合成开发题和真实 API 结果作为共同项目，不为每个框架重做一个无关联的 demo。每天约 5 小时，评测主课通常 2–3 小时，余下时间用于原计划中的 Python/数据/产品与应用功能。以下是 7 个学习单元，不是新增 7 天期限。

| 顺序 | 对应原路线 | 开源项目与任务 | GitHub 可验收产物 |
|---|---|---|---|
| E1 | D3 | promptfoo：两 Prompt × 同模型 × 五题，规则断言与结果分析 | YAML、Prompt、开发题、断言及对照报告 |
| E2 | D4 前半 | promptfoo：人工标注与 LLM-as-a-Judge，解释规则误判与裁判误判 | 判分标准、人工/裁判分歧案例、额外用量记录 |
| E3 | D4 后半至 D5 | DeepEval：将同一助手输出写成 Python 测试；结合 FastAPI 入口做回归 | 测试文件、metric/threshold 选择、失败记录 |
| E4 | D5–D6 | RAG + Ragas：对比检索与生成，分别测 context precision/recall 与 faithfulness | RAG 输入字段、所选指标、失败归因；Langfuse 接入时集中记录 |
| E5 | D8 | lm-evaluation-harness：先跑兼容生成 API 的小样本任务，理解抽取与评分；源码读 multiple_choice/loglikelihood 区别 | 固定版本/参数、样本数、样例输出与协议限制，不冒充论文分数 |
| E6 | D9–D10 | Inspect AI：在自己的隔离练习任务中执行一次工具调用，检查工具参数、最终任务状态与预算 | dataset/solver/scorer、小任务执行日志与失败路径 |
| E7 | D13 | Agent 评测回归：使用 E6 项目比较有无记忆、不同工作流/重试上限；对照 AgentBench 与 Harness² 的设计 | 完成率、错误工具调用、步数/token、案例复盘与面试说明 |

D7 保留 Mem0 记忆更新、删除与会话/用户隔离；D11 保留 OpenViking；D12 保留 Harness²/Dream-RSI 方法和小规模可行实验；D14 作品演示与投递材料。SQL/产品指标结合实验数据完成，PyTorch/Transformer 基础安排为小练习；深度以实际验收为准。若每个工具都追求生产级掌握，两周不足；本阶段重点把 promptfoo 与 Python 应用评测做扎实，其他框架完成有明确边界的小实验。

## 选型边界与官方来源

- [promptfoo](https://github.com/promptfoo/promptfoo)：配置驱动的 Prompt/模型/应用对照。本节已开始，不强迫云账号。
- [DeepEval](https://github.com/confident-ai/deepeval)：Python 应用测试和模型裁判指标。安装前核验当前 Python 与裁判模型接口，单独环境，不替换现有 .venv。
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)：模型 benchmark。许多选择题评分需要 loglikelihood；普通聊天 API 不必然支持。无 GPU 时优先生成式任务/API 小样本，不能把自定义聊天选择题分数当作官方 MMLU 复现。
- [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai)：复杂评测任务与 Agent 工具执行。先构建自己可控的小任务，再考虑依赖多服务的 benchmark。
- [Ragas](https://github.com/vibrantlabsai/ragas)：原 explodinggradients/ragas 地址目前重定向至该仓库。根据所选 metric 核验需要的 reference、contexts、LLM 或 embedding，不默认 DeepSeek 聊天接口同时提供 embedding。
- [AgentBench](https://github.com/THUDM/AgentBench)：论文作者仓库是 THUDM/AgentBench。用于研究 LLM 作为 Agent 在交互环境中的表现；先读任务与环境配置，在当前服务器上不承诺部署全部环境。

lm-evaluation-harness、Agent 执行系统（harness 的泛称）和 Google Harness² 是不同概念。正确最终答案不能代替工具调用轨迹检查；轨迹也不等于模型未公开的内部思考过程。我们记录可观察的消息、工具调用、结果、步数、用量和任务状态。

## 每个项目统一学习方法

读最小官方示例 → 在本项目跑通 → 修改一个变量 → 跑固定测试 → 解释失败 → 记录局限 → GitHub 提交。说明代码哪些由 AI 协助、哪些由自己修改；不伪造独立实现或评测成绩。未开始的 E2–E7 只记计划，依赖版本与具体 API 在进入单元时重新验证。
