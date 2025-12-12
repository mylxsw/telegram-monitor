# Usage Examples

## Scenario 1: Local Development Testing

### 1. Start Test Webhook Server

Terminal 1:
```bash
python test_webhook.py
```

Output:
```
============================================================
Test Webhook Server
============================================================
Listening address: http://0.0.0.0:8080
Local access: http://localhost:8080
Webhook URL: http://localhost:8080/webhook
------------------------------------------------------------
Press Ctrl+C to stop server
============================================================
```

### 2. Configure and Start Monitoring Service

Terminal 2:
```bash
# Set environment variables
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdefgh12345678
export TARGET_CHATS=@my_test_group
export WEBHOOK_URL=http://localhost:8080/webhook

# Start monitoring
python monitor.py
```

### 3. Test

Send message "Hello World" in Telegram group `@my_test_group`

Terminal 2 displays:
```
📨 Received message | Group: My Test Group | Sender: @john | Text: Hello World
✓ Message sent to webhook (status code: 200)
```

Terminal 1 displays:
```
============================================================
Received message @ 2024-01-01 12:00:00
============================================================
Group: My Test Group (ID: -1001234567890)
Sender: @john (ID: 123456789)
Message ID: 12345
Time: 2024-01-01T12:00:00+08:00
Media: No
Content: Hello World
------------------------------------------------------------
Complete JSON: {
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

## Scenario 2: Production Environment Deployment

### Using Docker Compose

1. **Prepare Configuration File**

Create `.env`:
```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdefgh12345678
TARGET_CHATS=@group1,@group2,-1001234567890
WEBHOOK_URL=https://api.yourdomain.com/telegram/webhook
LOG_LEVEL=INFO
```

2. **First Login**

```bash
# Create sessions directory
mkdir -p sessions

# Interactive login
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/sessions:/app/sessions \
  telegram-monitor:latest
```

Follow prompts to enter phone number and verification code.

3. **Run in Background**

```bash
docker-compose up -d
```

4. **View Logs**

```bash
docker-compose logs -f telegram-monitor
```

5. **Stop Service**

```bash
docker-compose down
```

---

## Scenario 3: Linux System Service

### Using Systemd

1. **Create Service File**

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

2. **Start Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
```

3. **Check Status**

```bash
sudo systemctl status telegram-monitor
```

4. **View Logs**

```bash
# Real-time logs
sudo journalctl -u telegram-monitor -f

# Or view file
tail -f /var/log/telegram-monitor.log
```

---

## Scenario 4: Monitor Multiple Groups

```bash
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=abcdefgh12345678
export TARGET_CHATS=@crypto_news,@tech_updates,@trading_signals,-1001234567890
export WEBHOOK_URL=http://api.example.com/telegram/messages

python monitor.py
```

Log example:
```
Initializing target group list...
  ✓ Added monitoring target: Crypto News (ID: -1001111111111)
  ✓ Added monitoring target: Tech Updates (ID: -1002222222222)
  ✓ Added monitoring target: Trading Signals (ID: -1003333333333)
  ✓ Added monitoring target: Custom Group (ID: -1001234567890)
✓ Initialized 4 monitoring target(s)
```

---

## Scenario 5: Custom Webhook Handling

### Python Flask Example

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Process message
    print(f"Received message from {data['chat_name']}")
    print(f"Sender: {data['sender_name']}")
    print(f"Content: {data['text']}")
    
    # Add your business logic here
    # - Store to database
    # - Send notifications
    # - Trigger other actions
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Node.js Express Example

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/webhook', (req, res) => {
    const data = req.body;
    
    console.log(`Received message from ${data.chat_name}`);
    console.log(`Sender: ${data.sender_name}`);
    console.log(`Content: ${data.text}`);
    
    // Your business logic
    
    res.json({ status: 'ok' });
});

app.listen(8080, () => {
    console.log('Webhook server listening on port 8080');
});
```

---

## Scenario 6: Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python monitor.py
```

Output will include more details:
```
DEBUG - Connection status: Connected
DEBUG - Received event: NewMessage
DEBUG - Processing message ID: 12345
DEBUG - Sending JSON: {"chat_id": -1001234567890, ...}
DEBUG - HTTP response: 200 OK
```

---

## Scenario 7: Error Handling Example

When Webhook service is unavailable:

```
📨 Received message | Group: Test Group | Sender: @user | Text: Test message
✗ Failed to send to webhook (network error): Cannot connect to host localhost:8080
```

The service will log errors but **continue running**, without interrupting monitoring.

---

## Common Command Summary

```bash
# Check Python version
python3 --version

# Install dependencies
pip install -r requirements.txt

# Start monitoring (using environment variables)
export TELEGRAM_API_ID=xxx
export TELEGRAM_API_HASH=xxx
export TARGET_CHATS=xxx
export WEBHOOK_URL=xxx
python monitor.py

# Start test webhook
python test_webhook.py

# Start test webhook with custom port
python test_webhook.py 9000

# Docker build
docker build -t telegram-monitor .

# Docker run
docker run -d --env-file .env -v $(pwd)/sessions:/app/sessions telegram-monitor

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```
