import runpod
import shlex
import tempfile
from pathlib import Path
import base64
import os
import subprocess
import json

# 可选：查询 GPU 名称
try:
    import pynvml

    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    DEVICE_NAMES: list[str] = []

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        name = pynvml.nvmlDeviceGetName(handle).decode("utf-8").replace(" ", "_")
        DEVICE_NAMES.append(name)

    pynvml.nvmlShutdown()

    if len(set(DEVICE_NAMES)) > 1:
        print(f"Warning: different device names found: {DEVICE_NAMES}")

    # 主 GPU 名字，沿用你之前的逻辑
    DEVICE_NAME = DEVICE_NAMES[0] if DEVICE_NAMES else None

except Exception as e:
    print(f"Warning: failed to query GPU name via pynvml: {e}")
    DEVICE_NAMES = []
    DEVICE_NAME = None


def handler(event):
    print("Worker Start")
    input_data = event["input"]

    # 1. 先处理 config：写到 /tmp/cuda-roll/test_config.json
    config = input_data.get("config")
    config_path_str = None
    if config is not None:
        cfg_dir = Path("/tmp/cuda-roll")
        cfg_dir.mkdir(parents=True, exist_ok=True)
        cfg_path = cfg_dir / "test_config.json"
        config_path_str = str(cfg_path)

        with open(cfg_path, "w") as f:
            # 既支持传 dict/list，也支持直接传 JSON 字符串
            if isinstance(config, str):
                # 假设已经是 JSON 文本，原样写入
                f.write(config)
            else:
                # Python 对象，序列化成 JSON
                json.dump(config, f)

        print(f"Wrote config to {cfg_path}")

    # 2. 二进制部分：解码到临时目录
    binary_b64 = input_data.get("binary")
    mode = input_data.get("mode", "run")
    args = input_data.get("args", [])
    if isinstance(args, str):
        args = shlex.split(args)

    tmp_dir = Path(tempfile.mkdtemp())
    bin_path = tmp_dir / "bin_runner"

    with open(bin_path, "wb") as f:
        f.write(base64.b64decode(binary_b64))
    os.chmod(bin_path, 0o755)

    # 3. 构造命令
    if mode == "run":
        cmd = [str(bin_path)] + args
    elif mode == "ncu":
        cmd = ["ncu", "--set", "full", str(bin_path)] + args
    else:
        return {"error": f"unknown mode: {mode}"}

    # 4. 执行
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 5. 返回结果（确保都是可 JSON 序列化的类型）
    return {
        "bin_path": str(bin_path),
        "config_path": config_path_str,
        "args": args,
        "mode": mode,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        # 新增：GPU 信息
        "gpu_name": DEVICE_NAME,
        "gpu_names": DEVICE_NAMES,
    }


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
