#!/usr/bin/env python3
"""
测试今日总结功能
"""
import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from ai_summary import create_ai_summarizer
from scheduler import TaskScheduler

async def test_today_summary():
    """测试今日总结功能"""
    print("🔧 测试今日总结功能...")
    
    # 初始化配置
    config = Config()
    if not config.validate():
        print("❌ 配置验证失败")
        return
    
    # 创建AI总结器
    ai_summarizer = create_ai_summarizer()
    if not ai_summarizer:
        print("❌ AI总结器初始化失败")
        return
    
    # 创建调度器
    scheduler = TaskScheduler()
    
    # 测试群组ID (使用已知的测试群组)
    test_chat_id = 5048705007
    
    print(f"📊 测试群组: {test_chat_id}")
    
    # 测试获取过去24小时的消息
    print("1. 测试获取过去24小时消息...")
    messages_24h = ai_summarizer.get_messages_for_24h(test_chat_id)
    print(f"   找到 {len(messages_24h)} 条过去24小时的消息")
    
    if len(messages_24h) > 0:
        print(f"   最早消息时间: {messages_24h[0].get('timestamp', 'N/A')}")
        print(f"   最晚消息时间: {messages_24h[-1].get('timestamp', 'N/A')}")
    
    # 测试生成今日总结
    if len(messages_24h) >= config.MIN_MESSAGES_FOR_SUMMARY:
        print("2. 测试生成今日总结...")
        summary = await scheduler.generate_today_summary(test_chat_id)
        if summary:
            print("✅ 今日总结生成成功!")
            print(f"   总结长度: {len(summary)} 字符")
            print(f"   总结预览: {summary[:100]}...")
            
            # 检查保存的文件
            today = datetime.now()
            date_str = today.strftime('%Y%m%d')
            filename = f"summary_chat_{abs(test_chat_id)}_{date_str}.json"
            filepath = os.path.join(config.SUMMARY_DIR, filename)
            
            if os.path.exists(filepath):
                print(f"✅ 总结文件已保存: {filename}")
            else:
                print(f"❌ 总结文件未找到: {filename}")
        else:
            print("❌ 今日总结生成失败")
    else:
        print(f"⚠️  消息数量不足 ({len(messages_24h)} < {config.MIN_MESSAGES_FOR_SUMMARY})，跳过总结生成测试")
    
    print("🎉 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_today_summary())