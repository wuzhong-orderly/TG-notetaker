#!/usr/bin/env python3
"""
简单的AI总结功能测试
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config

def test_ai_config():
    """测试AI配置"""
    print("🤖 AI总结功能配置检查")
    print("=" * 50)
    
    config = Config()
    
    print("📋 当前配置:")
    print(f"   ✅ AI总结启用: {config.ENABLE_AI_SUMMARY}")
    print(f"   🤖 AI提供商: {config.AI_PROVIDER}")
    print(f"   🧠 模型: {config.OPENAI_MODEL}")
    print(f"   🌍 语言: {config.SUMMARY_LANGUAGE}")
    print(f"   📏 长度: {config.SUMMARY_LENGTH}")
    print(f"   🎨 风格: {config.SUMMARY_STYLE}")
    print(f"   📊 最小消息数: {config.MIN_MESSAGES_FOR_SUMMARY}")
    print(f"   📤 发送到群组: {config.SEND_SUMMARY_TO_CHAT}")
    print()
    
    # 检查API密钥
    if config.AI_PROVIDER == 'openai':
        has_key = config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here'
        print(f"   🔑 OpenAI API密钥: {'已设置' if has_key else '未设置'}")
        
        if not has_key:
            print("\n⚠️  需要设置OpenAI API密钥才能使用真实AI总结")
            print("💡 在.env文件中设置: OPENAI_API_KEY=你的密钥")
    
    return config

def create_mock_summary(messages):
    """创建模拟总结"""
    if not messages:
        return "📭 今日无消息记录"
    
    # 统计信息
    total_messages = len(messages)
    users = {}
    topics = []
    
    for msg in messages:
        username = msg.get('first_name', 'Unknown')
        if username not in users:
            users[username] = 0
        users[username] += 1
        
        # 提取一些关键词作为话题
        text = msg.get('message_text', '').lower()
        if 'test' in text or 'hello' in text or 'hi' in text:
            topics.append('问候和测试')
    
    # 生成总结
    summary = f"""
📊 **群组对话总结 - {datetime.now().strftime('%Y年%m月%d日')}**

• **消息统计**:
  - 总消息数: {total_messages}条
  - 活跃用户: {len(users)}位

• **用户活跃度**:
"""
    
    for user, count in users.items():
        summary += f"  - {user}: {count}条消息\n"
    
    if topics:
        summary += f"\n• **主要话题**: {', '.join(set(topics))}\n"
    
    summary += f"""
• **时间范围**: {messages[0].get('timestamp', 'Unknown')} - {messages[-1].get('timestamp', 'Unknown')}

📝 *这是模拟总结，实际AI总结会更详细和智能*
"""
    
    return summary.strip()

def load_today_messages():
    """加载今天的消息"""
    today = datetime.now().strftime('%Y%m%d')
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    if not os.path.exists(data_dir):
        print("❌ 数据目录不存在")
        return {}
    
    all_messages = {}
    
    # 查找今天的消息文件
    for filename in os.listdir(data_dir):
        if filename.endswith(f'{today}.json'):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    chat_id = filename.split('_')[1]
                    all_messages[chat_id] = messages
            except Exception as e:
                print(f"❌ 读取文件 {filename} 失败: {e}")
    
    return all_messages

def main():
    """主函数"""
    # 检查配置
    config = test_ai_config()
    
    # 加载消息
    print("\n📁 加载今天的消息...")
    all_messages = load_today_messages()
    
    if not all_messages:
        print("❌ 没有找到今天的消息文件")
        return
    
    print(f"📊 找到 {len(all_messages)} 个群组的消息")
    
    # 为每个群组生成总结
    for chat_id, messages in all_messages.items():
        print(f"\n🔍 处理群组 {chat_id}...")
        print(f"📨 消息数量: {len(messages)}")
        
        if len(messages) < config.MIN_MESSAGES_FOR_SUMMARY:
            print(f"⏭️  消息数量不足(最少需要{config.MIN_MESSAGES_FOR_SUMMARY}条)")
            continue
        
        # 生成总结
        print("🤖 生成总结...")
        summary = create_mock_summary(messages)
        
        print("\n" + "="*50)
        print("📄 AI总结结果:")
        print("="*50)
        print(summary)
        print("="*50)
    
    print("\n✅ 总结完成!")
    print("\n💡 要使用真实AI总结:")
    print("1. 获取OpenAI API密钥")
    print("2. 在.env文件中设置 OPENAI_API_KEY")
    print("3. 使用 /summary 命令或等待自动总结")

if __name__ == "__main__":
    main()