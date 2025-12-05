#!/usr/bin/env python3
"""
生成最近可用数据的AI总结
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config
from src.storage import MessageStorage
from src.ai_summary import AISummarizer

async def generate_available_summaries():
    """生成所有可用数据的总结"""
    print("🤖 生成最近可用数据的AI总结")
    print("=" * 60)
    
    try:
        config = Config()
        
        # 检查AI配置
        if not config.ENABLE_AI_SUMMARY:
            print("❌ AI总结功能未启用")
            return
            
        print(f"✅ AI总结已启用 (提供商: {config.AI_PROVIDER})")
        print(f"📊 最小消息数要求: {config.MIN_MESSAGES_FOR_SUMMARY}")
        print()
        
        # 初始化组件
        storage = MessageStorage()
        summarizer = AISummarizer()
        
        # 扫描数据目录
        data_dir = Path(__file__).parent / 'data'
        if not data_dir.exists():
            print("❌ 数据目录不存在")
            return
            
        # 查找所有消息文件
        message_files = list(data_dir.glob("chat_*_*.json"))
        
        if not message_files:
            print("❌ 没有找到任何消息文件")
            return
            
        print(f"📁 找到 {len(message_files)} 个消息文件")
        
        # 按日期分组
        dates_data = {}
        
        for file in message_files:
            # 从文件名提取信息: chat_CHATID_YYYYMMDD.json
            parts = file.stem.split('_')
            if len(parts) >= 3:
                chat_id = parts[1]
                date_str = parts[2]
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                date_key = date_obj.strftime('%Y-%m-%d')
                
                if date_key not in dates_data:
                    dates_data[date_key] = {}
                    
                # 读取消息数据
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        dates_data[date_key][chat_id] = {
                            'messages': messages,
                            'chat_title': messages[0]['chat_title'] if messages else 'Unknown'
                        }
                except Exception as e:
                    print(f"⚠️ 读取文件 {file.name} 失败: {e}")
        
        # 按日期排序（最新的在前）
        sorted_dates = sorted(dates_data.keys(), reverse=True)
        
        print(f"📅 找到 {len(sorted_dates)} 个日期的数据: {', '.join(sorted_dates)}")
        print()
        
        # 为每个日期生成总结
        for date in sorted_dates[:3]:  # 最近3天
            print(f"📊 处理日期: {date}")
            print("-" * 40)
            
            day_data = dates_data[date]
            total_messages = 0
            
            for chat_id, chat_data in day_data.items():
                messages = chat_data['messages']
                chat_title = chat_data['chat_title']
                message_count = len(messages)
                total_messages += message_count
                
                print(f"   📱 群组: {chat_title}")
                print(f"   💬 消息数: {message_count}")
                
                if message_count >= config.MIN_MESSAGES_FOR_SUMMARY:
                    print(f"   🤖 生成AI总结...")
                    
                    try:
                        # 生成总结
                        date_obj = datetime.strptime(date, '%Y-%m-%d')
                        summary = await summarizer.generate_daily_summary(int(chat_id), date_obj)
                        
                        if summary:
                            print(f"   ✅ 总结生成成功")
                            
                            # 显示总结
                            print("\n" + "="*50)
                            print(f"📄 {date} - {chat_title} 总结")
                            print("="*50)
                            print(summary)
                            print("="*50)
                            print()
                        else:
                            print(f"   ❌ 总结生成失败")
                            
                    except Exception as e:
                        print(f"   ❌ 生成总结时出错: {e}")
                        # 如果API调用失败，生成备用总结
                        print(f"   🔄 生成备用总结...")
                        backup_summary = create_backup_summary(messages, date, chat_title)
                        print("\n" + "="*50)
                        print(f"📄 {date} - {chat_title} 备用总结")
                        print("="*50)
                        print(backup_summary)
                        print("="*50)
                        print()
                else:
                    print(f"   ⏭️ 消息数不足，跳过总结")
                
                print()
            
            print(f"📊 {date} 总计: {total_messages} 条消息")
            print()
        
        print("✅ 所有可用数据的总结生成完成!")
        
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        import traceback
        traceback.print_exc()

def create_backup_summary(messages, date, chat_title):
    """创建备用总结（当AI API不可用时）"""
    if not messages:
        return f"📭 {date} 该群组无消息记录"
    
    # 统计信息
    total_messages = len(messages)
    users = {}
    time_range = []
    
    for msg in messages:
        username = msg.get('first_name', 'Unknown User')
        if username not in users:
            users[username] = 0
        users[username] += 1
        
        if msg.get('timestamp'):
            time_range.append(msg['timestamp'])
    
    # 时间范围
    time_start = min(time_range) if time_range else 'Unknown'
    time_end = max(time_range) if time_range else 'Unknown'
    
    # 生成总结
    summary = f"""
📊 **群组对话总结 - {date}**
📱 群组: {chat_title}

• **基本统计**:
  - 总消息数: {total_messages} 条
  - 活跃用户: {len(users)} 位
  - 时间跨度: {time_start} 至 {time_end}

• **用户活跃度**:
"""
    
    # 按消息数排序用户
    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    for username, count in sorted_users:
        summary += f"  - {username}: {count} 条消息\n"
    
    # 提取一些示例消息
    if len(messages) > 0:
        summary += "\n• **消息示例**:\n"
        sample_messages = messages[:3] if len(messages) >= 3 else messages
        for msg in sample_messages:
            text = msg.get('message_text', '')[:50]
            username = msg.get('first_name', 'Unknown')
            if text:
                summary += f"  - {username}: {text}{'...' if len(msg.get('message_text', '')) > 50 else ''}\n"
    
    summary += f"\n📝 *备用总结 - 如需详细AI分析请确保API配置正确*"
    
    return summary.strip()

if __name__ == "__main__":
    asyncio.run(generate_available_summaries())