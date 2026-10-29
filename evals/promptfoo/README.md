# promptfoo 第一节

完整讲义：[08 promptfoo 实践](../../docs/learning/008-promptfoo.md)。

在这个目录运行：

```bash
npm install
npm test
npm run smoke
```

package.json 固定 promptfoo 版本，服务器保留安装生成的 lock 文件；公开副本暂未发布该 lock，其他机器安装时传递依赖可能有差异。已安装的服务器无需反复安装。smoke 回显两条人工样例，不调用模型。

当前终端配置 DEEPSEEK_API_KEY 后：

```bash
npm run eval
```

两个 Prompt、同一个 DeepSeek 模型、五道固定题，共十个评测单元。结果保存为 results 下的 JSON 和 HTML。assertions.cjs 检查结构、证据充足标签与引用编号；语义正确性仍需人工核对。`npm test` 特意展示一个格式正确但内容错误的漏检案例。

不要将 smoke 的通过率写成模型准确率。真实模型对照完成后，以真实输出分析 FAIL，并抽查 PASS；所有结论注明数据集规模和评分规则。
