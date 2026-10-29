# 08：用 promptfoo 做第一份可重复的开源评测实验

准备日期：2026-10-28，继续部署与核验：2026-10-29。第一阶段使用 promptfoo 0.125.1；服务器 Node 22.22.2 满足官方 >=22.22.0 要求。依赖安装在 evals/promptfoo，保持 Python 学习环境和系统 Node 服务独立。

## 你现在要学会的四个组成部分

1. Prompt：发给模型的指令模板。本实验 baseline 与 grounded 都要求相同 JSON 格式，后者增加资料不足时的处理规则。
2. Provider：负责调用被测系统。本节使用 DeepSeek 官方 provider；之后可接自己的 Python RAG 应用。promptfoo 负责运行和评判，模型负责生成。
3. Test：输入与预期。沿用 q03/q05/q08/q09/q10，把 top_k=2 的检索结果固定成资料快照；不在本节改变检索算法。
4. Assertion：自动检查输出的规则。这里检查 JSON 格式、supported 标记和 source_ids；预期标签在 metadata 中，不插入模型的 Prompt。

评测矩阵：2 个 Prompt × 1 个模型 × 5 道题 = 10 个评测单元。两个 Prompt 若都通过，也不必强行证明 grounded 更好；可以加入新的开发难例，但要保留原结果。

## 文件与阅读顺序

工作目录：`evals/promptfoo`。

| 文件 | 阅读目的 |
|---|---|
| promptfooconfig.yaml | 看 prompts、providers、tests、assert 如何组成实验 |
| prompts/baseline.txt、prompts/grounded.txt | 比较模型实际收到的两套指令 |
| tests.json | 看问题、资料和评分标签；理解标签不发给模型 |
| assertions.cjs | 看 pass/fail 的具体判定条件 |
| generate_tests.py | 看如何从原有开发集冻结检索结果，避免重复手写数据 |
| run.sh | 看 CLI 参数、串行调用、关闭共享、结果目录 |
| test_assertions.cjs、smoke.yaml | 看评分器自身如何验证，以及它漏检什么 |

本次测试的是固定检索资料条件下的生成行为，不是整个实时 RAG 流程。q05 的资料为空，expected_supported=false；这只表示模型应该承认资料不足，不表示用户的依赖隔离任务已经完成。原来的端到端完成度维度仍应保留。

## 启动与运行

按私人启动指南连接服务器并激活 .venv 后：

```bash
cd /home/ubuntu/ai-learning-lab/evals/promptfoo
npm test
npm run smoke
```

smoke 用 echo provider 回显两条人工构造的固定输出，不调用模型、不需要密钥。通过只证明框架与断言能运行，不代表 DeepSeek 质量。真实实验使用当前终端的 DEEPSEEK_API_KEY，按之前隐藏输入和 export 的方式设置，然后执行：

```bash
npm run eval
```

每次运行产生唯一的 results/*.json 和同名 HTML 表格。实验禁用缓存并设置 maxRetries=0，正常运行共 10 次模型请求，重复运行会再次产生模型用量。输出预算为每单元最多 600 token，本节没有 LLM 裁判，不会额外调用裁判模型。只有使用本节 run.sh 才保证应用这里的共享与环境设置。先看终端结果表；HTML 可下载到自己的电脑打开，无需在服务器公开报告端口。

PASS 是所有配置的断言通过；FAIL 是断言不通过；ERROR 是请求或执行错误。有 FAIL 时可能返回非零退出码，具体行为依版本与设置而异；不能只凭退出码认定安装坏了。先读失败原因和 errors 数量，不要反复重跑碰运气。

## 为什么自动评分通过仍不代表答案正确

输出示例：

```json
{"answer":"Mem0 用于长期记忆。","supported":true,"source_ids":["mem0"]}
```

断言可以检查结构、标签和引用 ID 是否符合预期。但将 answer 改为“Mem0 是咖啡机。”，这些规则仍然可能通过。test_assertions.cjs 故意保留这个漏检例子，提醒我们：**引用 ID 正确不等于引用内容支持结论；supported 是模型输出的标签，不是事实证明。**

所以下一节再加人工评分校准的语义裁判。不要直接把规则通过率写成事实准确率；也不要只用“包含 Mem0”判答案正确。对照旧的 07 评分表，分别保留正确性、依据性、完成度。

## 本节独立实践（约 2 小时）

1. 运行真实 10 单元实验，保存结果；先看 FAIL/ERROR，再抽查 PASS。
2. 从两个 Prompt 的同一题找差异。解释差异来自格式、证据判断还是实质内容。
3. 新增一条虚构开发题，例如用“收入”替换成另一种资料不含的事实；写清预期依据。不要把真实个人数据加入公开测试集。
4. 修改 grounded 的一条指令，再回归同一批题；记录有无回退。扩充开发集后保留版本，不拿改过的题集与旧结果直接算增益。
5. 提交 Prompt、用例、断言、必要的脱敏结果与解释。真实输出和密钥默认留在被忽略的本地目录。

完成标准：能解释一次 FAIL，能新增一个用例，能指出自动规则的漏检，能复现一次修改前后对照。安装成功不等于学会，100% smoke 不等于模型 100% 正确。

## 官方资料

- [项目仓库](https://github.com/promptfoo/promptfoo)
- [安装与 Node 版本](https://www.promptfoo.dev/docs/installation/)
- [DeepSeek provider](https://www.promptfoo.dev/docs/providers/deepseek/)
- [断言与指标](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
- [JavaScript 评分函数](https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript/)
- [CLI 与退出码](https://www.promptfoo.dev/docs/usage/command-line/)

## 状态

2026-10-29：服务器 promptfoo 0.125.1 安装完成；7 项评分函数检查通过，echo 离线 smoke 为 2 通过、0 失败、0 错误。见 [部署验证](../../reports/promptfoo-setup-verification.md)。真实模型对照未运行。

学习者此前 07 的 5 道真实模型请求已由截图及服务器日志核验成功，人工正式评分仍待完成。08 的真实 Prompt 对照需要学习者在持有密钥的终端运行；不把离线样例或断言测试记为模型成绩。
