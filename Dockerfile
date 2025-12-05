FROM nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04

# 1. 安装 Python + venv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# 2. 创建虚拟环境
RUN python3 -m venv /opt/venv
# 让后续命令都用 venv 里的 python/pip
ENV PATH="/opt/venv/bin:$PATH"

# 3. 安装依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 拷贝 handler
COPY rp_handler.py .

# 5. 启动
CMD ["python", "-u", "rp_handler.py"]
