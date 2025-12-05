"""
AI 总结功能使用示例和测试
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from config.config import Config
from src.ai_summary import create_ai_summarizer

async def test_ai_summary():
    """测试 AI 总结功能"""
    print("🤖 测试 AI 总结功能...")
    
    # 检查配置
    if not Config.ENABLE_AI_SUMMARY:
        print("⚠️ AI 总结功能未启用")
        print("💡 请在 .env 文件中设置 ENABLE_AI_SUMMARY=true")
        return
    
    # 创建 AI 总结器
    summarizer = create_ai_summarizer()
    if not summarizer:
        print("❌ 无法创建 AI 总结器")
        return
    
    print(f"✅ AI 总结器创建成功 (提供商: {Config.AI_PROVIDER})")
    
    # 模拟消息数据
    sample_messages = [
        {
            "message_id": 1,
            "chat_id": -1001234567890,
            "chat_title": "测试群组",
            "user_id": 123456789,
            "username": "user1",
            "first_name": "张三",
            "last_name": "",
            "message_text": "大家好，今天我们讨论一下项目进度",
            "message_type": "text",
            "timestamp": "2024-01-01 10:00:00"
        },
        {
            "message_id": 2,
            "chat_id": -1001234567890,
            "chat_title": "测试群组",
            "user_id": 987654321,
            "username": "user2",
            "first_name": "李四",
            "last_name": "",
            "message_text": "好的，我这边已经完成了用户界面的设计",
            "message_type": "text",
            "timestamp": "2024-01-01 10:05:00"
        },
        {
            "message_id": 3,
            "chat_id": -1001234567890,
            "chat_title": "测试群组",
            "user_id": 555666777,
            "username": "user3",
            "first_name": "王五",
            "last_name": "",
            "message_text": "数据库部分还需要一些时间，预计明天完成",
            "message_type": "text",
            "timestamp": "2024-01-01 10:10:00"
        },
        {
            "message_id": 4,
            "chat_id": -1001234567890,
            "chat_title": "测试群组",
            "user_id": 123456789,
            "username": "user1",
            "first_name": "张三",
            "last_name": "",
            "message_text": "那我们计划后天进行集成测试，大家觉得怎么样？",
            "message_type": "text",
            "timestamp": "2024-01-01 10:15:00"
        },
        {
            "message_id": 5,
            "chat_id": -1001234567890,
            "chat_title": "测试群组",
            "user_id": 987654321,
            "username": "user2",
            "first_name": "李四",
            "last_name": "",
            "message_text": "同意，我会准备好测试用例",
            "message_type": "text",
            "timestamp": "2024-01-01 10:20:00"
        }
    ]
    
    try:
        print("\n📝 生成测试总结...")
        
        # 生成总结
        summary = await summarizer.provider.generate_summary(
            sample_messages, 
            "测试群组"
        )
        
        print("✅ 总结生成成功！")
        print("\n" + "="*50)
        print("📊 AI 生成的总结:")
        print("="*50)
        print(summary)
        print("="*50)
        
        # 格式化用于 Telegram 发送
        formatted = summarizer.format_summary_for_telegram(
            summary, 
            "测试群组", 
            datetime.now(), 
            len(sample_messages)
        )
        
        print("\n📱 Telegram 格式化总结:")
        print("-"*30)
        print(formatted)
        print("-"*30)
        
    except Exception as e:
        print(f"❌ 生成总结失败: {e}")
        if "API Key" in str(e):
            print("💡 请检查 AI API Key 配置")

def check_ai_config():
    """检查 AI 配置"""
    print("🔧 检查 AI 配置...")
    
    config_items = [
        ("ENABLE_AI_SUMMARY", Config.ENABLE_AI_SUMMARY),
        ("AI_PROVIDER", Config.AI_PROVIDER),
        ("OPENAI_API_KEY", "已设置" if Config.OPENAI_API_KEY else "未设置"),
        ("OPENAI_MODEL", Config.OPENAI_MODEL),
        ("SUMMARY_LANGUAGE", Config.SUMMARY_LANGUAGE),
        ("SUMMARY_LENGTH", Config.SUMMARY_LENGTH),
        ("SUMMARY_STYLE", Config.SUMMARY_STYLE),
        ("AUTO_SUMMARY_TIME", Config.AUTO_SUMMARY_TIME),
        ("MIN_MESSAGES_FOR_SUMMARY", Config.MIN_MESSAGES_FOR_SUMMARY),
    ]
    
    for key, value in config_items:
        print(f"  {key}: {value}")
    
    # 检查必要的配置
    issues = []
    if not Config.ENABLE_AI_SUMMARY:
        issues.append("AI 总结功能未启用")
    
    if Config.AI_PROVIDER == 'openai' and not Config.OPENAI_API_KEY:
        issues.append("OpenAI API Key 未设置")
    elif Config.AI_PROVIDER == 'claude' and not Config.ANTHROPIC_API_KEY:
        issues.append("Anthropic API Key 未设置")
    
    if issues:
        print("\n⚠️ 配置问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ AI 配置检查通过")
        return True

async def main():
    """主函数"""
    print("🧪 AI 总结功能测试工具")
    print("="*50)
    
    # 加载环境变量
    try:
        from dotenv import load_dotenv
        env_file = os.path.join(project_root, '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"✅ 已加载环境变量: {env_file}")
        else:
            print(f"⚠️ 环境变量文件不存在: {env_file}")
    except ImportError:
        print("⚠️ python-dotenv 未安装，跳过环境变量加载")
    
    # 检查配置
    if not check_ai_config():
        print("\n💡 解决方案:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中设置 ENABLE_AI_SUMMARY=true")
        print("3. 设置相应的 AI API Key")
        return
    
    # 测试 AI 总结
    await test_ai_summary()
    
    print("\n🎉 测试完成！")
    print("\n📚 使用说明:")
    print("1. 在群组中使用 /summary 命令手动生成总结")
    print("2. 使用 /summary_history 查看历史总结")
    print("3. 机器人会在每天设定时间自动生成总结")

if __name__ == "__main__":
    asyncio.run(main())