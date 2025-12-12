# Telegram Monitor Service

A Telegram group/channel message monitoring service implemented using Python + Telethon. It listens to specified Telegram groups/channels and forwards new messages to a custom HTTP API.

## Features

- ✅ Uses Telethon (MTProto) to log in as a user account, not a Bot
- ✅ Supports monitoring multiple groups/channels
- ✅ Supports both @username and numeric ID formats for group identification
- ✅ Posts messages in structured JSON format to custom Webhooks
- ✅ Complete message information: group, sender, text, time, media, etc.
- ✅ Session persistence, no need to log in every time
- ✅ Detailed log output for easy monitoring and debugging
- ✅ Supports both environment variables and configuration file methods
- ✅ Error handling, Webhook failures do not affect the monitoring service

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install telethon aiohttp
```

### 2. Get Telegram API Credentials

1. Visit [https://my.telegram.org](https://my.telegram.org)
2. Log in with your Telegram account
3. Go to "API development tools"
4. Create an application and obtain `api_id` and `api_hash`

### 3. Configure Service

#### Method 1: Environment Variables (Recommended)

Copy `.env.example` to `.env` and modify:

```bash
cp .env.example .env
# Edit the .env file and fill in your configuration
```

```env
TELEGRAM_API_ID=your_API_ID
TELEGRAM_API_HASH=your_API_HASH
TARGET_CHATS=@group1,@group2,-1001234567890
WEBHOOK_URL=http://your-api.com/webhook
```

Then run using environment variables:

```bash
export $(cat .env | xargs)
python monitor.py
```

#### Method 2: Direct Code Modification

Edit the `monitor.py` file and modify the configuration section:

```python
# Telegram API credentials
API_ID = 12345678  # Replace with your API ID
API_HASH = 'your_api_hash_here'  # Replace with your API Hash

# List of groups/channels to monitor
TARGET_CHATS = [
    '@example_group',  # Group username
    -1001234567890,    # Group ID
]

# Webhook URL
WEBHOOK_URL = 'http://your-api.com/webhook'
```

### 4. Run Service

```bash
python monitor.py
```

**On first run**, the program will prompt you to enter:
1. Phone number (including country code, e.g., +86)
2. Verification code (Telegram will send to your phone)
3. Password (if two-step verification is enabled)

After completion, a `telegram_monitor.session` file will be generated. Subsequent runs will automatically use this session without re-login.

## Message Format

JSON format sent to Webhook:

```json
{
  "chat_id": -1001234567890,
  "chat_name": "Example Group",
  "message_id": 12345,
  "text": "Message text content",
  "date": "2024-01-01T12:00:00+08:00",
  "sender_id": 987654321,
  "sender_name": "@username",
  "media": false,
  "ts": 1704081600
}
```

Field Description:

| Field | Type | Description |
|------|------|------|
| `chat_id` | int | Group/Channel ID |
| `chat_name` | string | Group/Channel name |
| `message_id` | int | Message ID |
| `text` | string | Message text content (plain text, empty string if none) |
| `date` | string | Message send time (ISO8601 format) |
| `sender_id` | int | Sender ID |
| `sender_name` | string | Sender name (username preferred, otherwise full name) |
| `media` | boolean | Whether contains media (images, videos, files, etc.) |
| `ts` | int | Current timestamp (Unix timestamp) |

## Log Output

The service outputs detailed log information when running:

```
2024-01-01 12:00:00 - __main__ - INFO - ============================================================
2024-01-01 12:00:00 - __main__ - INFO - Telegram Monitor Service starting...
2024-01-01 12:00:00 - __main__ - INFO - ============================================================
2024-01-01 12:00:00 - __main__ - INFO - Configuration:
2024-01-01 12:00:00 - __main__ - INFO -   API ID: 12345678
2024-01-01 12:00:00 - __main__ - INFO -   Session: telegram_monitor.session
2024-01-01 12:00:00 - __main__ - INFO -   Webhook URL: http://your-api.com/webhook
2024-01-01 12:00:00 - __main__ - INFO -   Target count: 2
2024-01-01 12:00:00 - __main__ - INFO - ------------------------------------------------------------
2024-01-01 12:00:00 - __main__ - INFO - Connecting to Telegram...
2024-01-01 12:00:01 - __main__ - INFO - ✓ Successfully connected to Telegram
2024-01-01 12:00:01 - __main__ - INFO - ✓ Logged in as: @your_username (ID: 123456789)
2024-01-01 12:00:01 - __main__ - INFO - Initializing target group list...
2024-01-01 12:00:01 - __main__ - INFO -   ✓ Added monitoring target: Example Group (ID: -1001234567890)
2024-01-01 12:00:01 - __main__ - INFO - ✓ Initialized 1 monitoring target(s)
2024-01-01 12:00:01 - __main__ - INFO - ============================================================
2024-01-01 12:00:01 - __main__ - INFO - ✓ Service started, listening for new messages...
2024-01-01 12:00:01 - __main__ - INFO -   Press Ctrl+C to stop the service
2024-01-01 12:00:01 - __main__ - INFO - ============================================================
2024-01-01 12:05:30 - __main__ - INFO - 📨 Received message | Group: Example Group | Sender: @user1 | Text: Hello World
2024-01-01 12:05:30 - __main__ - INFO - ✓ Message sent to webhook (status code: 200)
```

## Advanced Configuration

### Adjust Log Level

```bash
export LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
python monitor.py
```

### Use Different Session File

```bash
export TELEGRAM_SESSION=my_custom_session
python monitor.py
```

### Get Group ID

If you don't know the numeric ID of a group, you can:

1. Use the official Telegram app and check in group settings
2. Or use the following temporary script:

```python
from telethon.sync import TelegramClient

