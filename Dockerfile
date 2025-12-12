FROM python:3.11-slim

LABEL maintainer="telegram-monitor"
LABEL description="Telegram Monitor Service - Forward messages from Telegram groups to HTTP API"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TELEGRAM_SESSION=telegram_monitor

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY monitor.py .

# Create sessions directory for persisting session files
RUN mkdir -p /app/sessions

# Set session file path (can be overridden by environment variable)
ENV TELEGRAM_SESSION=/app/sessions/telegram_monitor

# Health check (verify process is running)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pgrep -f monitor.py > /dev/null || exit 1

# Run application
CMD ["python", "-u", "monitor.py"]
