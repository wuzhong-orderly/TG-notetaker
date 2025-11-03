#!/usr/bin/env python3
"""
简化的 Telegram Bot 测试版本
专门用于调试消息接收问题
"""

import os
import sys
import logging

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from config.config import Config

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理任何类型的消息 - 用于调试"""
    print("\n" + "="*60, flush=True)
    print("🔥 收到更新！", flush=True)
    
    if update.message:
        message = update.message
        print(f"📨 消息类型: {message.chat.type}", flush=True)
        print(f"👤 发送者: {message.from_user.first_name} (@{message.from_user.username})", flush=True)
        print(f"💬 群组: {message.chat.title} (ID: {message.chat.id})", flush=True)
        
        if message.text:
            print(f"📝 内容: '{message.text}'", flush=True)
        else:
            print(f"🎵 媒体消息", flush=True)
        
        print(f"🕒 时间: {message.date}", flush=True)
    
    elif update.edited_message:
        print("✏️ 编辑消息", flush=True)
    elif update.channel_post:
        print("📢 频道消息", flush=True)
    elif update.edited_channel_post:
        print("✏️ 编辑频道消息", flush=True)
    else:
        print("❓ 其他类型更新", flush=True)
    
    print("="*60 + "\n", flush=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    print("🚀 收到 /start 命令", flush=True)
    await update.message.reply_text("Bot 正在运行！发送任何消息测试。")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /test 命令"""
    print("🧪 收到 /test 命令", flush=True)
    message = update.message
    
    info = f"""
测试信息:
- 用户 ID: {message.from_user.id}
- 用户名: @{message.from_user.username}
- 群组 ID: {message.chat.id}
- 群组类型: {message.chat.type}
- 群组标题: {message.chat.title}
"""
    await message.reply_text(info)

def main():
    """主函数"""
    config = Config()
    
    if not config.BOT_TOKEN:
        print("❌ 错误: 请设置 TELEGRAM_BOT_TOKEN")
        return
    
    print("🤖 启动测试 Bot...")
    print(f"📋 Token: {config.BOT_TOKEN[:10]}...")
    print(f"👑 管理员: {config.get_admin_ids()}")
    print("="*50, flush=True)
    
    # 创建应用程序
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # 添加处理器 - 处理所有类型的消息
    application.add_handler(MessageHandler(filters.ALL, handle_any_message))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("test", test_command))
    
    print("✅ Bot 已启动，监听所有消息...", flush=True)
    print("💡 在群组或私聊中发送任何消息进行测试", flush=True)
    print("🔍 使用 /test 命令查看详细信息", flush=True)
    print("-"*50, flush=True)
    
    try:
        # 启动机器人
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        print("\n👋 Bot 已停止")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

if __name__ == '__main__':
    main()