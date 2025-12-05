import runpod
import shlex
import tempfile
from pathlib import Path
import base64
import os
import subprocess

def handler(event):
    print("Worker Start")
    input = event['input']
    binary_b64 = input.get('binary')  
    mode = input.get("mode", "run")
    args = input.get("args", [])
    if isinstance(args, str):
        args = shlex.split(args)
    
    tmp_dir = Path(tempfile.mkdtemp())
    bin_path = tmp_dir / "bin_runner"

    with open(bin_path, "wb") as f:
        f.write(base64.b64decode(binary_b64))
    os.chmod(bin_path, 0o755)

    if mode == "run":
        cmd = [str(bin_path)] + args
    elif mode == "ncu":
        cmd = ["ncu", "--set", "full", str(bin_path)] + args
    else:
        return {"error": f"unknown mode: {mode}"}

    proc = subprocess.run(
        cmd, text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return {
        "bin_path": str(bin_path),
        "args": args,
        "mode": mode,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler })
