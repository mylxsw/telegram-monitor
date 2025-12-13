# -*- coding: utf-8 -*-
"""
Configuration File Example
Copy this file as config.py and fill in your actual configuration

Note: config.py file has been added to .gitignore and will not be committed to the repository
"""

# ============================================================================
# Telegram API Credentials
# Get from https://my.telegram.org
# ============================================================================
API_ID = 12345678  # Replace with your API ID
API_HASH = 'your_api_hash_here'  # Replace with your API Hash

# ============================================================================
# Session File Configuration
# ============================================================================
SESSION_NAME = 'telegram_monitor'  # Session file name

# ============================================================================
# List of Groups/Channels to Monitor
# Supports the following formats:
# - '@username' format (e.g., '@example_group')
# - Numeric ID format (e.g., -1001234567890)
# ============================================================================
TARGET_CHATS = [
    '@example_group',
    '@another_channel',
    -1001234567890,
]

# ============================================================================
# Webhook Configuration
# ============================================================================
WEBHOOK_URL = 'http://localhost:8080/webhook'  # Replace with your webhook address

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
