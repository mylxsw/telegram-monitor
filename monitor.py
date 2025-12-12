#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Monitor Service
监听指定的 Telegram 群组/频道，将新消息转发到 HTTP API

使用 Telethon 库以用户账号登录 Telegram，监听指定群组的消息
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
# 配置部分 - 请根据实际情况修改这些配置
# ============================================================================

# Telegram API 凭证 (从 https://my.telegram.org 获取)
API_ID = os.getenv('TELEGRAM_API_ID', '你的_API_ID')  # 必须替换
API_HASH = os.getenv('TELEGRAM_API_HASH', '你的_API_HASH')  # 必须替换

# Session 文件名 (用于保存登录状态)
SESSION_NAME = os.getenv('TELEGRAM_SESSION', 'telegram_monitor')

# 要监听的群组/频道列表
# 支持格式：
# - @username 形式 (如 '@example_group')
# - 数字 ID 形式 (如 -1001234567890)
TARGET_CHATS_STR = os.getenv('TARGET_CHATS', '')
if TARGET_CHATS_STR:
    TARGET_CHATS = [chat.strip() for chat in TARGET_CHATS_STR.split(',') if chat.strip()]
else:
    # 默认配置示例 - 请替换为你要监听的群组
    TARGET_CHATS = [
        # '@example_group',
        # -1001234567890,
    ]

# Webhook URL - 接收消息的 HTTP 接口地址
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:8080/webhook')  # 必须替换

# 日志级别
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================================================
# 日志配置
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
# 全局变量
# ============================================================================

# 存储目标群组的 ID 和名称映射
target_chat_ids = set()
chat_info_cache = {}


# ============================================================================
# 辅助函数
# ============================================================================

