#!/usr/bin/env python3
"""
Bot状态和权限检查工具
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot
from telegram.error import TelegramError
from config.config import Config

async def check_bot_status():
    """检查bot的状态和权限"""
    try:
        config = Config()
        bot = Bot(token=config.BOT_TOKEN)
        
        print("🔍 检查 Bot 状态...")
        print("=" * 50)
        
        # 获取bot信息
        bot_info = await bot.get_me()
        print(f"🤖 Bot信息:")
        print(f"   - 用户名: @{bot_info.username}")
        print(f"   - 显示名: {bot_info.first_name}")
        print(f"   - ID: {bot_info.id}")
        print(f"   - 是否为Bot: {bot_info.is_bot}")
        print(f"   - 支持群组: {bot_info.supports_inline_queries}")
        print()
        
        # 检查webhook状态
        webhook_info = await bot.get_webhook_info()
        print(f"🔗 Webhook状态:")
        print(f"   - URL: {webhook_info.url or '未设置 (使用轮询模式)'}")
        print(f"   - 待处理更新: {webhook_info.pending_update_count}")
        if webhook_info.last_error_date:
            print(f"   - 最后错误: {webhook_info.last_error_message}")
        print()
        
        # 获取最近的更新
        print("📥 检查最近的更新...")
        try:
            updates = await bot.get_updates(limit=5)
            if updates:
                print(f"   - 找到 {len(updates)} 条最近更新:")
                for i, update in enumerate(updates[-3:], 1):  # 只显示最后3条
                    if update.message:
                        chat = update.message.chat
                        user = update.message.from_user
                        print(f"   {i}. Chat ID: {chat.id} | 类型: {chat.type} | 来自: {user.first_name or 'Unknown'}")
                        if chat.type in ['group', 'supergroup']:
                            print(f"      群组名: {chat.title}")
                        print(f"      消息: {update.message.text[:50]}{'...' if len(update.message.text or '') > 50 else ''}")
            else:
                print("   - 没有找到最近的更新")
        except Exception as e:
            print(f"   - 获取更新时出错: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Bot状态检查完成")
        
    except TelegramError as e:
        print(f"❌ Telegram API 错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot_status())