"""
AI 总结功能模块
支持多种 AI 服务提供商进行聊天记录的智能总结
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config


class AIProvider:
    """AI 服务提供商基类"""
    
    async def generate_summary(self, messages: List[Dict], chat_title: str) -> str:
        """生成总结"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API 提供商"""
    
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.base_url = Config.OPENAI_BASE_URL
    
    def _build_prompt(self, messages: List[Dict], chat_title: str) -> str:
        """构建提示词"""
        language_prompts = {
            'zh': '请用中文总结',
            'en': 'Please summarize in English',
            'ja': '日本語で要約してください',
        }
        
        length_prompts = {
            'short': '简短总结（100-200字）',
            'medium': '中等长度总结（200-500字）',
            'long': '详细总结（500-1000字）'
        }
        
        style_prompts = {
            'bullet': '请使用要点列表格式',
            'paragraph': '请使用段落格式',
            'structured': '请使用结构化格式（包含主要话题、重要决定、行动项等）'
        }
        
        lang_prompt = language_prompts.get(Config.SUMMARY_LANGUAGE, language_prompts['zh'])
        length_prompt = length_prompts.get(Config.SUMMARY_LENGTH, length_prompts['medium'])
        style_prompt = style_prompts.get(Config.SUMMARY_STYLE, style_prompts['bullet'])
        
        # 格式化消息
        formatted_messages = []
        for msg in messages:
            timestamp = msg.get('timestamp', '')
            user = f"{msg.get('first_name', '')} {msg.get('last_name', '')}".strip()
            if msg.get('username'):
                user += f" (@{msg['username']})"
            text = msg.get('message_text', '')
            
            formatted_messages.append(f"[{timestamp}] {user}: {text}")
        
        messages_text = '\n'.join(formatted_messages)
        
        return f"""
你是一个专业的会议和聊天记录总结助手。请分析以下来自Telegram群组"{chat_title}"的聊天记录，并生成总结。

总结要求：
- {lang_prompt}
- {length_prompt}
- {style_prompt}
- 保持客观和准确
- 突出重要信息和关键决定
- 如果有行动项或待办事项，请单独列出

聊天记录：
{messages_text}

请生成总结：
"""
    
    async def generate_summary(self, messages: List[Dict], chat_title: str) -> str:
        """使用 OpenAI API 生成总结"""
        if not self.api_key:
            raise ValueError("OpenAI API Key 未设置")
        
        prompt = self._build_prompt(messages, chat_title)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        # 构建API请求数据 - 使用最兼容的参数
        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        # 根据模型类型添加token限制参数
        if 'gpt-5' in self.model.lower():
            # GPT-5只使用确认可用的参数
            data['max_completion_tokens'] = 2000
        else:
            # 传统GPT模型参数
            data.update({
                'max_tokens': 2000,
                'temperature': 0.3
            })
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API 错误: {response.status} - {error_text}")
                
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()


class ClaudeProvider(AIProvider):
    """Anthropic Claude API 提供商"""
    
    def __init__(self):
        self.api_key = Config.ANTHROPIC_API_KEY
        self.model = Config.ANTHROPIC_MODEL
    
    async def generate_summary(self, messages: List[Dict], chat_title: str) -> str:
        """使用 Claude API 生成总结"""
        if not self.api_key:
            raise ValueError("Anthropic API Key 未设置")
        
        # 这里可以实现 Claude API 调用
        # 目前作为占位符
        raise NotImplementedError("Claude API 支持开发中")


class LocalProvider(AIProvider):
    """本地 AI 模型提供商（如 Ollama）"""
    
    def __init__(self):
        self.base_url = os.getenv('LOCAL_AI_URL', 'http://localhost:11434')
        self.model = os.getenv('LOCAL_AI_MODEL', 'llama2')
    
    async def generate_summary(self, messages: List[Dict], chat_title: str) -> str:
        """使用本地 AI 模型生成总结"""
        # 这里可以实现本地 AI 调用
        # 目前作为占位符
        raise NotImplementedError("本地 AI 模型支持开发中")


