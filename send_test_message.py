#!/usr/bin/env python3
"""
发送测试消息到目标群组
"""
import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from telegram import Bot

async def send_test_message():
    """发送测试消息到配置的目标群组"""
    print("🔧 准备发送测试消息...")
    
    # 加载配置
    config = Config()
    if not config.validate():
        print("❌ 配置验证失败")
        return
    
    # 获取目标群组ID
    target_chat_id = config.get_summary_report_chat_id()
    
    if target_chat_id == 0:
        print("❌ 未设置目标群组ID")
        print("💡 请在 .env 文件中设置 SUMMARY_REPORT_CHAT_ID")
        return
    
    print(f"📊 配置信息：")
    print(f"   - Bot Token: {config.BOT_TOKEN[:20]}...")
    print(f"   - 目标群组ID: {target_chat_id}")
    print(f"   - 发送功能: {'启用' if config.SEND_SUMMARY_TO_CHAT else '未启用'}")
    
    # 创建Bot实例
    bot = Bot(token=config.BOT_TOKEN)
    
    # 准备测试消息
    test_message = f"""
🧪 **测试消息**

这是一条来自 Telegram Note Taker Bot 的测试消息。

📋 测试信息：
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 目标群组ID: {target_chat_id}
- 消息类型: 配置测试

✅ 如果你看到这条消息，说明bot已成功配置并可以发送消息到此群组！

---
💡 接下来，每日00:00会自动发送AI总结到此群组。
    """
    
    try:
        print("\n📤 正在发送测试消息...")
        
        # 发送消息
        message = await bot.send_message(
            chat_id=target_chat_id,
            text=test_message,
            parse_mode='Markdown'
        )
        
        print("✅ 测试消息发送成功！")
        print(f"   - 消息ID: {message.message_id}")
        print(f"   - 群组: {message.chat.title or message.chat.id}")
        print(f"   - 类型: {message.chat.type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        print("\n🔍 可能的原因：")
        print("   1. Bot未加入目标群组")
        print("   2. Bot在群组中没有发送消息权限")
        print("   3. 群组ID不正确")
        print("\n💡 解决方法：")
        print("   1. 将bot添加到目标群组")
        print("   2. 确保bot有发送消息权限")
        print("   3. 使用 get_chat_id.py 重新获取群组ID")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(send_test_message())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
