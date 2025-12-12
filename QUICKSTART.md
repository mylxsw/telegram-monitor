# Quick Start Guide

## Start Service in 3 Minutes

### 1️⃣ Install Dependencies

```bash
pip install telethon aiohttp
```

### 2️⃣ Get Telegram API Credentials

Visit https://my.telegram.org → "API development tools" → Create application

You will get:
- `api_id`: A string of numbers (e.g., 12345678)
- `api_hash`: A string of letters and numbers (e.g., abcdef1234567890abcdef1234567890)

### 3️⃣ Modify Configuration

Edit lines 20-40 of `monitor.py`:

```python
API_ID = 12345678  # Replace with your api_id
API_HASH = 'abcdef1234567890'  # Replace with your api_hash

TARGET_CHATS = [
    '@your_group_username',  # Replace with your group
]

WEBHOOK_URL = 'http://localhost:8080/webhook'  # Replace with your API address
```

### 4️⃣ Start Service

**Terminal 1 - Start test webhook (optional):**
```bash
python test_webhook.py
```

**Terminal 2 - Start monitoring service:**
```bash
python monitor.py
```

First run requires login:
1. Enter phone number (with country code, e.g., +86)
2. Enter verification code sent by Telegram
3. Done!

### 5️⃣ Test

Send a message in your configured Telegram group and check the log output.

---

## Using Environment Variables (Recommended)

```bash
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdef1234567890
export TARGET_CHATS=@group1,@group2
export WEBHOOK_URL=http://your-api.com/webhook

python monitor.py
```

---

## Get Group Identifier

### Method 1: Using Username
If the group has a public username (e.g., @example_group), use it directly.

### Method 2: Using ID
1. Add [@userinfobot](https://t.me/userinfobot) to the group
2. Forward any message from the group to the bot
3. Bot will tell you the group ID (e.g., -1001234567890)

---

## Message Format Example

JSON sent to your webhook:

```json
{
  "chat_id": -1001234567890,
  "chat_name": "Example Group",
  "message_id": 12345,
  "text": "Message content",
  "date": "2024-01-01T12:00:00+08:00",
  "sender_id": 987654321,
  "sender_name": "@username",
  "media": false,
  "ts": 1704081600
}
```

---

## Background Running (Linux)

```bash
nohup python monitor.py > monitor.log 2>&1 &
```

View logs:
```bash
tail -f monitor.log
```

Stop service:
```bash
pkill -f monitor.py
```

---

## Docker Quick Start

```bash
# Build image
docker build -t telegram-monitor .

# First run (requires login)
docker run -it --rm \
  -e TELEGRAM_API_ID=12345678 \
  -e TELEGRAM_API_HASH=abcdef1234567890 \
  -e TARGET_CHATS=@group1,@group2 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor

# Run in background
docker run -d --name telegram-monitor \
  -e TELEGRAM_API_ID=12345678 \
  -e TELEGRAM_API_HASH=abcdef1234567890 \
  -e TARGET_CHATS=@group1,@group2 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor

# View logs
docker logs -f telegram-monitor
```

---

## FAQ

**Q: How to stop the service?**  
A: Press `Ctrl+C`

**Q: What if Session file is lost?**  
A: Delete the old `.session` file, run again and log in

**Q: Webhook call failed?**  
A: Check if WEBHOOK_URL is correct and network is reachable

**Q: Not receiving messages?**  
A: Confirm group identifier is correct and account has viewing permission

---

## Need More Help?

- Detailed documentation: [README.md](README.md)
- Installation guide: [INSTALL.md](INSTALL.md)
- Usage examples: [example_usage.md](example_usage.md)