class AISummarizer:
    """AI 总结器主类"""
    
    def __init__(self):
        self.config = Config()
        self.provider = self._get_provider()
        self.logger = self._setup_logger()
    
    def _get_provider(self) -> AIProvider:
        """获取 AI 服务提供商"""
        providers = {
            'openai': OpenAIProvider,
            'claude': ClaudeProvider,
            'local': LocalProvider,
        }
        
        provider_class = providers.get(self.config.AI_PROVIDER)
        if not provider_class:
            raise ValueError(f"不支持的 AI 提供商: {self.config.AI_PROVIDER}")
        
        return provider_class()
    
    def _setup_logger(self):
        """设置日志"""
        import logging
        logger = logging.getLogger('ai_summarizer')
        return logger
    
    def get_messages_for_date(self, chat_id: int, target_date: datetime) -> List[Dict]:
        """获取指定日期的消息"""
        messages = []
        
        if self.config.STORAGE_FORMAT == 'sqlite':
            messages = self._get_messages_from_sqlite(chat_id, target_date)
        elif self.config.STORAGE_FORMAT == 'json':
            messages = self._get_messages_from_json(chat_id, target_date)
        
        return messages
    
    def get_messages_for_24h(self, chat_id: int) -> List[Dict]:
        """获取过去24小时的消息"""
        messages = []
        
        if self.config.STORAGE_FORMAT == 'sqlite':
            messages = self._get_messages_24h_from_sqlite(chat_id)
        elif self.config.STORAGE_FORMAT == 'json':
            messages = self._get_messages_24h_from_json(chat_id)
        
        return messages
    
    def _get_messages_from_sqlite(self, chat_id: int, target_date: datetime) -> List[Dict]:
        """从 SQLite 获取消息"""
        import sqlite3
        
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        if not os.path.exists(db_path):
            return []
        
        start_date = target_date.strftime('%Y-%m-%d 00:00:00')
        end_date = target_date.strftime('%Y-%m-%d 23:59:59')
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM messages 
                WHERE chat_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (chat_id, start_date, end_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _get_messages_24h_from_sqlite(self, chat_id: int) -> List[Dict]:
        """从 SQLite 获取过去24小时的消息"""
        import sqlite3
        
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        if not os.path.exists(db_path):
            return []
        
        # 计算过去24小时的时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        start_date = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM messages 
                WHERE chat_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (chat_id, start_date, end_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _get_messages_from_json(self, chat_id: int, target_date: datetime) -> List[Dict]:
        """从 JSON 文件获取消息"""
        messages = []
        date_str = target_date.strftime(self.config.FILENAME_TIME_FORMAT)
        pattern = f"chat_{abs(chat_id)}_{date_str}"
        
        for filename in os.listdir(self.config.DATA_DIR):
            if filename.startswith(pattern) and filename.endswith('.json'):
                filepath = os.path.join(self.config.DATA_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_messages = json.load(f)
                        # 过滤指定日期的消息
                        for msg in file_messages:
                            msg_date = datetime.strptime(
                                msg['timestamp'].split(' ')[0], 
                                '%Y-%m-%d'
                            ).date()
                            if msg_date == target_date.date():
                                messages.append(msg)
                except (json.JSONDecodeError, FileNotFoundError, KeyError):
                    continue
        
        return sorted(messages, key=lambda x: x.get('timestamp', ''))
    
    def _get_messages_24h_from_json(self, chat_id: int) -> List[Dict]:
        """从 JSON 文件获取过去24小时的消息"""
        messages = []
        
        # 计算过去24小时的时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # 需要检查可能涉及的日期文件（昨天和今天）
        dates_to_check = [start_time.date(), end_time.date()]
        
        for check_date in set(dates_to_check):  # 去重
            date_str = check_date.strftime(self.config.FILENAME_TIME_FORMAT)
            pattern = f"chat_{abs(chat_id)}_{date_str}"
            
            for filename in os.listdir(self.config.DATA_DIR):
                if filename.startswith(pattern) and filename.endswith('.json'):
                    filepath = os.path.join(self.config.DATA_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            file_messages = json.load(f)
                            # 过滤过去24小时的消息
                            for msg in file_messages:
                                try:
                                    msg_time = datetime.strptime(msg['timestamp'], self.config.TIME_FORMAT)
                                    if start_time <= msg_time <= end_time:
                                        messages.append(msg)
                                except (ValueError, KeyError):
                                    continue
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
        
        return sorted(messages, key=lambda x: x.get('timestamp', ''))
    
    async def generate_daily_summary(self, chat_id: int, date: Optional[datetime] = None) -> Optional[str]:
        """生成每日总结"""
        if not self.config.ENABLE_AI_SUMMARY:
            self.logger.info("AI 总结功能未启用")
            return None
        
        if date is None:
            date = datetime.now() - timedelta(days=1)  # 默认总结昨天
        
        # 获取消息
        messages = self.get_messages_for_date(chat_id, date)
        
        if len(messages) < self.config.MIN_MESSAGES_FOR_SUMMARY:
            self.logger.info(f"消息数量不足 ({len(messages)} < {self.config.MIN_MESSAGES_FOR_SUMMARY})，跳过总结")
            return None
        
        # 获取群组标题
        chat_title = messages[0].get('chat_title', f'Chat {abs(chat_id)}') if messages else f'Chat {abs(chat_id)}'
        
        try:
            # 生成总结
            summary = await self.provider.generate_summary(messages, chat_title)
            
            # 保存总结
            self._save_summary(chat_id, date, summary, len(messages))
            
            self.logger.info(f"成功生成总结: {chat_title} - {date.strftime('%Y-%m-%d')}")
            return summary
        
        except Exception as e:
            self.logger.error(f"生成总结失败: {e}")
            return None
    
    async def generate_today_summary(self, chat_id: int) -> Optional[str]:
        """生成今日总结（过去24小时的消息，保存为今天的文件）"""
        if not self.config.ENABLE_AI_SUMMARY:
            self.logger.info("AI 总结功能未启用")
            return None
        
        # 获取过去24小时的消息
        messages = self.get_messages_for_24h(chat_id)
        
        if len(messages) < self.config.MIN_MESSAGES_FOR_SUMMARY:
            self.logger.info(f"消息数量不足 ({len(messages)} < {self.config.MIN_MESSAGES_FOR_SUMMARY})，跳过总结")
            return None
        
        # 获取群组标题
        chat_title = messages[0].get('chat_title', f'Chat {abs(chat_id)}') if messages else f'Chat {abs(chat_id)}'
        
        try:
            # 生成总结
            summary = await self.provider.generate_summary(messages, chat_title)
            
            # 保存总结（使用今天的日期作为文件名）
            today = datetime.now()
            self._save_summary(chat_id, today, summary, len(messages))
            
            self.logger.info(f"成功生成今日总结: {chat_title} - {today.strftime('%Y-%m-%d')}")
            return summary
        
        except Exception as e:
            self.logger.error(f"生成今日总结失败: {e}")
            return None
    
    def _save_summary(self, chat_id: int, date: datetime, summary: str, message_count: int):
        """保存总结"""
        summary_data = {
            'chat_id': chat_id,
            'date': date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().strftime(self.config.TIME_FORMAT),
            'message_count': message_count,
            'summary': summary,
            'config': {
                'ai_provider': self.config.AI_PROVIDER,
                'model': getattr(self.config, f'{self.config.AI_PROVIDER.upper()}_MODEL', ''),
                'language': self.config.SUMMARY_LANGUAGE,
                'length': self.config.SUMMARY_LENGTH,
                'style': self.config.SUMMARY_STYLE
            }
        }
        
        # 创建文件名
        date_str = date.strftime('%Y%m%d')
        filename = f"summary_chat_{abs(chat_id)}_{date_str}.json"
        filepath = os.path.join(self.config.SUMMARY_DIR, filename)
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    def get_summary_history(self, chat_id: int, days: int = 7) -> List[Dict]:
        """获取最近的总结历史"""
        summaries = []
        
        for filename in os.listdir(self.config.SUMMARY_DIR):
            if filename.startswith(f"summary_chat_{abs(chat_id)}_") and filename.endswith('.json'):
                filepath = os.path.join(self.config.SUMMARY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                        summaries.append(summary_data)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        # 按日期排序，返回最近的记录
        summaries.sort(key=lambda x: x.get('date', ''), reverse=True)
        return summaries[:days]
    
    def format_summary_for_telegram(self, summary: str, chat_title: str, date: datetime, message_count: int) -> str:
        """格式化总结用于 Telegram 发送"""
        date_str = date.strftime('%Y年%m月%d日')
        
        formatted = f"""
📊 **{chat_title} - {date_str} 聊天总结**

💬 消息数量: {message_count} 条
🤖 AI 模型: {self.config.AI_PROVIDER.upper()}
⏰ 生成时间: {datetime.now().strftime('%H:%M')}

---

{summary}

---
_由 AI 自动生成 · Telegram Note Taker_
"""
        return formatted.strip()


# 工厂函数
def create_ai_summarizer() -> Optional[AISummarizer]:
    """创建 AI 总结器实例"""
    try:
        if not Config.ENABLE_AI_SUMMARY:
            return None
        return AISummarizer()
    except Exception as e:
        print(f"创建 AI 总结器失败: {e}")
        return None