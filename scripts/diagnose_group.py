#!/usr/bin/env python3
"""
群组权限诊断工具
检查 Bot 在群组中的权限和设置
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from config.config import Config

async def diagnose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """诊断群组权限"""
    message = update.message
    if not message:
        return
    
    print("\n" + "="*60, flush=True)
    print("🔍 群组诊断信息", flush=True)
    print("="*60, flush=True)
    
    # 基本信息
    print(f"📋 聊天类型: {message.chat.type}", flush=True)
    print(f"📋 聊天ID: {message.chat.id}", flush=True)
    print(f"📋 聊天标题: {message.chat.title}", flush=True)
    print(f"👤 发送者: {message.from_user.first_name} (@{message.from_user.username})", flush=True)
    print(f"👤 用户ID: {message.from_user.id}", flush=True)
    
    try:
        # 获取 Bot 信息
        bot_member = await context.bot.get_chat_member(message.chat.id, context.bot.id)
        print(f"🤖 Bot 状态: {bot_member.status}", flush=True)
        
        if hasattr(bot_member, 'can_read_all_group_messages'):
            print(f"📖 可以读取所有消息: {bot_member.can_read_all_group_messages}", flush=True)
        
        # 获取聊天信息
        chat_info = await context.bot.get_chat(message.chat.id)
        print(f"📊 群组成员数: {chat_info.get_member_count()}", flush=True)
        
        if hasattr(chat_info, 'permissions'):
            perms = chat_info.permissions
            print(f"🔒 群组权限:", flush=True)
            print(f"   - 发送消息: {perms.can_send_messages}", flush=True)
            print(f"   - 发送媒体: {perms.can_send_media_messages}", flush=True)
            
    except Exception as e:
        print(f"❌ 获取权限信息失败: {e}", flush=True)
    
    print("="*60, flush=True)
    
    # 发送回复
    response = f"""
🔍 诊断完成！

聊天类型: {message.chat.type}
聊天ID: {message.chat.id}
Bot ID: {context.bot.id}

请检查终端输出获取详细信息。

💡 如果 Bot 无法接收普通消息，请：
1. 确保 Bot 是群组管理员
2. 或者在群组设置中关闭"群组隐私"
3. 或者让 Bot 只响应命令和@提及
"""
    
    await message.reply_text(response)

async def handle_any_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理任何更新"""
    print("\n" + "🔥 收到更新！", flush=True)
    
    if update.message:
        message = update.message
        print(f"📨 消息 - 聊天类型: {message.chat.type}", flush=True)
        print(f"👤 发送者: {message.from_user.first_name}", flush=True)
        print(f"💬 群组: {message.chat.title} (ID: {message.chat.id})", flush=True)
        
        if message.text:
            print(f"📝 内容: '{message.text}'", flush=True)
            
            # 如果是群组消息，额外打印信息
            if message.chat.type in ['group', 'supergroup']:
                print("✅ 这是一条群组消息！Bot 可以接收群组消息。", flush=True)
        
        print("-" * 40, flush=True)

async def test_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """测试群组命令"""
    message = update.message
    
    print("🧪 收到群组测试命令", flush=True)
    
    if message.chat.type in ['group', 'supergroup']:
        await message.reply_text("✅ Bot 可以在群组中接收和发送消息！")
        print("✅ 群组命令响应成功", flush=True)
    else:
        await message.reply_text("这是私聊，请在群组中测试")

def main():
    """主函数"""
    config = Config()
    
    print("🔍 启动群组权限诊断工具...")
    print("="*50, flush=True)
    
    # 创建应用程序
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("diagnose", diagnose_command))
    application.add_handler(CommandHandler("testgroup", test_group_command))
    application.add_handler(MessageHandler(filters.ALL, handle_any_update))
    
    print("✅ 诊断工具已启动", flush=True)
    print("📋 可用命令:", flush=True)
    print("   /diagnose - 诊断群组权限", flush=True)
    print("   /testgroup - 测试群组功能", flush=True)
    print("💡 请在群组中发送消息或命令进行测试", flush=True)
    print("-"*50, flush=True)
    
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        print("\n👋 诊断工具已停止")

if __name__ == '__main__':
    main()