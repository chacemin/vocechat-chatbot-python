# 使用Python官方镜像作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制必需的文件
COPY pyproject.toml .
COPY config.yaml .
COPY src/ ./src/
COPY setup.py .
COPY uv.lock .

# 安装依赖
RUN pip install --no-cache-dir -e .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "src/main.py"]
