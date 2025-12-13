#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Monitor Service
Listens to specified Telegram groups/channels and forwards new messages to HTTP API

Uses Telethon library to log in to Telegram as a user account and monitor messages from specified groups
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import User, Channel, Chat

# ============================================================================
# Configuration Section - Modify these settings according to your needs
# ============================================================================

# Telegram API credentials (get from https://my.telegram.org)
API_ID = os.getenv('TELEGRAM_API_ID', 'your_API_ID')  # Must replace
API_HASH = os.getenv('TELEGRAM_API_HASH', 'your_API_HASH')  # Must replace

# Session file name (used to save login state)
SESSION_NAME = os.getenv('TELEGRAM_SESSION', 'telegram_monitor')

# List of groups/channels to monitor
# Supported formats:
# - @username format (e.g., '@example_group')
# - Numeric ID format (e.g., -1001234567890)
TARGET_CHATS_STR = os.getenv('TARGET_CHATS', '')
if TARGET_CHATS_STR:
    TARGET_CHATS = [chat.strip() for chat in TARGET_CHATS_STR.split(',') if chat.strip()]
else:
    # Default configuration example - replace with groups you want to monitor
    TARGET_CHATS = [
        # '@example_group',
        # -1001234567890,
    ]

# Webhook URL - HTTP interface address to receive messages
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:8080/webhook')  # Must replace

# Log level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Global Variables
# ============================================================================

# Store target group ID and name mapping
target_chat_ids = set()
chat_info_cache = {}


# ============================================================================
# Helper Functions
# ============================================================================

