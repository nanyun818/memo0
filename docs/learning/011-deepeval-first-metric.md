# 11：从promptfoo到DeepEval，第一次Python语义评测

2026-10-31。状态：独立环境安装与7项离线检查通过；已只读核验学习者运行的j02真实DeepSeek判分，不通过，理由指出咖啡机说法无依据；有效1/1、与助教参考一致1/1，实际请求尝试1次。助教准备和核验没有发起付费请求。完整六条与独立修改仍待完成；下一节[已保存结果的校准检查](012-saved-verdict-regression.md)。

## 先确认上一节实际发生了什么

已读取服务器judge-20261031T111526Z-3550354.json及中文汇总：六条全部获得有效判分，j01/j03/j05通过，j02/j04/j06不通过，与事先的助教参考6/6一致。见[实测报告](../../reports/promptfoo-judge-calibration.md)和[脱敏逐条判分](../../reports/promptfoo-judge-calibration.json)。这验证了六条简单合成样例的表现，不能推断真实应用普遍正确或裁判可靠。

## 为什么还学另一个工具

本轮不换题、不换裁判服务，先理解同一类测试在Python中如何组织。promptfoo让你熟悉YAML配置和网页；DeepEval让你把测试用例、评分指标和通过条件接到Python程序和自动化测试中。两者都可以做模型评分，没有“网页工具弱、Python工具强”的必然关系。

此时评的是固定答案的依据一致性，还没有接入Agent Desk，也没有评工具执行过程；之后才逐步连接真实应用与执行记录。

## 三个对象

| 对象 | 含义 | 本例 |
|---|---|---|
| LLMTestCase | 一份待评样例，提供问题、答案和相关资料 | input、actual_output、retrieval_context |
| GEval metric | 按明确自然语言步骤，用裁判模型评价某个维度 | EvidenceConsistency：事实是否得到资料支持 |
| threshold | 分数达到多少才通过 | 本例strict_mode=True，阈值为1，只收0或1分 |

LLMTestCase里的actual_output是“待批改的答案”，不会因为名字中有actual就自动调用模型生成。本例直接放入旧的固定答案。retrieval_context是提供给裁判检查的资料；这里并未重新运行检索，不能把字段存在当作已测试RAG检索器。

先看这段教学简化代码：

```python
case = LLMTestCase(
    input="Mem0的用途是什么？",
    actual_output='{"answer":"Mem0是一台咖啡机。"}',
    retrieval_context=["Mem0帮助应用保存和检索长期记忆。"],
)

metric = make_metric(judge)  # 建立自带GEval指标，显式指定DeepSeek适配器
metric.measure(case)        # 执行评分，会发起裁判请求
print(metric.score, metric.reason, metric.is_successful())
```

定义case只是把材料装入对象；定义metric是把尺子准备好；measure才开始批改。评分达到阈值后is_successful返回True。这里的1表示满足我们规定的维度，不是100%正确概率，更不是所有功能均正确。

## 模型调用究竟在哪

```text
六条公开合成样例
   ↓ make_test
DeepEval LLMTestCase
   ↓ GEval.measure，使用显式评分步骤
生成裁判提示
   ↓ DeepSeekJudge.generate
DeepSeek API
   ↓ 返回score与中文reason，经结构校验
GEval保存score/reason并比较threshold
   ↓
命令行与本地JSON报告
```

DeepEval本身不是另一个大模型。DeepSeekJudge是我们写的服务适配器，职责是按框架接口把请求发到DeepSeek，再把响应转成框架要求的结构。实际标准在STEPS，标准不藏在模型名称里。框架自带GEval负责组装评测提示和分数处理。

评分步骤只测依据一致性：编造金额、无依据保证不通过；资料不足时如实说明未知可以通过。应用任务完成度需要另一个指标。

## 操作

2026-10-31继续学习时，服务器尚无DeepEval真实报告。为把代码与结果对应起来，先完成一个j02单例，再扩展到全部六条。新增--case参数保持默认六条模式不变；单例模式的请求硬上限按选中用例数设为1。

