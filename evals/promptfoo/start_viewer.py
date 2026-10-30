"""Start or reuse this Linux server's history viewer. No model API calls."""
import fcntl
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".promptfoo"
PORT = 15500


def healthy():
    try:
        with urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2) as response:
            data = json.load(response)
        return data.get("status") == "OK" and data.get("version") == "0.125.1"
    except (OSError, ValueError, URLError):
        return False


def main():
    STATE.mkdir(exist_ok=True)
    # Prevent two starts in separate terminals from racing.
    with (STATE / "viewer-start.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if healthy():
            print("网页服务已经运行，直接打开 http://localhost:15500/eval")
            return
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", PORT)) == 0:
                raise RuntimeError("15500 端口已占用，但未识别为课程网页服务；请先检查。")
        executable = ROOT / "node_modules/.bin/promptfoo"
        if not executable.exists():
            raise RuntimeError("尚未安装 promptfoo，请先在此目录执行 npm install。")
        env = os.environ.copy()
        env.pop("DEEPSEEK_API_KEY", None)  # Viewing saved results needs no model key.
        env.update(PROMPTFOO_CONFIG_DIR=str(STATE),
                   PROMPTFOO_DISABLE_TELEMETRY="1", PROMPTFOO_DISABLE_UPDATE="1")
        with (STATE / "viewer.log").open("a") as log:
            process = subprocess.Popen(
                [str(executable), "view", "--port", str(PORT), "--no"],
                cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        (STATE / "viewer.pid").write_text(str(process.pid))
        for _ in range(30):
            if process.poll() is not None:
                raise RuntimeError("网页服务退出，请查看 .promptfoo/viewer.log。")
            if healthy():
                print("网页服务已在后台启动。保持 SSH 通道连接，打开 http://localhost:15500/eval")
                return
            time.sleep(0.5)
        raise RuntimeError("服务还未就绪，请查看 .promptfoo/viewer.log；稍后可重新运行本命令检查。")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as error:
        raise SystemExit(str(error))