async def send_to_webhook(data: Dict[str, Any]) -> None:
    """
    Send message data to Webhook URL
    
    Args:
        data: Message data dictionary to send
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WEBHOOK_URL,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                if status == 200:
                    logger.info(f"✓ Message sent to webhook (status code: {status})")
                else:
                    response_text = await response.text()
                    logger.warning(
                        f"⚠ Webhook returned non-200 status code: {status}, "
                        f"Response: {response_text[:200]}"
                    )
    except asyncio.TimeoutError:
        logger.error(f"✗ Sending to webhook timed out: {WEBHOOK_URL}")
    except aiohttp.ClientError as e:
        logger.error(f"✗ Failed to send to webhook (network error): {e}")
    except Exception as e:
        logger.error(f"✗ Failed to send to webhook (unknown error): {e}")


def get_sender_name(sender) -> str:
    """
    Get sender's name
    
    Priority: username > first_name + last_name > id
    
    Args:
        sender: Telegram sender object
        
    Returns:
        Sender name string
    """
    if not sender:
        return "Unknown"
    
    # Prioritize username
    if hasattr(sender, 'username') and sender.username:
        return f"@{sender.username}"
    
    # Then use full name
    if isinstance(sender, User):
        name_parts = []
        if hasattr(sender, 'first_name') and sender.first_name:
            name_parts.append(sender.first_name)
        if hasattr(sender, 'last_name') and sender.last_name:
            name_parts.append(sender.last_name)
        if name_parts:
            return ' '.join(name_parts)
    
    # Finally use ID
    if hasattr(sender, 'id'):
        return f"User_{sender.id}"
    
    return "Unknown"


def get_chat_name(chat) -> str:
    """
    Get chat name
    
    Args:
        chat: Telegram chat object
        
    Returns:
        Chat name string
    """
    if not chat:
        return "Unknown Chat"
    
    # Channel or group
    if isinstance(chat, (Channel, Chat)):
        if hasattr(chat, 'title') and chat.title:
            return chat.title
    
    # User
    if isinstance(chat, User):
        return get_sender_name(chat)
    
    # Use ID
    if hasattr(chat, 'id'):
        return f"Chat_{chat.id}"
    
    return "Unknown Chat"


async def build_message_data(event) -> Dict[str, Any]:
    """
    Build message data structure from event
    
    Args:
        event: Telethon message event
        
    Returns:
        Dictionary containing message information
    """
    message = event.message
    
    # Get sender information
    sender = await event.get_sender()
    sender_id = sender.id if sender else 0
    sender_name = get_sender_name(sender)
    
    # Get chat information
    chat = await event.get_chat()
    chat_id = event.chat_id
    chat_name = chat_info_cache.get(chat_id, get_chat_name(chat))
    
    # Build message data
    data = {
        "chat_id": chat_id,
        "chat_name": chat_name,
        "message_id": message.id,
        "text": message.text or "",
        "date": message.date.isoformat() if message.date else "",
        "sender_id": sender_id,
        "sender_name": sender_name,
        "media": bool(message.media),
        "ts": int(datetime.now().timestamp())
    }
    
    return data


# ============================================================================
# Telegram Client and Event Handling
# ============================================================================

async def init_target_chats(client: TelegramClient) -> None:
    """
    Initialize target group list, parse and get group entities
    
    Args:
        client: Telegram client instance
    """
    global target_chat_ids, chat_info_cache
    
    logger.info("Initializing target group list...")
    
    for chat_identifier in TARGET_CHATS:
        try:
            # Get group entity
            entity = await client.get_entity(chat_identifier)
            chat_id = entity.id
            target_chat_ids.add(chat_id)
            
            # Cache group information
            chat_name = get_chat_name(entity)
            chat_info_cache[chat_id] = chat_name
            
            logger.info(f"  ✓ Added monitoring target: {chat_name} (ID: {chat_id})")
            
        except ValueError as e:
            logger.error(f"  ✗ Cannot find group: {chat_identifier} - {e}")
        except Exception as e:
            logger.error(f"  ✗ Failed to get group information: {chat_identifier} - {e}")
    
    if not target_chat_ids:
        logger.error("⚠ Warning: No valid monitoring targets! Please check TARGET_CHATS configuration")
    else:
        logger.info(f"✓ Initialized {len(target_chat_ids)} monitoring target(s)")


async def message_handler(event):
    """
    Handle new message events
    
    Args:
        event: Telethon new message event
    """
    try:
        chat_id = event.chat_id
        
        # Only process messages from target groups
        if chat_id not in target_chat_ids:
            return
        
        message = event.message
        chat_name = chat_info_cache.get(chat_id, "Unknown")
        
        # Build message data
        data = await build_message_data(event)
        
        # Print brief information
        logger.info(
            f"📨 Received message | Group: {chat_name} | "
            f"Sender: {data['sender_name']} | "
            f"Text: {data['text'][:50]}{'...' if len(data['text']) > 50 else ''}"
        )
        
        # Send to webhook
        await send_to_webhook(data)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)


# ============================================================================
# Main Program
# ============================================================================

async def main():
    """
    Main function - Initialize client and start monitoring
    """
    logger.info("=" * 60)
    logger.info("Telegram Monitor Service starting...")
    logger.info("=" * 60)
    
    # Validate configuration
    if API_ID == 'your_API_ID' or API_HASH == 'your_API_HASH':
        logger.error("✗ Error: Please configure API_ID and API_HASH first!")
        logger.error("  Get your API credentials from https://my.telegram.org")
        sys.exit(1)
    
    if not TARGET_CHATS:
        logger.error("✗ Error: Please configure at least one group to monitor (TARGET_CHATS)!")
        sys.exit(1)
    
    if WEBHOOK_URL == 'http://localhost:8080/webhook':
        logger.warning("⚠ Warning: Using default WEBHOOK_URL, please ensure this is what you want")
    
    logger.info(f"Configuration:")
    logger.info(f"  API ID: {API_ID}")
    logger.info(f"  Session: {SESSION_NAME}.session")
    logger.info(f"  Webhook URL: {WEBHOOK_URL}")
    logger.info(f"  Target count: {len(TARGET_CHATS)}")
    logger.info("-" * 60)
    
    # Create Telegram client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        # Start client
        logger.info("Connecting to Telegram...")
        await client.start()
        logger.info("✓ Successfully connected to Telegram")
        
        # Get current user information
        me = await client.get_me()
        logger.info(f"✓ Logged in as: {get_sender_name(me)} (ID: {me.id})")
        
        # Initialize target groups
        await init_target_chats(client)
        
        # Register new message event handler
        client.add_event_handler(
            message_handler,
            events.NewMessage()
        )
        
        logger.info("=" * 60)
        logger.info("✓ Service started, listening for new messages...")
        logger.info("  Press Ctrl+C to stop the service")
        logger.info("=" * 60)
        
        # Keep running
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal, stopping service...")
    except Exception as e:
        logger.error(f"✗ Runtime error: {e}", exc_info=True)
    finally:
        if client.is_connected():
            await client.disconnect()
            logger.info("✓ Disconnected")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nService stopped")
    except Exception as e:
        logger.error(f"Program exited abnormally: {e}", exc_info=True)
        sys.exit(1)