API_ID = your_API_ID
API_HASH = 'your_API_HASH'

with TelegramClient('temp_session', API_ID, API_HASH) as client:
    for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"{dialog.name}: {dialog.id}")
```

## Docker Deployment

### Build Image

```bash
docker build -t telegram-monitor .
```

### Run Container

```bash
docker run -d \
  --name telegram-monitor \
  -e TELEGRAM_API_ID=your_API_ID \
  -e TELEGRAM_API_HASH=your_API_HASH \
  -e TARGET_CHATS=@group1,-1001234567890 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor
```

Note: First run requires interactive login:

```bash
docker run -it \
  --name telegram-monitor \
  -e TELEGRAM_API_ID=your_API_ID \
  -e TELEGRAM_API_HASH=your_API_HASH \
  -e TARGET_CHATS=@group1,-1001234567890 \
  -e WEBHOOK_URL=http://your-api.com/webhook \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor
```

## FAQ

### 1. How to get Group ID?

- Forward any message from the group to [@userinfobot](https://t.me/userinfobot)
- Or use [@RawDataBot](https://t.me/RawDataBot) in the group to view complete information
- Use the temporary script provided above to list all groups

### 2. What if Session file is lost?

Delete the old `.session` file and run the program again to perform login verification.

### 3. Webhook call failed

Check the following:
- Is the Webhook URL correct and accessible?
- Is the network connection normal?
- Check error messages in service logs

### 4. Cannot connect to Telegram

- Check network connection
- If in China, you may need to configure a proxy
- Confirm API_ID and API_HASH are correct

### 5. Incomplete message reception

- Ensure the account has permission to view group messages
- Some private groups may have restrictions
- Check if TARGET_CHATS configuration is correct

## Important Notes

1. **Privacy and Security**:
   - Session file contains your login credentials, keep it safe
   - Do not commit Session file to code repository
   - Recommended to use environment variables to manage sensitive configuration

2. **Usage Restrictions**:
   - Follow Telegram's Terms of Service
   - Avoid frequent operations that may cause account restrictions
   - Do not use for spam or illegal purposes

3. **Stability**:
   - Recommended to use supervisor, systemd, or Docker to keep the service running
   - Regularly check logs to ensure the service is operating normally

## System Service Deployment (Linux)

### Using systemd

Create service file `/etc/systemd/system/telegram-monitor.service`:

```ini
[Unit]
Description=Telegram Monitor Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telegram-monitor
Environment="TELEGRAM_API_ID=your_API_ID"
Environment="TELEGRAM_API_HASH=your_API_HASH"
Environment="TARGET_CHATS=@group1,-1001234567890"
Environment="WEBHOOK_URL=http://your-api.com/webhook"
ExecStart=/usr/bin/python3 /path/to/telegram-monitor/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
sudo systemctl status telegram-monitor
```

View logs:

```bash
sudo journalctl -u telegram-monitor -f
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Support

If you have any questions, please submit them in GitHub Issues.
