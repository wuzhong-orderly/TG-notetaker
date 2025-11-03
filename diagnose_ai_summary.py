#!/usr/bin/env python3
"""
AI总结功能诊断和测试工具
"""

import sys
import os
import json
from datetime import datetime, timedelta
import asyncio

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.storage import MessageStorage
from src.ai_summary import AISummarizer

def check_data_availability():
    """检查可用的数据"""
    print("📁 数据可用性检查")
    print("=" * 50)
    
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    if not os.path.exists(data_dir):
        print("❌ 数据目录不存在")
        return {}
    
    # 列出所有消息文件
    message_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f.startswith('chat_')]
    
    if not message_files:
        print("❌ 没有找到任何消息文件")
        return {}
    
    print(f"📊 找到 {len(message_files)} 个消息文件:")
    
    data_by_date = {}
    
    for filename in sorted(message_files):
        # 解析文件名: chat_ID_YYYYMMDD.json
        parts = filename.replace('.json', '').split('_')
        if len(parts) >= 3:
            chat_id = parts[1]
            date_str = parts[2]
            
            # 格式化日期
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                formatted_date = date_obj.strftime('%Y-%m-%d')
                
                if formatted_date not in data_by_date:
                    data_by_date[formatted_date] = []
                
                # 读取消息数量
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        message_count = len(messages)
                        
                        data_by_date[formatted_date].append({
                            'chat_id': chat_id,
                            'filename': filename,
                            'message_count': message_count
                        })
                        
                        print(f"   📅 {formatted_date} - 群组 {chat_id}: {message_count} 条消息")
                        
                except Exception as e:
                    print(f"   ❌ 无法读取 {filename}: {e}")
                    
            except ValueError:
                print(f"   ⚠️ 无法解析日期: {filename}")
    
    return data_by_date

def check_summaries():
    """检查已生成的总结"""
    print("\n📄 已生成的总结检查")
    print("=" * 50)
    
    summaries_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'summaries')
    
    if not os.path.exists(summaries_dir):
        print("📭 没有总结目录")
        return
    
    summary_files = [f for f in os.listdir(summaries_dir) if f.endswith('.md')]
    
    if not summary_files:
        print("📭 没有找到已生成的总结")
        return
    
    print(f"📊 找到 {len(summary_files)} 个总结文件:")
    
    for filename in sorted(summary_files):
        print(f"   📄 {filename}")

async def test_summary_generation(target_date=None):
    """测试总结生成"""
    print(f"\n🤖 测试总结生成")
    print("=" * 50)
    
    config = Config()
    
    if not config.ENABLE_AI_SUMMARY:
        print("❌ AI总结功能未启用")
        return False
    
    # 使用今天的日期如果没有指定
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"🎯 目标日期: {target_date}")
    
    try:
        storage = MessageStorage()
        summarizer = AISummarizer()
        
        # 查找该日期的所有群组消息
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        date_str = target_date.replace('-', '')
        
        chat_files = []
        for filename in os.listdir(data_dir):
            if filename.endswith(f'{date_str}.json') and filename.startswith('chat_'):
                chat_files.append(filename)
        
        if not chat_files:
            print(f"❌ 没有找到 {target_date} 的消息文件")
            return False
        
        print(f"📁 找到 {len(chat_files)} 个群组的消息文件")
        
        total_summaries = 0
        
        for filename in chat_files:
            chat_id = filename.split('_')[1]
            print(f"\n🔍 处理群组 {chat_id}...")
            
            # 加载消息
            messages = storage.load_messages(int(chat_id), target_date)
            print(f"   📨 消息数量: {len(messages)}")
            
            if len(messages) < config.MIN_MESSAGES_FOR_SUMMARY:
                print(f"   ⏭️ 消息数量不足(最少需要 {config.MIN_MESSAGES_FOR_SUMMARY} 条)")
                continue
            
            # 生成总结
            print("   🤖 正在生成AI总结...")
            try:
                summary = await summarizer.generate_summary(messages, target_date)
                
                if summary:
                    print("   ✅ 总结生成成功!")
                    print(f"   📄 总结长度: {len(summary)} 字符")
                    print("   📄 总结预览:")
                    print("   " + "-" * 30)
                    # 显示前200个字符
                    preview = summary[:200] + "..." if len(summary) > 200 else summary
                    for line in preview.split('\n'):
                        print(f"   {line}")
                    print("   " + "-" * 30)
                    total_summaries += 1
                else:
                    print("   ❌ 总结生成失败")
                    
            except Exception as e:
                print(f"   ❌ 生成总结时出错: {e}")
        
        print(f"\n✅ 完成! 成功生成 {total_summaries} 个总结")
        return total_summaries > 0
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Telegram Note Taker AI总结诊断工具")
    print("=" * 60)
    
    # 检查配置
    config = Config()
    print("⚙️ 配置检查:")
    print(f"   - AI总结启用: {config.ENABLE_AI_SUMMARY}")
    print(f"   - AI提供商: {config.AI_PROVIDER}")
    print(f"   - 最小消息数: {config.MIN_MESSAGES_FOR_SUMMARY}")
    print(f"   - API密钥: {'已设置' if config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here' else '未设置'}")
    
    # 检查数据可用性
    data_by_date = check_data_availability()
    
    # 检查已有总结
    check_summaries()
    
    # 显示可用日期
    if data_by_date:
        print(f"\n📅 可以生成总结的日期:")
        for date, chats in data_by_date.items():
            total_messages = sum(chat['message_count'] for chat in chats)
            sufficient_chats = len([chat for chat in chats if chat['message_count'] >= config.MIN_MESSAGES_FOR_SUMMARY])
            print(f"   - {date}: {total_messages} 条消息，{sufficient_chats} 个群组满足要求")
    
    # 提供建议
    print(f"\n💡 建议:")
    if not data_by_date:
        print("   - 首先让bot记录一些群组消息")
        print("   - 确保群组中有足够的对话")
    else:
        available_dates = list(data_by_date.keys())
        print(f"   - 可以尝试生成这些日期的总结: {', '.join(available_dates)}")
        print("   - 使用命令: /summary 或 /summary YYYY-MM-DD")
    
    # 测试今天的总结生成
    today = datetime.now().strftime('%Y-%m-%d')
    if today in data_by_date:
        print(f"\n🚀 测试生成今天({today})的总结...")
        try:
            success = asyncio.run(test_summary_generation(today))
            if success:
                print("✅ 测试成功! AI总结功能正常工作")
            else:
                print("❌ 测试失败，请检查配置和数据")
        except Exception as e:
            print(f"❌ 测试出错: {e}")

if __name__ == "__main__":
    main()