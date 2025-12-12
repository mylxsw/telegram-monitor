FROM python:3.11-slim

LABEL maintainer="telegram-monitor"
LABEL description="Telegram Monitor Service - Forward messages from Telegram groups to HTTP API"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TELEGRAM_SESSION=telegram_monitor

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY monitor.py .

# 创建 sessions 目录用于持久化 session 文件
RUN mkdir -p /app/sessions

# 设置 session 文件路径（可通过环境变量覆盖）
ENV TELEGRAM_SESSION=/app/sessions/telegram_monitor

# 健康检查（检查进程是否运行）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pgrep -f monitor.py > /dev/null || exit 1

# 运行应用
CMD ["python", "-u", "monitor.py"]