```bash
python lesson.py --preview --case j02
```

这一条只准备“Mem0是咖啡机”的测试对象。代码中的make_test把问题、答案、资料装进LLMTestCase；STEPS是评分要求；make_metric创建自带GEval并显式指定DeepSeek；metric.measure才发出评分请求。strict_mode=True将本节门槛设为1，因此返回0应判不通过。

设置好当前终端的DEEPSEEK_API_KEY后，运行单例：

```bash
python lesson.py --run --case j02
```

预先预测：咖啡机说法没有资料支持，应为0分、不通过。只有实际返回后才记录实测结论；如果模型判为1，先检查它的理由和保存的judge_prompt，不修改标签迎合模型。如果出错，报告执行错误，不伪造0分。

--report读取最新报告，此时应只有j02一行；“有效1/1、一致1/1”只覆盖这个案例。之后再用不带--case的--run测试六条。

按私人启动指南连接服务器，进入仓库后：

```bash
cd evals/deepeval
source .venv/bin/activate
python lesson.py --preview
```

服务器已经安装在本目录.venv，独立于原项目根目录.venv。激活后终端仍可能显示(.venv)，名字相同不表示路径相同。必要时用which python确认当前解释器在evals/deepeval/.venv/bin/python。

预览没有请求；看每条问题、资料和待评答案，确认仍是同一批六条。真正评分前，在当前终端单独执行隐藏输入命令：

```bash
read -rsp '输入 DeepSeek 密钥后回车：' DEEPSEEK_API_KEY
```

输入完成并回车后，再执行：

```bash
export DEEPSEEK_API_KEY
python lesson.py --run
```

正常6次裁判调用，每次最多500输出token。适配器限制最多6次尝试，不自动重试，错误停止并保存已有结果。再次--run会产生新用量。使用--report查看已有报告，不再次调用模型：

```bash
python lesson.py --report
```

程序输出先看每条裁判判分与理由，再看有效判分数、与参考一致数。无有效判分的错误单列；不能把网络错误写成“答案不合格”。参考标签仍是助教建议，未作为裁判输入，也未冒充独立人工标注。

这次结果先在终端看，不会自动出现在promptfoo网页；两个框架各自保存结果。后面Langfuse再学习统一记录和实验比较。

## 最先读的代码入口

1. [make_test与make_metric](../../evals/deepeval/lesson.py)：看资料放在哪、标准写在哪、model显式传入哪个适配器。
2. main中的metric.measure：分清准备对象与真正执行。
3. DeepSeekJudge.generate与parse_verdict：发送HTTP、限制请求、校验响应；不要求第一节独立重写适配器。

第一项独立修改放在真实基线之后：写一个“部分事实正确、夹带无依据事实”的新答案，先独立写预期判分和原因，再在隔离副本加入样例、运行并记录。不要先看裁判结果再倒推标准。未完成此修改前，不能把AI准备的适配器称为自己独立实现。

## 已完成验证和边界

- Ubuntu Python3.10独立虚拟环境安装deepeval==4.3.2，版本已确认，传递依赖清单留在服务器installed-versions.txt。
- self-check经真实GEval执行六条，但假裁判固定返回0，网络请求为0；验证框架接口，不验证语义。
- 7项离线检查通过：输出schema、无效/非二值评分拒绝、缺密钥零请求、预算上限、请求载荷、错误不重试、真实GEval连接且不使用参考标签直接判分。
- 真实DeepSeek兼容性与判分质量尚待--run验证。GEval构建的提示不同于promptfoo，同一模型与样例也不保证结果一致。
- 本例用自定义模型的结构化返回，不使用logprobs加权；固定评测步骤避免额外生成步骤请求，严格二值评分。它不是论文G-Eval指标复现。

官方依据：[DeepEval G-Eval](https://deepeval.com/docs/metrics-llm-evals)、[自定义裁判模型接口](https://deepeval.com/guides/guides-using-custom-llms)。执行接口另核对了已安装4.3.2包内GEval、DeepEvalBaseLLM和schema源码。
