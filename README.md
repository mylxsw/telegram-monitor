# Telegram Monitor Service

一个使用 Python + Telethon 实现的 Telegram 群组/频道消息监听服务。监听指定的 Telegram 群组/频道，并将新消息转发到自定义的 HTTP API。

## 功能特点

- ✅ 使用 Telethon (MTProto) 以用户账号登录，而非 Bot
- ✅ 支持监听多个群组/频道
- ✅ 支持 @username 和数字 ID 两种格式的群组标识
- ✅ 将消息以结构化 JSON 格式 POST 到自定义 Webhook
- ✅ 完整的消息信息：群组、发送者、文本、时间、媒体等
- ✅ Session 持久化，无需每次登录
- ✅ 详细的日志输出，便于监控和调试
- ✅ 支持环境变量和配置文件两种配置方式
- ✅ 容错处理，Webhook 失败不影响监听服务

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install telethon aiohttp
```

### 2. 获取 Telegram API 凭证

1. 访问 [https://my.telegram.org](https://my.telegram.org)
2. 登录你的 Telegram 账号
3. 进入 "API development tools"
4. 创建一个应用，获取 `api_id` 和 `api_hash`

### 3. 配置服务

#### 方式一：环境变量（推荐）

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

```env
TELEGRAM_API_ID=你的_API_ID
TELEGRAM_API_HASH=你的_API_HASH
TARGET_CHATS=@group1,@group2,-1001234567890
WEBHOOK_URL=http://your-api.com/webhook
```

然后使用环境变量运行：

```bash
export $(cat .env | xargs)
python monitor.py
```

#### 方式二：直接修改代码

编辑 `monitor.py` 文件，修改配置部分：

```python
# Telegram API 凭证
API_ID = 12345678  # 替换为你的 API ID
API_HASH = 'your_api_hash_here'  # 替换为你的 API Hash

# 要监听的群组/频道列表
TARGET_CHATS = [
    '@example_group',  # 群组用户名
    -1001234567890,    # 群组 ID
]

# Webhook URL
WEBHOOK_URL = 'http://your-api.com/webhook'
```

### 4. 运行服务

```bash
python monitor.py
```

**首次运行**时，程序会提示你输入：
1. 手机号码（包含国家代码，如 +86）
2. 验证码（Telegram 会发送到你的手机）
3. 如果启用了两步验证，还需要输入密码

完成后会生成 `telegram_monitor.session` 文件，后续运行会自动使用该 session，无需重新登录。

## 消息格式

发送到 Webhook 的 JSON 格式：

```json
{
  "chat_id": -1001234567890,
  "chat_name": "示例群组",
  "message_id": 12345,
  "text": "消息文本内容",
  "date": "2024-01-01T12:00:00+08:00",
  "sender_id": 987654321,
  "sender_name": "@username",
  "media": false,
  "ts": 1704081600
}
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `chat_id` | int | 群组/频道 ID |
| `chat_name` | string | 群组/频道名称 |
| `message_id` | int | 消息 ID |
| `text` | string | 消息文本内容（纯文本，无则为空字符串） |
| `date` | string | 消息发送时间（ISO8601 格式） |
| `sender_id` | int | 发送者 ID |
| `sender_name` | string | 发送者名称（优先 username，否则为姓名） |
| `media` | boolean | 是否包含媒体（图片、视频、文件等） |
| `ts` | int | 当前时间戳（Unix timestamp） |

## 日志输出

服务运行时会输出详细的日志信息：

