"""
GitHub Copilot集成的AI总结服务
支持多种AI提供商，包括Azure OpenAI (Copilot背后的服务)
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import aiohttp

class CopilotAISummarizer:
    """使用GitHub Copilot风格的AI总结器"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_copilot_style_prompt(self, messages: List[Dict], chat_title: str) -> str:
        """创建Copilot风格的提示词"""
        # 格式化消息内容
        formatted_messages = []
        for msg in messages:
            timestamp = msg.get('timestamp', '')
            username = msg.get('first_name', 'Unknown')
            text = msg.get('message_text', '')
            formatted_messages.append(f"[{timestamp}] {username}: {text}")
        
        conversation_text = "\n".join(formatted_messages)
        
        prompt = f"""# Telegram群组对话分析

## 任务
请分析以下Telegram群组"{chat_title}"的对话记录，生成一份智能总结报告。

## 对话数据
```
{conversation_text}
```

## 输出要求
请生成一个结构化的中文总结，包含：

### 📊 基本统计
- 消息总数
- 参与人数
- 时间跨度

### 💬 主要话题
- 识别讨论的核心话题
- 话题的发展脉络

### 👥 用户活跃度
- 各用户的参与情况
- 主要发言者

### 🔍 关键信息
- 重要决策或结论
- 值得注意的信息点

### 📝 对话趋势
- 对话的整体氛围
- 讨论的方向和结果

请用友好、专业的语调生成总结，重点突出有价值的信息。
"""
        return prompt
    
    async def generate_with_azure_openai(self, messages: List[Dict], chat_title: str) -> Optional[str]:
        """使用Azure OpenAI生成总结"""
        try:
            # 这里需要你的Azure OpenAI配置
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
            api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
            deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
            
            if not all([endpoint, api_key, deployment]):
                print("⚠️ Azure OpenAI配置不完整，跳过")
                return None
            
            url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
            
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }
            
            prompt = self.create_copilot_style_prompt(messages, chat_title)
            
            data = {
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的对话分析助手，擅长分析群聊记录并生成有洞察力的总结。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 1500,
                'temperature': 0.7
            }
            
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    error_text = await response.text()
                    print(f"❌ Azure OpenAI API错误 {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Azure OpenAI调用失败: {e}")
            return None
    
    def generate_local_copilot_summary(self, messages: List[Dict], chat_title: str) -> str:
        """生成本地Copilot风格的总结"""
        if not messages:
            return f"📭 群组 '{chat_title}' 暂无消息记录"
        
        # 统计数据
        total_messages = len(messages)
        users = {}
        topics = set()
        
        for msg in messages:
            username = msg.get('first_name', 'Unknown')
            text = msg.get('message_text', '').lower()
            
            users[username] = users.get(username, 0) + 1
            
            # 简单话题识别
            if any(word in text for word in ['test', '测试', 'bot']):
                topics.add('🤖 Bot功能测试')
            if any(word in text for word in ['weather', 'rain', '天气', '下雨']):
                topics.add('🌤️ 天气讨论')
            if any(word in text for word in ['music', 'rock', '音乐', '摇滚']):
                topics.add('🎵 音乐分享')
            if any(word in text for word in ['hi', 'hello', '你好', 'hey']):
                topics.add('👋 日常问候')
        
        # 时间分析
        timestamps = [msg.get('timestamp', '') for msg in messages if msg.get('timestamp')]
        time_start = min(timestamps) if timestamps else 'Unknown'
        time_end = max(timestamps) if timestamps else 'Unknown'
        
        # 生成Copilot风格的总结
        summary = f"""# 📊 Telegram群组智能分析报告

## 群组信息
**群组名称**: {chat_title}
**分析时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 📈 数据概览
- **总消息数**: {total_messages} 条
- **活跃用户**: {len(users)} 位
- **时间跨度**: {time_start} 至 {time_end}

## 👥 用户参与度"""

        # 用户活跃度排序
        sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
        for username, count in sorted_users:
            percentage = (count / total_messages) * 100
            summary += f"\n- **{username}**: {count} 条消息 ({percentage:.1f}%)"
        
        # 话题分析
        if topics:
            summary += f"\n\n## 💬 主要话题\n"
            for topic in sorted(topics):
                summary += f"- {topic}\n"
        
        # 消息示例
        summary += f"\n## 📝 对话片段\n"
        sample_size = min(3, len(messages))
        for i, msg in enumerate(messages[:sample_size]):
            username = msg.get('first_name', 'Unknown')
            text = msg.get('message_text', '')[:100]
            timestamp = msg.get('timestamp', '')
            summary += f"**{username}** `{timestamp}`: {text}{'...' if len(msg.get('message_text', '')) > 100 else ''}\n\n"
        
        # 智能洞察
        summary += f"## 🔍 AI洞察\n"
        if total_messages < 10:
            summary += "- 对话量较少，主要为功能测试或初期交流\n"
        if len(users) == 1:
            summary += "- 单人主导对话，可能为测试场景或独白模式\n"
        if 'test' in ' '.join([msg.get('message_text', '').lower() for msg in messages]):
            summary += "- 检测到测试相关内容，群组可能处于功能验证阶段\n"
        
        summary += f"\n---\n*🤖 由本地AI分析生成 | GitHub Copilot风格总结*"
        
        return summary
    
    async def generate_summary(self, messages: List[Dict], chat_title: str) -> str:
        """生成总结（优先使用Azure OpenAI，回退到本地）"""
        # 首先尝试Azure OpenAI
        azure_summary = await self.generate_with_azure_openai(messages, chat_title)
        if azure_summary:
            return f"🤖 **Azure OpenAI 智能总结**\n\n{azure_summary}"
        
        # 回退到本地Copilot风格总结
        local_summary = self.generate_local_copilot_summary(messages, chat_title)
        return local_summary

# 使用示例函数
async def test_copilot_summarizer():
    """测试Copilot风格的总结器"""
    print("🤖 测试GitHub Copilot风格AI总结器")
    print("="*50)
    
    # 加载今天的消息数据
    data_dir = '/Users/wuzhongzhu/Documents/GitHub/demo-9357-old/TG-notetaker/data'
    message_files = [f for f in os.listdir(data_dir) if f.endswith('20251103.json')]
    
    async with CopilotAISummarizer() as summarizer:
        for file in message_files:
            if 'chat_' not in file:
                continue
                
            filepath = os.path.join(data_dir, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                if messages:
                    chat_title = messages[0].get('chat_title', 'Unknown Group')
                    print(f"\n📊 分析群组: {chat_title}")
                    print(f"📨 消息数量: {len(messages)}")
                    
                    summary = await summarizer.generate_summary(messages, chat_title)
                    
                    print("\n" + "="*60)
                    print(summary)
                    print("="*60)
                    
            except Exception as e:
                print(f"❌ 处理文件 {file} 时出错: {e}")

if __name__ == "__main__":
    asyncio.run(test_copilot_summarizer())