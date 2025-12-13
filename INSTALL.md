# Installation and Usage Guide

## Quick Start (5 minutes)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Click "API development tools"
4. Fill in application information (can be anything)
5. Obtain `api_id` (number) and `api_hash` (string)

### Step 3: Configure Monitoring Targets

#### Method A: Using Environment Variables (Recommended)

```bash
export TELEGRAM_API_ID=your_API_ID
export TELEGRAM_API_HASH=your_API_HASH
export TARGET_CHATS=@group1,@group2,-1001234567890
export WEBHOOK_URL=http://localhost:8080/webhook
```

#### Method B: Direct Code Modification

Edit `monitor.py`, find the configuration section (starting around line 20):

```python
API_ID = 12345678  # Change to your API ID
API_HASH = 'abcdefgh12345678'  # Change to your API Hash

TARGET_CHATS = [
    '@your_group',      # Replace with your group
    -1001234567890,     # Or use group ID
]

WEBHOOK_URL = 'http://localhost:8080/webhook'  # Change to your API address
```

### Step 4: Start Test Webhook (Optional)

In another terminal window:

```bash
python test_webhook.py
```

This will start a test server listening on http://localhost:8080

### Step 5: Start Monitoring Service

```bash
python monitor.py
```

**First run** will prompt:

```
Please enter your phone number (with country code, e.g., +86):
```

After entering, Telegram will send a verification code to your phone, follow the prompts to enter.

Upon success, it will display:

```
============================================================
✓ Service started, listening for new messages...
  Press Ctrl+C to stop the service
============================================================
```

### Step 6: Test

Send a message in your configured group and check:

1. `monitor.py` terminal should show logs of received messages
2. `test_webhook.py` terminal should show received JSON data

## How to Get Group ID?

### Method 1: Using Bot

1. Add [@userinfobot](https://t.me/userinfobot) to the group
2. Forward any message from the group to this bot
3. Bot will tell you the group ID

### Method 2: Using Script

Create file `get_chats.py`:

```python
from telethon.sync import TelegramClient

API_ID = your_API_ID
API_HASH = 'your_API_HASH'

with TelegramClient('temp_session', API_ID, API_HASH) as client:
    print("All your groups and channels:\n")
    for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"Name: {dialog.name}")
            print(f"ID: {dialog.id}")
            print(f"Username: @{dialog.entity.username}" if hasattr(dialog.entity, 'username') and dialog.entity.username else "None")
            print("-" * 40)
```

Run:

```bash
python get_chats.py
```

## Docker Deployment

### First Login (Requires Interaction)

```bash
# 1. Create sessions directory
mkdir -p sessions

# 2. Run interactively for first login
docker run -it --rm \
  -e TELEGRAM_API_ID=your_API_ID \
  -e TELEGRAM_API_HASH=your_API_HASH \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor:latest
```

Follow prompts to enter phone number and verification code.

### Background Running

After successful login, use docker-compose to run in background:

```bash
# 1. Create .env file
cat > .env << EOF
TELEGRAM_API_ID=your_API_ID
TELEGRAM_API_HASH=your_API_HASH
TARGET_CHATS=@group1,@group2
WEBHOOK_URL=http://your-api.com/webhook
LOG_LEVEL=INFO
EOF

# 2. Start service
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

## System Service (Linux)

### Create systemd Service

```bash
sudo nano /etc/systemd/system/telegram-monitor.service
```

Content:

```ini
[Unit]
Description=Telegram Monitor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/telegram-monitor
Environment="TELEGRAM_API_ID=your_API_ID"
Environment="TELEGRAM_API_HASH=your_API_HASH"
Environment="TARGET_CHATS=@group1,@group2"
Environment="WEBHOOK_URL=http://your-api.com/webhook"
ExecStart=/usr/bin/python3 monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start:

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

## FAQ

### Q: "FloodWaitError" prompt

A: Operations too frequent, wait the specified time and retry.

### Q: Cannot connect to Telegram

A: Check network connection, users in China may need a proxy. You can add proxy configuration in code:

```python
client = TelegramClient(
    SESSION_NAME, 
    API_ID, 
    API_HASH,
    proxy=("socks5", "127.0.0.1", 1080)  # Your proxy address
)
```

### Q: Where is the Session file?

A: In the run directory, filename is `{SESSION_NAME}.session`, default is `telegram_monitor.session`

### Q: How to stop the service?

A: Press `Ctrl+C`

### Q: How to switch accounts?

A: Delete the `.session` file and run `monitor.py` again to log in.

## Test Webhook

Ensure your Webhook server:

1. Can receive POST requests
2. Content-Type is `application/json`
3. Returns status code 200 to indicate success

Test command:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Security Recommendations

1. **Do not publicly share your Session file**
2. **Do not commit API_ID and API_HASH to Git**
3. **Change password regularly**
4. **Use HTTPS to protect Webhook**

## Need Help?

See [README.md](README.md) for more details.
