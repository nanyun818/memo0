# DeepEval：第一节

状态（2026-10-31）：服务器独立Python环境已安装deepeval==4.3.2；7项离线检查和实际GEval假裁判流程通过。真实DeepSeek评分尚待运行。本目录不会改动项目原有的Python虚拟环境。

本例使用DeepEval自带GEval，不自制一套同名框架。通过DeepEvalBaseLLM适配DeepSeek。先按[中文讲义](../../docs/learning/011-deepeval-first-metric.md)理解LLMTestCase、metric、threshold。

在仓库根目录，首次安装：

```bash
python3 -m venv evals/deepeval/.venv
evals/deepeval/.venv/bin/python -m pip install -r evals/deepeval/requirements.txt
```

服务器本课程环境已完成安装，无须重装。进入该实验目录：

```bash
cd evals/deepeval
source .venv/bin/activate
python lesson.py --preview
```

初学时先只看j02“咖啡机”样例：`python lesson.py --preview --case j02`。对应的真实评分命令是`python lesson.py --run --case j02`，正常只发1次请求，适配器也限制本轮最多1次尝试。省略--case才对全部6条运行。该单例实验的通过/一致数分母为1，不能称为已完成6条实验。

默认/preview不发模型请求。真实运行要求当前终端已export DEEPSEEK_API_KEY：

```bash
python lesson.py --run
python lesson.py --report
```

--run才会发起请求。正常6条，每条1次；适配器硬上限6次尝试，单次最多500输出token、60秒超时，无自动重试，出错停止并保存已有结果。只对固定答案评分，不再次生成答案。结果在本目录results内，--report读取最近报告；重跑会再次使用模型额度。

离线验证供开发使用：

```bash
python -m unittest -v test_adapter
python lesson.py --self-check
```

self-check通过真实GEval流程，但假裁判固定返回0；它故意不辨别内容，不能把输出当成DeepSeek判分。单元检查验证schema、二值分数、缺密钥不请求、预算上限、错误不重试、实际GEval连接与参考标签不代替判分。

复用兄弟目录promptfoo/judge-cases.json中的同一批6条样例。参考标签不会进入LLMTestCase或裁判提示，仅在判分后比较。关闭DeepEval遥测和自动dotenv加载，使用独立metric.measure，不登录或上传到Confident AI。真实--run会把这批公开合成数据发给DeepSeek。

评分步骤显式给定，strict_mode=True，async_mode=False；阈值为1。自定义模型适配不提供logprobs加权分数，这是一项二值G-Eval练习，不是论文G-Eval实验复现。真实裁判返回的JSON由Pydantic schema校验，错误不是答案质量的0分。

报告记录输入样例文件哈希、评分步骤、生成的裁判提示、分数、理由、标签来源与用量。DeepEval会构建不同于promptfoo的裁判提示，结果不保证相同；同一组小样例不足以比较框架优劣。
