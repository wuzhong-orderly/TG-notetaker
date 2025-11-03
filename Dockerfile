# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据和日志目录
RUN mkdir -p data logs

# 设置启动脚本权限
RUN chmod +x run.sh

# 暴露端口（如果需要健康检查或 webhook）
EXPOSE 8080

# 创建非 root 用户
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# 启动命令
CMD ["python", "src/bot.py"]