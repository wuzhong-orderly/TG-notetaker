#!/usr/bin/env python3
"""
独立测试24小时实时总结功能
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
import traceback

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from config.config import Config
from ai_summary import create_ai_summarizer

async def test_24h_summary():
    """测试24小时总结功能"""
    print("="*80)
    print("🔍 测试24小时实时总结功能")
    print("="*80)
    
    # 1. 初始化配置
    print("\n📋 步骤1: 初始化配置")
    config = Config()
    print(f"   ✓ AI功能启用: {config.ENABLE_AI_SUMMARY}")
    print(f"   ✓ AI提供商: {config.AI_PROVIDER}")
    print(f"   ✓ 模型: {config.OPENAI_MODEL}")
    print(f"   ✓ API密钥: {config.OPENAI_API_KEY[:30]}...")
    print(f"   ✓ 最小消息数: {config.MIN_MESSAGES_FOR_SUMMARY}")
    
    # 2. 创建AI总结器
    print("\n🤖 步骤2: 创建AI总结器")
    try:
        ai_summarizer = create_ai_summarizer()
        if not ai_summarizer:
            print("   ❌ AI总结器创建失败")
            return False
        print("   ✓ AI总结器创建成功")
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        traceback.print_exc()
        return False
    
    # 3. 测试群组ID
    test_chat_id = 5048705007
    print(f"\n📱 步骤3: 测试群组 ID={test_chat_id}")
    
    # 4. 测试获取过去24小时消息
    print("\n📨 步骤4: 获取过去24小时的消息")
    try:
        messages = ai_summarizer.get_messages_for_24h(test_chat_id)
        print(f"   ✓ 获取到 {len(messages)} 条消息")
        
        if len(messages) == 0:
            print("   ⚠️  没有消息，检查数据文件...")
            import json
            data_dir = config.DATA_DIR
            print(f"   📁 数据目录: {data_dir}")
            
            # 列出所有相关文件
            for filename in os.listdir(data_dir):
                if str(test_chat_id) in filename:
                    print(f"   📄 找到文件: {filename}")
                    filepath = os.path.join(data_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_messages = json.load(f)
                        print(f"      - 包含 {len(file_messages)} 条消息")
                        if len(file_messages) > 0:
                            print(f"      - 第一条: {file_messages[0].get('timestamp', 'N/A')}")
            return False
        
        # 显示消息详情
        print(f"\n   📝 消息示例（前5条）:")
        for i, msg in enumerate(messages[:5]):
            timestamp = msg.get('timestamp', 'N/A')
            text = msg.get('message_text', msg.get('text', msg.get('caption', 'N/A')))
            user = msg.get('from_user', msg.get('username', msg.get('first_name', 'N/A')))
            print(f"      {i+1}. [{timestamp}] {user}: {text[:50] if text and text != 'N/A' else '(无文本)'}")
        
        # 显示消息的完整字段
        if len(messages) > 0:
            print(f"\n   🔍 第一条消息的所有字段:")
            for key, value in messages[0].items():
                print(f"      - {key}: {str(value)[:100]}")
        
        if len(messages) < config.MIN_MESSAGES_FOR_SUMMARY:
            print(f"   ⚠️  消息数不足 ({len(messages)} < {config.MIN_MESSAGES_FOR_SUMMARY})")
            return False
        
    except Exception as e:
        print(f"   ❌ 获取消息失败: {e}")
        traceback.print_exc()
        return False
    
    # 5. 测试生成今日总结
    print("\n🎯 步骤5: 调用generate_today_summary")
    try:
        print("   ⏳ 开始生成总结...")
        summary = await ai_summarizer.generate_today_summary(test_chat_id)
        
        if summary:
            print(f"   ✅ 总结生成成功!")
            print(f"   📊 总结长度: {len(summary)} 字符")
            print(f"\n   📄 总结内容:")
            print("   " + "-"*76)
            for line in summary.split('\n')[:15]:  # 显示前15行
                print(f"   {line}")
            if len(summary.split('\n')) > 15:
                print("   ...")
            print("   " + "-"*76)
            return True
        else:
            print("   ❌ 总结生成失败（返回None）")
            print("\n   🔍 检查详细日志...")
            return False
            
    except Exception as e:
        print(f"   ❌ 生成总结时出错: {e}")
        print("\n   📋 详细错误信息:")
        traceback.print_exc()
        return False
    
    # 6. 另外测试：直接调用provider
    print("\n🧪 步骤6: 直接测试AI Provider")
    try:
        chat_title = messages[0].get('chat_title', 'Test Chat') if messages else 'Test Chat'
        print(f"   群组标题: {chat_title}")
        print(f"   准备发送给AI的消息数: {len(messages)}")
        
        print("\n   ⏳ 调用 provider.generate_summary...")
        summary = await ai_summarizer.provider.generate_summary(messages, chat_title)
        
        if summary:
            print(f"   ✅ Provider返回成功!")
            print(f"   📊 返回长度: {len(summary)} 字符")
            print(f"   📄 内容预览: {summary[:200]}...")
        else:
            print(f"   ❌ Provider返回None")
        
    except Exception as e:
        print(f"   ❌ Provider调用失败: {e}")
        print("\n   📋 详细错误:")
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("开始测试...")
    print("="*80 + "\n")
    
    try:
        result = asyncio.run(test_24h_summary())
        
        print("\n" + "="*80)
        if result:
            print("✅ 测试通过：24小时总结功能正常")
        else:
            print("❌ 测试失败：24小时总结功能存在问题")
        print("="*80)
        
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        print("\n📋 完整错误堆栈:")
        traceback.print_exc()
        sys.exit(1)
