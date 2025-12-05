#!/usr/bin/env python3
"""
获取群组ID的辅助脚本
将bot添加到群组后，运行此脚本并在群组中发送消息，即可查看群组ID
"""
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

class ChatIDGetter:
    """获取Chat ID的工具"""
    
    def __init__(self):
        self.config = Config()
        
        if not self.config.validate():
            sys.exit(1)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息并显示chat信息"""
        message = update.message
        if not message:
            return
        
        chat = message.chat
        user = message.from_user
        
        print("\n" + "="*60)
        print("📱 消息信息：")
        print("-"*60)
        
        # Chat信息
        if chat.type == 'private':
            print(f"💬 聊天类型: 私聊")
            print(f"👤 用户ID: {chat.id}")
            print(f"👤 用户名: {user.username or 'N/A'}")
            print(f"👤 姓名: {user.first_name} {user.last_name or ''}")
        else:
            print(f"💬 聊天类型: {chat.type}")
            print(f"🆔 群组ID: {chat.id}")
            print(f"📛 群组名称: {chat.title or 'N/A'}")
            if chat.username:
                print(f"🔗 群组用户名: @{chat.username}")
        
        print("-"*60)
        print(f"👤 发送者ID: {user.id}")
        print(f"👤 发送者: {user.username or user.first_name}")
        print(f"💬 消息: {message.text[:50] if message.text else '(非文本消息)'}")
        print("="*60)
        
        # 如果是群组，给出配置建议
        if chat.type in ['group', 'supergroup']:
            print("\n✅ 要将总结发送到此群组，请在 .env 文件中设置：")
            print(f"   SUMMARY_REPORT_CHAT_ID={chat.id}")
            print()
    
    def run(self):
        """运行bot"""
        print("🤖 Chat ID 获取工具已启动...")
        print("📝 说明：")
        print("   1. 将bot添加到你想要的群组")
        print("   2. 在群组中发送任意消息")
        print("   3. 查看下方显示的群组ID")
        print("   4. 按 Ctrl+C 停止")
        print("\n等待消息中...\n")
        
        # 创建应用程序
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # 添加消息处理器
        application.add_handler(MessageHandler(
            filters.ALL,
            self.handle_message
        ))
        
        # 运行bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    getter = ChatIDGetter()
    try:
        getter.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
