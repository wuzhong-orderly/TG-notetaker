#!/usr/bin/env python3
"""
诊断AI总结功能
"""
import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from ai_summary import create_ai_summarizer

async def diagnose_ai_summary():
    """诊断AI总结功能"""
    print("🔍 开始诊断AI总结功能...")
    print("="*60)
    
    # 1. 检查配置
    print("\n1️⃣ 检查配置...")
    config = Config()
    
    print(f"   ✓ AI总结功能: {'启用' if config.ENABLE_AI_SUMMARY else '❌ 未启用'}")
    print(f"   ✓ AI提供商: {config.AI_PROVIDER}")
    print(f"   ✓ OpenAI模型: {config.OPENAI_MODEL}")
    print(f"   ✓ API密钥: {config.OPENAI_API_KEY[:20] if config.OPENAI_API_KEY else '❌ 未设置'}...")
    
    if not config.ENABLE_AI_SUMMARY:
        print("\n❌ AI总结功能未启用")
        return False
    
    if not config.OPENAI_API_KEY:
        print("\n❌ OpenAI API密钥未设置")
        return False
    
    # 2. 创建AI总结器
    print("\n2️⃣ 创建AI总结器...")
    try:
        ai_summarizer = create_ai_summarizer()
        if ai_summarizer:
            print("   ✅ AI总结器创建成功")
        else:
            print("   ❌ AI总结器创建失败")
            return False
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        return False
    
    # 3. 检查消息数据
    print("\n3️⃣ 检查消息数据...")
    chat_id = -5048705007  # 测试群组
    
    try:
        # 获取今天的消息
        today = datetime.now()
        messages_today = ai_summarizer.get_messages_for_24h(chat_id)
        print(f"   ✓ 过去24小时消息数: {len(messages_today)}")
        
        if len(messages_today) == 0:
            print("   ⚠️  没有找到消息")
            print("   💡 请确保bot已记录了消息")
            return False
        
        if len(messages_today) < config.MIN_MESSAGES_FOR_SUMMARY:
            print(f"   ⚠️  消息数量不足 (需要至少{config.MIN_MESSAGES_FOR_SUMMARY}条)")
            return False
        
        print(f"   ✓ 消息数量充足 ({len(messages_today)} >= {config.MIN_MESSAGES_FOR_SUMMARY})")
        
        # 显示部分消息
        print(f"\n   📝 消息示例（前3条）:")
        for i, msg in enumerate(messages_today[:3]):
            print(f"      {i+1}. {msg.get('timestamp', 'N/A')}: {msg.get('text', 'N/A')[:50]}")
    
    except Exception as e:
        print(f"   ❌ 获取消息失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 测试API连接
    print("\n4️⃣ 测试OpenAI API连接...")
    try:
        import aiohttp
        
        # 构建测试提示
        test_prompt = "请用一句话总结：今天天气很好。"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {config.OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.OPENAI_MODEL,
                'messages': [
                    {'role': 'user', 'content': test_prompt}
                ],
                'max_completion_tokens': 100
            }
            
            print(f"   📡 正在连接 {config.OPENAI_BASE_URL}/chat/completions...")
            
            async with session.post(
                f'{config.OPENAI_BASE_URL}/chat/completions',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"   📊 响应状态: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ API连接成功")
                    print(f"   ✓ 模型: {result.get('model', 'N/A')}")
                    print(f"   ✓ 测试响应: {result['choices'][0]['message']['content'][:50]}...")
                else:
                    error_text = await response.text()
                    print(f"   ❌ API请求失败: {response.status}")
                    print(f"   📄 错误详情: {error_text[:200]}")
                    return False
    
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 测试生成总结
    print("\n5️⃣ 测试生成总结...")
    try:
        print("   ⏳ 正在生成总结...")
        summary = await ai_summarizer.generate_today_summary(chat_id)
        
        if summary:
            print(f"   ✅ 总结生成成功!")
            print(f"   📝 总结长度: {len(summary)} 字符")
            print(f"   📄 总结预览:\n")
            print("   " + "-"*56)
            print("   " + summary[:200].replace('\n', '\n   '))
            if len(summary) > 200:
                print("   ...")
            print("   " + "-"*56)
            return True
        else:
            print("   ❌ 总结生成失败（返回None）")
            return False
    
    except Exception as e:
        print(f"   ❌ 生成总结时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(diagnose_ai_summary())
        print("\n" + "="*60)
        if result:
            print("✅ 诊断完成：AI总结功能正常")
        else:
            print("❌ 诊断完成：AI总结功能存在问题")
        print("="*60)
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