```
2024-01-01 12:00:00 - __main__ - INFO - ============================================================
2024-01-01 12:00:00 - __main__ - INFO - Telegram Monitor Service 启动中...
2024-01-01 12:00:00 - __main__ - INFO - ============================================================
2024-01-01 12:00:00 - __main__ - INFO - 配置信息:
2024-01-01 12:00:00 - __main__ - INFO -   API ID: 12345678
2024-01-01 12:00:00 - __main__ - INFO -   Session: telegram_monitor.session
2024-01-01 12:00:00 - __main__ - INFO -   Webhook URL: http://your-api.com/webhook
2024-01-01 12:00:00 - __main__ - INFO -   监听目标数: 2
2024-01-01 12:00:00 - __main__ - INFO - ------------------------------------------------------------
2024-01-01 12:00:00 - __main__ - INFO - 正在连接到 Telegram...
2024-01-01 12:00:01 - __main__ - INFO - ✓ 已成功连接到 Telegram
2024-01-01 12:00:01 - __main__ - INFO - ✓ 已登录为: @your_username (ID: 123456789)
2024-01-01 12:00:01 - __main__ - INFO - 正在初始化目标群组列表...
2024-01-01 12:00:01 - __main__ - INFO -   ✓ 已添加监听目标: 示例群组 (ID: -1001234567890)
2024-01-01 12:00:01 - __main__ - INFO - ✓ 共初始化 1 个监听目标
2024-01-01 12:00:01 - __main__ - INFO - ============================================================
2024-01-01 12:00:01 - __main__ - INFO - ✓ 服务已启动，正在监听新消息...
2024-01-01 12:00:01 - __main__ - INFO -   按 Ctrl+C 停止服务
2024-01-01 12:00:01 - __main__ - INFO - ============================================================
2024-01-01 12:05:30 - __main__ - INFO - 📨 收到消息 | 群组: 示例群组 | 发送者: @user1 | 文本: Hello World
2024-01-01 12:05:30 - __main__ - INFO - ✓ 消息已发送到 webhook (状态码: 200)
```

## 高级配置

### 调整日志级别

```bash
export LOG_LEVEL=DEBUG  # 可选: DEBUG, INFO, WARNING, ERROR
python monitor.py
```

### 使用不同的 Session 文件

```bash
export TELEGRAM_SESSION=my_custom_session
python monitor.py
```

### 获取群组 ID

如果你不知道群组的数字 ID，可以：

1. 使用 Telegram 官方应用，在群组设置中查看
2. 或者使用以下临时脚本：

```python
from telethon.sync import TelegramClient

API_ID = 你的_API_ID
API_HASH = '你的_API_HASH'

with TelegramClient('temp_session', API_ID, API_HASH) as client:
    for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"{dialog.name}: {dialog.id}")
```

## Docker 部署

### 构建镜像

```bash
docker build -t telegram-monitor .
```

### 运行容器

```bash
docker run -d \
  --name telegram-monitor \
  -e TELEGRAM_API_ID=你的_API_ID \
  -e TELEGRAM_API_HASH=你的_API_HASH \
  -e TARGET_CHATS=@group1,-1001234567890 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor
```

注意：首次运行需要交互式登录：

```bash
docker run -it \
  --name telegram-monitor \
  -e TELEGRAM_API_ID=你的_API_ID \
  -e TELEGRAM_API_HASH=你的_API_HASH \
  -e TARGET_CHATS=@group1,-1001234567890 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor
```

## 常见问题

### 1. 如何获取群组的 ID？

- 转发群组的任意消息给 [@userinfobot](https://t.me/userinfobot)
- 或在群组中使用 [@RawDataBot](https://t.me/RawDataBot) 查看完整信息
- 使用上面提供的临时脚本列出所有群组

### 2. Session 文件丢失怎么办？

删除旧的 `.session` 文件，重新运行程序进行登录验证。

### 3. Webhook 调用失败

检查以下几点：
- Webhook URL 是否正确且可访问
- 网络连接是否正常
- 查看服务日志中的错误信息

### 4. 无法连接到 Telegram

- 检查网络连接
- 如果在国内，可能需要配置代理
- 确认 API_ID 和 API_HASH 正确

### 5. 消息接收不完整

- 确保账号有权限查看群组消息
- 某些私密群组可能有限制
- 检查 TARGET_CHATS 配置是否正确

## 注意事项

1. **隐私和安全**：
   - Session 文件包含你的登录凭证，请妥善保管
   - 不要将 Session 文件提交到代码库
   - 建议使用环境变量管理敏感配置

2. **使用限制**：
   - 遵守 Telegram 的使用条款
   - 避免频繁操作导致账号受限
   - 不要用于垃圾信息或非法用途

3. **稳定性**：
   - 建议使用 supervisor、systemd 或 Docker 保持服务运行
   - 定期检查日志，确保服务正常

## 系统服务部署（Linux）

### 使用 systemd

创建服务文件 `/etc/systemd/system/telegram-monitor.service`：

```ini
[Unit]
Description=Telegram Monitor Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telegram-monitor
Environment="TELEGRAM_API_ID=你的_API_ID"
Environment="TELEGRAM_API_HASH=你的_API_HASH"
Environment="TARGET_CHATS=@group1,-1001234567890"
Environment="WEBHOOK_URL=http://your-api.com/webhook"
ExecStart=/usr/bin/python3 /path/to/telegram-monitor/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

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

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 GitHub Issues 中提出。
