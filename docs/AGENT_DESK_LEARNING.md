# 用自己的 Agent Desk 学懂 AI 应用

2026-10-31顺序调整：学习者要求先学开源评测项目，当前按[评测项目计划](EVAL_PROJECTS_PLAN.md)执行。本文能力地图与源码链路保留；下方10/30版逐日顺序已被新计划替代，未执行部分不代表已完成。

2026-10-30：根据学习者指定的“agent desk”聊天和本机源码，将主项目切换为已经由 AI 协助实现的桌面工作台。后续目标是理解、验证和独立修改现有功能。原终端学习助手和服务器 promptfoo 作为基础练习与评测工具继续保留。

来源：本地 agent-desk 项目 package.json（0.7.0）、README、docs/CAPABILITIES.md、docs/HARNESS2.md，以及下列源文件。本地存在大量未提交改动，公开仓库版本可能滞后；本轮只阅读现有应用，没有改变应用代码或重跑历史聊天所述的97项测试。教学记录发布在学习仓库，不把应用工作区的改动、用户数据或配置整体推送。

## 你已经拥有的东西与需要学会的东西

| 功能 | 当前源码实现 | 对应原理与学习目标 |
|---|---|---|
| 桌面窗口与桌宠 | Electron，React 界面 | 主进程、页面、事件、状态、桌面与网页关系 |
| 普通聊天 | Express 接口，provider SDK，流式输出 | HTTP、JSON、消息列表、模型请求、SSE、取消、错误 |
| 对话历史 | SQLite session/messages | 内存/数据库、会话 ID、恢复与分支 |
| 个人/项目记忆 | 手动编辑的 SQLite 记录，按授权筛选注入 | 长期保存、作用域、注入、更新删除；尚未集成 Mem0 |
| 知识库 | 按行切块、中文双字/英文词处理、FTS5/BM25 | 倒排索引、排序、召回、引用、预算；尚无向量语义检索 |
| Skills | 文本指引，按项目和目标注入 | 指令模板与上下文组织；不等于执行技能脚本 |
| Tools/MCP | 官方 SDK stdio，手动审批、发现、调用 | 宿主/服务/工具、参数、生命周期；尚非模型自主工具循环 |
| 项目任务 | Codex、Claude、DeepSeek Harness 引擎适配 | 工具执行、权限、状态机、停止、备份与恢复 |
| Harness² | 固定 revision 的上游核心与本地宿主适配 | 计划生成、改进、选择、执行边界；不是论文性能复现 |

核心开发语言改为 JavaScript/React/Node；Python继续用于 DeepEval/Ragas、模型基础和研究实验。Mem0、OpenViking、Langfuse 应作为选型与有证据的增量实验，不以“装上所有框架”为验收。

## 先学一条最短链路：点击发送后发生什么

1. `src/main.jsx` 的 `sendMessage` 读取输入框文本和选中的模型/服务商；没有会话时先创建会话。
2. `src/api.mjs` 的 `api` 用 fetch 发出本机 HTTP 请求，将 body 编码为 JSON，携带本机接口 token。这个 token 与模型 API Key 是不同的凭据；学习时不要复制真实值。
3. `server/app.mjs` 的 `/api/sessions/:id/chat` 找到会话，加入用户消息，从已有消息构造 history。
4. `server/extensions.mjs` 的 `context` 根据项目和目标授权选取记忆、技能、知识片段，受字符预算限制；返回参考文本和 sources。
5. app.mjs 将参考文本加入 history，再调用 `server/providers.mjs` 的 `streamProvider`。以 chat-completions 协议为例，模型收到 system 指令和组装后的 history。
6. 模型流式返回片段，后端逐步累加 answer，并发送 start/delta/done 事件；前端读取流并更新 React 状态，因此文字逐步出现。
7. `server/store.mjs` 用 SQLite 保存会话。对话记录不只存在于当前页面，重新打开才能继续读取。

概念性的示意：

```text
输入框 → 前端 sendMessage → 本机 Express 接口
                          ↓
               历史 + 已授权参考的组装
                          ↓
                       模型接口
                          ↓
            后端事件流 → 前端逐步显示答案
                          ↓
                    SQLite 保存记录
```

普通聊天和做项目是两条路径：聊天走 provider API；项目执行走 runs 和引擎适配器。不能因为聊天界面中说了“已改文件”就认为产生了真实修改，要检查执行路径和文件证据。

## 后续十个单元：沿用剩余两周排期

