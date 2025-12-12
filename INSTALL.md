# 安装和使用指南

## 快速开始（5分钟）

### 步骤 1: 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 获取 Telegram API 凭证

1. 访问 https://my.telegram.org
2. 使用你的手机号登录
3. 点击 "API development tools"
4. 填写应用信息（随意填写）
5. 获得 `api_id` (数字) 和 `api_hash` (字符串)

### 步骤 3: 配置监听目标

#### 方法 A: 使用环境变量（推荐）

```bash
export TELEGRAM_API_ID=你的API_ID
export TELEGRAM_API_HASH=你的API_HASH
export TARGET_CHATS=@group1,@group2,-1001234567890
export WEBHOOK_URL=http://localhost:8080/webhook
```

#### 方法 B: 直接修改代码

编辑 `monitor.py`，找到配置部分（约第 20 行开始）：

```python
API_ID = 12345678  # 改成你的 API ID
API_HASH = 'abcdefgh12345678'  # 改成你的 API Hash

TARGET_CHATS = [
    '@your_group',      # 替换为你的群组
    -1001234567890,     # 或使用群组 ID
]

WEBHOOK_URL = 'http://localhost:8080/webhook'  # 改成你的 API 地址
```

### 步骤 4: 启动测试 Webhook（可选）

在另一个终端窗口中：

```bash
python test_webhook.py
```

这会启动一个测试服务器，监听 http://localhost:8080

### 步骤 5: 启动监听服务

```bash
python monitor.py
```

**首次运行**会提示：

```
请输入你的手机号 (包含国家代码，如 +86):
```

输入后，Telegram 会发送验证码到你的手机，按提示输入即可。

成功后会显示：

```
============================================================
✓ 服务已启动，正在监听新消息...
  按 Ctrl+C 停止服务
============================================================
```

### 步骤 6: 测试

在你配置的群组中发送一条消息，查看：

1. `monitor.py` 的终端应该显示收到消息的日志
2. `test_webhook.py` 的终端应该显示收到的 JSON 数据

## 如何获取群组 ID？

### 方法 1: 使用 Bot

1. 在群组中添加 [@userinfobot](https://t.me/userinfobot)
2. 转发群组的任意消息给这个 bot
3. Bot 会告诉你群组的 ID

### 方法 2: 使用脚本

创建文件 `get_chats.py`:

```python
from telethon.sync import TelegramClient

API_ID = 你的_API_ID
API_HASH = '你的_API_HASH'

with TelegramClient('temp_session', API_ID, API_HASH) as client:
    print("你的所有群组和频道：\n")
    for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"名称: {dialog.name}")
            print(f"ID: {dialog.id}")
            print(f"Username: @{dialog.entity.username}" if hasattr(dialog.entity, 'username') and dialog.entity.username else "无")
            print("-" * 40)
```

运行：

```bash
python get_chats.py
```

## Docker 部署

### 首次登录（需要交互）

```bash
# 1. 创建 sessions 目录
mkdir -p sessions

# 2. 交互式运行进行首次登录
docker run -it --rm \
  -e TELEGRAM_API_ID=你的_API_ID \
  -e TELEGRAM_API_HASH=你的_API_HASH \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor:latest
```

按提示输入手机号和验证码。

### 后台运行

登录成功后，使用 docker-compose 后台运行：

```bash
# 1. 创建 .env 文件
cat > .env << EOF
TELEGRAM_API_ID=你的_API_ID
TELEGRAM_API_HASH=你的_API_HASH
TARGET_CHATS=@group1,@group2
WEBHOOK_URL=http://your-api.com/webhook
LOG_LEVEL=INFO
EOF

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

## 系统服务（Linux）

### 创建 systemd 服务

```bash
sudo nano /etc/systemd/system/telegram-monitor.service
```

内容：

```ini
[Unit]
Description=Telegram Monitor Service
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/telegram-monitor
Environment="TELEGRAM_API_ID=你的_API_ID"
Environment="TELEGRAM_API_HASH=你的_API_HASH"
Environment="TARGET_CHATS=@group1,@group2"
Environment="WEBHOOK_URL=http://your-api.com/webhook"
ExecStart=/usr/bin/python3 monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
sudo systemctl status telegram-monitor
```

查看日志：

```bash
sudo journalctl -u telegram-monitor -f
```

## 常见问题

### Q: 提示 "FloodWaitError"

A: 操作太频繁，等待指定的时间后重试。

### Q: 无法连接到 Telegram

A: 检查网络连接，国内用户可能需要代理。可以在代码中添加代理配置：

```python
client = TelegramClient(
    SESSION_NAME, 
    API_ID, 
    API_HASH,
    proxy=("socks5", "127.0.0.1", 1080)  # 你的代理地址
)
```

### Q: Session 文件在哪里？

A: 在运行目录下，文件名是 `{SESSION_NAME}.session`，默认为 `telegram_monitor.session`

### Q: 如何停止服务？

A: 按 `Ctrl+C`

### Q: 如何切换账号？

A: 删除 `.session` 文件，重新运行 `monitor.py` 进行登录。

## 测试 Webhook

确保你的 Webhook 服务器：

1. 可以接收 POST 请求
2. Content-Type 为 `application/json`
3. 返回状态码 200 表示成功

测试命令：

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 安全建议

1. **不要公开你的 Session 文件**
2. **不要将 API_ID 和 API_HASH 提交到 Git**
3. **定期更换密码**
4. **使用 HTTPS 保护 Webhook**

## 需要帮助？

查看 [README.md](README.md) 了解更多详情。
