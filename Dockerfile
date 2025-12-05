FROM nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04

# 1. 装 Python 和 pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# 2. 工作目录随便选一个干净的
WORKDIR /app

# 3. 拷贝依赖文件并安装
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. 拷贝 handler
COPY rp_handler.py .

# 5. 启动容器
CMD ["python3", "-u", "rp_handler.py"]
