# 每次打开历史评测页面

2026-10-30。仅查看已有结果，无模型请求，不需要 API Key。私人 SSH 连接命令保留在学习启动指南，不发布服务器连接信息。

1. 在自己的电脑用 SSH 的 `-L` 参数，将本地 15500 转发至服务器的 127.0.0.1:15500。保持该 SSH 终端连接。
2. 服务器上进入项目，激活 Python 环境，执行：

```bash
cd /home/ubuntu/ai-learning-lab
source .venv/bin/activate
cd evals/promptfoo
python start_viewer.py
```

该辅助脚本适用于本课程的 Linux 服务器，已有服务则复用，没有运行则在后台启动。使用原来的 .promptfoo 数据目录；日志与启动状态均被 Git 忽略。使用锁防止重复启动；不抢占其他服务的端口。

3. 电脑浏览器打开 http://localhost:15500/eval 。点击当前实验标题旁的下拉箭头选择以前的实验；也可用顶部 History 查看历史记录。

上次真实实验有五道题、两个 Prompt，baseline 4/5、grounded 5/5；echo 是离线样例。

`start_viewer.py` 打开已有记录。`npm run eval` 会重新执行模型评测并产生用量，仅查看历史时不用执行。网页服务可在 SSH 退出后继续运行，但电脑访问服务器的 SSH 通道需要保持连接；重启服务器后可再运行启动脚本。历史数据通常保留在磁盘，不会因关闭浏览器自动删除。