async def send_to_webhook(data: Dict[str, Any]) -> None:
    """
    将消息数据发送到 Webhook URL
    
    Args:
        data: 要发送的消息数据字典
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
                    logger.info(f"✓ 消息已发送到 webhook (状态码: {status})")
                else:
                    response_text = await response.text()
                    logger.warning(
                        f"⚠ Webhook 返回非 200 状态码: {status}, "
                        f"响应: {response_text[:200]}"
                    )
    except asyncio.TimeoutError:
        logger.error(f"✗ 发送到 webhook 超时: {WEBHOOK_URL}")
    except aiohttp.ClientError as e:
        logger.error(f"✗ 发送到 webhook 失败 (网络错误): {e}")
    except Exception as e:
        logger.error(f"✗ 发送到 webhook 失败 (未知错误): {e}")


def get_sender_name(sender) -> str:
    """
    获取发送者的名称
    
    优先级: username > first_name + last_name > id
    
    Args:
        sender: Telegram 发送者对象
        
    Returns:
        发送者名称字符串
    """
    if not sender:
        return "Unknown"
    
    # 优先使用 username
    if hasattr(sender, 'username') and sender.username:
        return f"@{sender.username}"
    
    # 其次使用姓名
    if isinstance(sender, User):
        name_parts = []
        if hasattr(sender, 'first_name') and sender.first_name:
            name_parts.append(sender.first_name)
        if hasattr(sender, 'last_name') and sender.last_name:
            name_parts.append(sender.last_name)
        if name_parts:
            return ' '.join(name_parts)
    
    # 最后使用 ID
    if hasattr(sender, 'id'):
        return f"User_{sender.id}"
    
    return "Unknown"


def get_chat_name(chat) -> str:
    """
    获取聊天的名称
    
    Args:
        chat: Telegram 聊天对象
        
    Returns:
        聊天名称字符串
    """
    if not chat:
        return "Unknown Chat"
    
    # 频道或群组
    if isinstance(chat, (Channel, Chat)):
        if hasattr(chat, 'title') and chat.title:
            return chat.title
    
    # 用户
    if isinstance(chat, User):
        return get_sender_name(chat)
    
    # 使用 ID
    if hasattr(chat, 'id'):
        return f"Chat_{chat.id}"
    
    return "Unknown Chat"


async def build_message_data(event) -> Dict[str, Any]:
    """
    从事件中构建消息数据结构
    
    Args:
        event: Telethon 消息事件
        
    Returns:
        包含消息信息的字典
    """
    message = event.message
    
    # 获取发送者信息
    sender = await event.get_sender()
    sender_id = sender.id if sender else 0
    sender_name = get_sender_name(sender)
    
    # 获取聊天信息
    chat = await event.get_chat()
    chat_id = event.chat_id
    chat_name = chat_info_cache.get(chat_id, get_chat_name(chat))
    
    # 构建消息数据
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
# Telegram 客户端和事件处理
# ============================================================================

async def init_target_chats(client: TelegramClient) -> None:
    """
    初始化目标群组列表，解析并获取群组实体
    
    Args:
        client: Telegram 客户端实例
    """
    global target_chat_ids, chat_info_cache
    
    logger.info("正在初始化目标群组列表...")
    
    for chat_identifier in TARGET_CHATS:
        try:
            # 获取群组实体
            entity = await client.get_entity(chat_identifier)
            chat_id = entity.id
            target_chat_ids.add(chat_id)
            
            # 缓存群组信息
            chat_name = get_chat_name(entity)
            chat_info_cache[chat_id] = chat_name
            
            logger.info(f"  ✓ 已添加监听目标: {chat_name} (ID: {chat_id})")
            
        except ValueError as e:
            logger.error(f"  ✗ 无法找到群组: {chat_identifier} - {e}")
        except Exception as e:
            logger.error(f"  ✗ 获取群组信息失败: {chat_identifier} - {e}")
    
    if not target_chat_ids:
        logger.error("⚠ 警告: 没有有效的监听目标！请检查 TARGET_CHATS 配置")
    else:
        logger.info(f"✓ 共初始化 {len(target_chat_ids)} 个监听目标")


async def message_handler(event):
    """
    处理新消息事件
    
    Args:
        event: Telethon 新消息事件
    """
    try:
        chat_id = event.chat_id
        
        # 只处理目标群组的消息
        if chat_id not in target_chat_ids:
            return
        
        message = event.message
        chat_name = chat_info_cache.get(chat_id, "Unknown")
        
        # 构建消息数据
        data = await build_message_data(event)
        
        # 打印简要信息
        logger.info(
            f"📨 收到消息 | 群组: {chat_name} | "
            f"发送者: {data['sender_name']} | "
            f"文本: {data['text'][:50]}{'...' if len(data['text']) > 50 else ''}"
        )
        
        # 发送到 webhook
        await send_to_webhook(data)
        
    except Exception as e:
        logger.error(f"处理消息时出错: {e}", exc_info=True)


# ============================================================================
# 主程序
# ============================================================================

async def main():
    """
    主函数 - 初始化客户端并开始监听
    """
    logger.info("=" * 60)
    logger.info("Telegram Monitor Service 启动中...")
    logger.info("=" * 60)
    
    # 验证配置
    if API_ID == '你的_API_ID' or API_HASH == '你的_API_HASH':
        logger.error("✗ 错误: 请先配置 API_ID 和 API_HASH！")
        logger.error("  从 https://my.telegram.org 获取你的 API 凭证")
        sys.exit(1)
    
    if not TARGET_CHATS:
        logger.error("✗ 错误: 请配置至少一个要监听的群组 (TARGET_CHATS)！")
        sys.exit(1)
    
    if WEBHOOK_URL == 'http://localhost:8080/webhook':
        logger.warning("⚠ 警告: 使用默认的 WEBHOOK_URL，请确保这是你想要的")
    
    logger.info(f"配置信息:")
    logger.info(f"  API ID: {API_ID}")
    logger.info(f"  Session: {SESSION_NAME}.session")
    logger.info(f"  Webhook URL: {WEBHOOK_URL}")
    logger.info(f"  监听目标数: {len(TARGET_CHATS)}")
    logger.info("-" * 60)
    
    # 创建 Telegram 客户端
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        # 启动客户端
        logger.info("正在连接到 Telegram...")
        await client.start()
        logger.info("✓ 已成功连接到 Telegram")
        
        # 获取当前用户信息
        me = await client.get_me()
        logger.info(f"✓ 已登录为: {get_sender_name(me)} (ID: {me.id})")
        
        # 初始化目标群组
        await init_target_chats(client)
        
        # 注册新消息事件处理器
        client.add_event_handler(
            message_handler,
            events.NewMessage()
        )
        
        logger.info("=" * 60)
        logger.info("✓ 服务已启动，正在监听新消息...")
        logger.info("  按 Ctrl+C 停止服务")
        logger.info("=" * 60)
        
        # 保持运行
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，正在停止服务...")
    except Exception as e:
        logger.error(f"✗ 运行时错误: {e}", exc_info=True)
    finally:
        if client.is_connected():
            await client.disconnect()
            logger.info("✓ 已断开连接")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n服务已停止")
    except Exception as e:
        logger.error(f"程序异常退出: {e}", exc_info=True)
        sys.exit(1)
