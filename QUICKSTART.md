# 快速开始指南

## 3 分钟启动服务

### 1️⃣ 安装依赖

```bash
pip install telethon aiohttp
```

### 2️⃣ 获取 Telegram API 凭证

访问 https://my.telegram.org → "API development tools" → 创建应用

你会得到：
- `api_id`: 一串数字（例如：12345678）
- `api_hash`: 一串字母数字（例如：abcdef1234567890abcdef1234567890）

### 3️⃣ 修改配置

编辑 `monitor.py` 的第 20-40 行：

```python
API_ID = 12345678  # 替换成你的 api_id
API_HASH = 'abcdef1234567890'  # 替换成你的 api_hash

TARGET_CHATS = [
    '@your_group_username',  # 替换成你的群组
]

WEBHOOK_URL = 'http://localhost:8080/webhook'  # 替换成你的 API 地址
```

### 4️⃣ 启动服务

**终端 1 - 启动测试 webhook (可选):**
```bash
python test_webhook.py
```

**终端 2 - 启动监听服务:**
```bash
python monitor.py
```

首次运行需要登录：
1. 输入手机号（带国家码，如 +86）
2. 输入 Telegram 发送的验证码
3. 完成！

### 5️⃣ 测试

在你配置的 Telegram 群组中发送一条消息，查看日志输出。

---

## 使用环境变量（推荐）

```bash
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdef1234567890
export TARGET_CHATS=@group1,@group2
export WEBHOOK_URL=http://your-api.com/webhook

python monitor.py
```

---

## 获取群组标识

### 方法 1: 使用用户名
如果群组有公开用户名（如 @example_group），直接使用即可。

### 方法 2: 使用 ID
1. 在群组中添加 [@userinfobot](https://t.me/userinfobot)
2. 转发群组的任意消息给 bot
3. Bot 会告诉你群组 ID（例如：-1001234567890）

---

## 消息格式示例

发送到你的 webhook 的 JSON：

```json
{
  "chat_id": -1001234567890,
  "chat_name": "示例群组",
  "message_id": 12345,
  "text": "消息内容",
  "date": "2024-01-01T12:00:00+08:00",
  "sender_id": 987654321,
  "sender_name": "@username",
  "media": false,
  "ts": 1704081600
}
```

---

## 后台运行（Linux）

```bash
nohup python monitor.py > monitor.log 2>&1 &
```

查看日志：
```bash
tail -f monitor.log
```

停止服务：
```bash
pkill -f monitor.py
```

---

## Docker 快速启动

```bash
# 构建镜像
docker build -t telegram-monitor .

# 首次运行（需要登录）
docker run -it --rm \
  -e TELEGRAM_API_ID=12345678 \
  -e TELEGRAM_API_HASH=abcdef1234567890 \
  -e TARGET_CHATS=@group1,@group2 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor

# 后台运行
docker run -d --name telegram-monitor \
  -e TELEGRAM_API_ID=12345678 \
  -e TELEGRAM_API_HASH=abcdef1234567890 \
  -e TARGET_CHATS=@group1,@group2 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor

# 查看日志
docker logs -f telegram-monitor
```

---

## 常见问题

**Q: 如何停止服务？**  
A: 按 `Ctrl+C`

**Q: Session 文件丢失了怎么办？**  
A: 删除旧的 `.session` 文件，重新运行并登录

**Q: Webhook 调用失败？**  
A: 检查 WEBHOOK_URL 是否正确，网络是否可达

**Q: 收不到消息？**  
A: 确认群组标识正确，账号有查看权限

---

## 需要更多帮助？

- 详细文档：[README.md](README.md)
- 安装指南：[INSTALL.md](INSTALL.md)
- 使用示例：[example_usage.md](example_usage.md)
