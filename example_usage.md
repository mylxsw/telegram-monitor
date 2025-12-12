# 使用示例

## 场景 1: 本地开发测试

### 1. 启动测试 Webhook 服务器

终端 1:
```bash
python test_webhook.py
```

输出:
```
============================================================
测试 Webhook 服务器
============================================================
监听地址: http://0.0.0.0:8080
本地访问: http://localhost:8080
Webhook URL: http://localhost:8080/webhook
------------------------------------------------------------
按 Ctrl+C 停止服务器
============================================================
```

### 2. 配置并启动监听服务

终端 2:
```bash
# 设置环境变量
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdefgh12345678
export TARGET_CHATS=@my_test_group
export WEBHOOK_URL=http://localhost:8080/webhook

# 启动监听
python monitor.py
```

### 3. 测试

在 Telegram 群组 `@my_test_group` 中发送消息 "Hello World"

终端 2 显示:
```
📨 收到消息 | 群组: My Test Group | 发送者: @john | 文本: Hello World
✓ 消息已发送到 webhook (状态码: 200)
```

终端 1 显示:
```
============================================================
收到消息 @ 2024-01-01 12:00:00
============================================================
群组: My Test Group (ID: -1001234567890)
发送者: @john (ID: 123456789)
消息ID: 12345
时间: 2024-01-01T12:00:00+08:00
媒体: 否
内容: Hello World
------------------------------------------------------------
完整 JSON: {
  "chat_id": -1001234567890,
  "chat_name": "My Test Group",
  "message_id": 12345,
  "text": "Hello World",
  "date": "2024-01-01T12:00:00+08:00",
  "sender_id": 123456789,
  "sender_name": "@john",
  "media": false,
  "ts": 1704081600
}
============================================================
```

---

## 场景 2: 生产环境部署

### 使用 Docker Compose

1. **准备配置文件**

创建 `.env`:
```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdefgh12345678
TARGET_CHATS=@group1,@group2,-1001234567890
WEBHOOK_URL=https://api.yourdomain.com/telegram/webhook
LOG_LEVEL=INFO
```

2. **首次登录**

```bash
# 创建 sessions 目录
mkdir -p sessions

# 交互式登录
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor:latest
```

按提示输入手机号和验证码。

3. **后台运行**

```bash
docker-compose up -d
```

4. **查看日志**

```bash
docker-compose logs -f telegram-monitor
```

5. **停止服务**

```bash
docker-compose down
```

---

## 场景 3: Linux 系统服务

### 使用 Systemd

1. **创建服务文件**

```bash
sudo nano /etc/systemd/system/telegram-monitor.service
```

内容:
```ini
[Unit]
Description=Telegram Monitor Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-monitor
Environment="TELEGRAM_API_ID=12345678"
Environment="TELEGRAM_API_HASH=abcdefgh12345678"
Environment="TARGET_CHATS=@group1,@group2"
Environment="WEBHOOK_URL=https://api.yourdomain.com/webhook"
ExecStart=/usr/bin/python3 /home/ubuntu/telegram-monitor/monitor.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/telegram-monitor.log
StandardError=append:/var/log/telegram-monitor.log

[Install]
WantedBy=multi-user.target
```

2. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
```

3. **查看状态**

```bash
sudo systemctl status telegram-monitor
```

4. **查看日志**

```bash
# 实时日志
sudo journalctl -u telegram-monitor -f

# 或查看文件
tail -f /var/log/telegram-monitor.log
```

---

## 场景 4: 监听多个群组

```bash
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdefgh12345678
export TARGET_CHATS=@crypto_news,@tech_updates,@trading_signals,-1001234567890
export WEBHOOK_URL=http://api.example.com/telegram/messages

python monitor.py
```

日志示例:
```
正在初始化目标群组列表...
  ✓ 已添加监听目标: Crypto News (ID: -1001111111111)
  ✓ 已添加监听目标: Tech Updates (ID: -1002222222222)
  ✓ 已添加监听目标: Trading Signals (ID: -1003333333333)
  ✓ 已添加监听目标: Custom Group (ID: -1001234567890)
✓ 共初始化 4 个监听目标
```

---

## 场景 5: 自定义 Webhook 处理

### Python Flask 示例

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # 处理消息
    print(f"收到来自 {data['chat_name']} 的消息")
    print(f"发送者: {data['sender_name']}")
    print(f"内容: {data['text']}")
    
    # 可以在这里添加你的业务逻辑
    # - 存储到数据库
    # - 发送通知
    # - 触发其他操作
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Node.js Express 示例

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/webhook', (req, res) => {
    const data = req.body;
    
    console.log(`收到来自 ${data.chat_name} 的消息`);
    console.log(`发送者: ${data.sender_name}`);
    console.log(`内容: ${data.text}`);
    
    // 你的业务逻辑
    
    res.json({ status: 'ok' });
});

app.listen(8080, () => {
    console.log('Webhook server listening on port 8080');
});
```

---

## 场景 6: 调试模式

启用详细日志:

```bash
export LOG_LEVEL=DEBUG
python monitor.py
```

输出会包含更多细节:
```
DEBUG - 连接状态: Connected
DEBUG - 接收到事件: NewMessage
DEBUG - 处理消息 ID: 12345
DEBUG - 发送 JSON: {"chat_id": -1001234567890, ...}
DEBUG - HTTP 响应: 200 OK
```

---

## 场景 7: 错误处理示例

当 Webhook 服务不可用时:

```
📨 收到消息 | 群组: Test Group | 发送者: @user | 文本: Test message
✗ 发送到 webhook 失败 (网络错误): Cannot connect to host localhost:8080
```

服务会记录错误但**继续运行**，不会中断监听。

---

## 常用命令总结

```bash
# 检查 Python 版本
python3 --version

# 安装依赖
pip install -r requirements.txt

# 启动监听（使用环境变量）
export TELEGRAM_API_ID=xxx
export TELEGRAM_API_HASH=xxx
export TARGET_CHATS=xxx
export WEBHOOK_URL=xxx
python monitor.py

# 启动测试 webhook
python test_webhook.py

# 使用自定义端口启动测试 webhook
python test_webhook.py 9000

# Docker 构建
docker build -t telegram-monitor .

# Docker 运行
docker run -d --env-file .env -v $(pwd)/sessions:/app/sessions telegram-monitor

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```
