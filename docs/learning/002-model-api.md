# 02：模型 API、请求、响应与 token

日期：2026-10-27。

状态：请求预览与一次真实调用已验证；对照实验及独立解释待完成。

## 数据流

问题 → 本地关键词检索 → 构造 messages → DeepSeek API → 解析回答 → 保存成功响应日志。

模型在 API 服务端运行，本地程序负责检索与请求。当前没有接入真正的 Mem0 或 OpenViking。

## 请求中的字段

| 字段 | 用途 |
|---|---|
| model | 指定模型，当前示例默认 deepseek-flash |
| messages | 模型本次能看到的消息列表 |
| system | 回答规则，例如根据资料回答 |
| user | 用户问题与参考资料 |
| Authorization | HTTP 请求头，携带从环境变量读取的密钥，不进入预览与日志 |
| max_tokens | 模型输出的 token 数量上限；与检索 top_k 不同 |

先预览，不调用 API：

```bash
python day2.py '用一个例子解释 Mem0 的用途' --dry-run
```

## 密钥的输入

在已登录的 Linux 服务器 shell 中，先单独运行：

```bash
read -rsp '输入 API Key 后按回车：' DEEPSEEK_API_KEY
```

输入或粘贴自己的密钥后按回车，屏幕不显示字符是正常的。再单独执行：

```bash
export DEEPSEEK_API_KEY
```

export 允许后续启动的 Python 进程读取该变量。新开 SSH 会话需要重新设置，不向仓库提交密钥，也不通过 echo 或截图展示。

## 真实请求与已有证据

```bash
python day2.py '用一个例子解释 Mem0 的用途'
```

真实请求会产生 API 用量。本程序关闭思考模式，输出上限 600 token，每次请求不自动重试。

从服务器成功日志提取的脱敏事实：

- 北京时间 2026-10-27 17:52:24 左右，有一条成功响应。
- 模型 deepseek-flash，使用 1 条本地参考资料。
- 请求耗时约 0.972 秒，输入 108 token，输出 37 token。
- finish_reason 为 stop，当前请求没有携带历史轮次。

这说明一次真实请求已跑通，不证明所有模型答案正确。脱敏结果见 [记录](../../reports/day2-api-observation.json)。未发布原始问题、回答、密钥和对话日志。

## token 与耗时

token 是模型处理文本的计量单位，不直接等于字数。输入包括 system、问题、参考资料与本次携带的历史；输出是模型生成内容。这里的秒数是客户端测得的一次请求耗时，不能用一个样本代表稳定的服务速度。

## 对照练习：待完成

1. top_k 分别设为 1 和 2，对“记忆”类问题先做 --dry-run，观察参考资料数量。
2. 在模型、提示词和问题固定的前提下比较资料差异。现有 --no-context 同时改变资料与回答规则，只用于教学演示，不把它当作严格归因实验。
3. 用自己的话解释 API Key、model、messages 的职责。

## 失败处理与检查

- 401：核对密钥；402：核对账户余额；429：频率或并发限制；500/503：平台错误或繁忙。
- 网络超时不代表请求一定没有处理或计费；先检查状态，避免盲目连续重试。
- 配置错误先检查 JSON；模型响应结构错误由程序明确提示，不把它伪装成正常答案。

离线检查：

```bash
python -m unittest -v test_day2
```

测试使用模拟响应，不使用真实密钥、不发送真实请求。覆盖缺少密钥、请求结构、HTTP 错误、网络错误、坏响应、预览及历史消息组织。

代码入口：day2.py 的 build_messages、call_deepseek 和 run_question。

官方参考：[首次调用](https://api-docs.deepseek.com/)、[错误码](https://api-docs.deepseek.com/quick_start/error_codes/)。