每天约5小时，日期仍暂排10/30至11/08。每单元先讲一个功能的数据流，再读少量关键代码、做一个独立修改或隔离实验、最后留下评测证据。

| 日期 | 学什么 | 看哪些入口 | 实践与验收 |
|---|---|---|---|
| 10/30 | 整体架构与一次聊天 | desktop/main.cjs、src/main.jsx、src/api.mjs、server/app.mjs、server/providers.mjs | 用一条已有对话画发送链路；能说清界面、程序、模型分别负责什么 |
| 10/31 | 历史与记忆 | server/store.mjs、server/extensions.mjs、src/Extensions.jsx | 在独立练习数据中保存/修改/删除一条偏好；区分历史与记忆、授权撤销与旧消息仍保留 |
| 11/01 | RAG 检索与引用 | extensions.mjs 的 search/context、store.mjs 索引、src/ReferenceSources.jsx | 导入虚构小文档，观察匹配和改写失败；解释切块、BM25、来源行号，建立关键词基线 |
| 11/02 | 给实际项目做评测 | test/extensions.test.mjs、test/app.test.mjs、已有 promptfoo/DeepEval | 在隔离数据上测试知识命中、无资料、撤销授权、跨项目不串资料；把语义质量与行为断言分开 |
| 11/03 | Mem0 与语义检索选型 | 现有 context 组装层与独立适配实验 | 对比手动记忆/自动提取，核验 LLM/embedder/存储；保留现有基线，做最小库实验与更新删除测试 |
| 11/04 | 工具与 MCP | server/mcp.mjs、内置工具、test/fixtures/mcp-server.mjs | 用测试服务跑发现/审批/调用，画一次性票据流程；说明手动调用与模型自主调用区别 |
| 11/05 | 任务引擎与 Harness² | server/runs.mjs、server/engines/、server/harness2/、docs/HARNESS2.md | 在临时小项目看状态与执行记录，区分计划比较和真正执行；比较有无规划的完成、耗时与额外调用 |
| 11/06 | 观测与专项评测 | 项目日志/来源快照、隔离测试工具 | 优先一次 Langfuse trace、一个 Ragas 指标；Inspect AI 小任务；OpenViking 最小例和选型说明按资源执行 |
| 11/07 | 产品指标与研究基础 | 现有 SQLite/实验报告、任务流程 | SQL 汇总失败类型；PRD与试用反馈；lm-evaluation-harness 小样本、PyTorch/Transformer与Dream-RSI分成独立限时练习，未运行部分明确标注 |
| 11/08 | 自己解释、修改与演示 | 项目代码和学习报告 | 展示一次消息、一次检索、一次记忆或工具；完成一个独立小改动与回归；整理产品/工程两版项目说明 |

后半段扩展内容较多，以主线验收为优先；无法在剩余时间完成的研究实验移入后续清单，不改成虚假完成。AgentBench保留作任务环境与评分方法对照，不要求部署全部环境。DeepEval与Ragas可通过独立Python测试调用应用，Node应用无须为学习框架而整体重写。

## 第一节怎样学，不再只有运行命令

第一节先在应用里打开已有聊天，指认问题、答案、所选服务商/模型和本轮参考；不需要为理解结构重新发送付费请求。然后只读三个短片段：sendMessage 发请求；app.mjs 组装 history/references；streamProvider 调模型。React 的状态和异步语法在出现时结合这条链路解释。

要形成的解释：前端负责显示，后端负责组织数据和调用，模型负责基于收到的内容生成，数据库负责保存。桌面 Electron 是运行窗口与本地能力宿主，不是另一个大模型。资料不会因为存在项目文件夹中就自动被模型读取，需被应用选择并发送。

独立实践在理解后进行：先对隔离练习页面或测试用例改一个小条件，预测结果，再运行验证。阶段目标是能追踪并改动一条链路，不要求一下读懂全部代码。

## 每次启动与留痕

主应用在 Windows 本机运行，优先打开已安装的 Agent Desk；本地网页默认127.0.0.1:4317，端口冲突时以启动器实际输出为准。它与云服务器15500的promptfoo页面是两个独立服务。开始每节时根据实际任务提供本机启动命令；需要远程评测时才提供SSH和虚拟环境命令。

每块在学习仓库发布概念图、相对代码入口、独立修改说明、测试题和实际结果。不复制生产数据库、密钥或私密历史；应用源码的已有未提交改动不在学习提交里整体提交。简历表述明确初版由AI协助，自己的理解、修改、测试分别有证据。此前示例不等同于你独立实现了这些模块。
