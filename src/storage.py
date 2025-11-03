"""
数据存储模块
支持 JSON、文本和 SQLite 格式的消息存储
"""
import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

class MessageStorage:
    """消息存储类"""
    
    def __init__(self):
        self.config = Config()
        self.ensure_directories()
        
        if self.config.STORAGE_FORMAT == 'sqlite':
            self.init_database()
    
    def ensure_directories(self):
        """确保存储目录存在"""
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        if self.config.DOWNLOAD_MEDIA:
            os.makedirs(self.config.MEDIA_DIR, exist_ok=True)
    
    def init_database(self):
        """初始化 SQLite 数据库"""
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    chat_id INTEGER,
                    chat_title TEXT,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    message_text TEXT,
                    message_type TEXT,
                    timestamp DATETIME,
                    media_info TEXT,
                    raw_data TEXT
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
    
    def save_message(self, message_data: Dict[str, Any]):
        """保存消息"""
        if self.config.STORAGE_FORMAT == 'json':
            self._save_to_json(message_data)
        elif self.config.STORAGE_FORMAT == 'txt':
            self._save_to_txt(message_data)
        elif self.config.STORAGE_FORMAT == 'sqlite':
            self._save_to_sqlite(message_data)
    
    def _save_to_json(self, message_data: Dict[str, Any]):
        """保存到 JSON 文件"""
        chat_id = message_data['chat_id']
        date_str = datetime.now().strftime(self.config.FILENAME_TIME_FORMAT)
        filename = f"chat_{abs(chat_id)}_{date_str}.json"
        filepath = os.path.join(self.config.DATA_DIR, filename)
        
        # 读取现有数据
        messages = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                messages = []
        
        # 添加新消息
        messages.append(message_data)
        
        # 检查是否需要分割文件
        if len(messages) > self.config.MAX_MESSAGES_PER_FILE:
            # 创建新的文件
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"chat_{abs(chat_id)}_{date_str}_{timestamp}.json"
            filepath = os.path.join(self.config.DATA_DIR, filename)
            messages = [message_data]
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def _save_to_txt(self, message_data: Dict[str, Any]):
        """保存到文本文件"""
        chat_id = message_data['chat_id']
        date_str = datetime.now().strftime(self.config.FILENAME_TIME_FORMAT)
        filename = f"chat_{abs(chat_id)}_{date_str}.txt"
        filepath = os.path.join(self.config.DATA_DIR, filename)
        
        # 格式化消息文本
        timestamp = message_data['timestamp']
        user_info = f"{message_data['first_name']} {message_data.get('last_name', '')}".strip()
        if message_data.get('username'):
            user_info += f" (@{message_data['username']})"
        
        message_line = f"[{timestamp}] {user_info}: {message_data['message_text']}\n"
        
        # 追加到文件
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(message_line)
    
    def _save_to_sqlite(self, message_data: Dict[str, Any]):
        """保存到 SQLite 数据库"""
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                INSERT INTO messages (
                    message_id, chat_id, chat_title, user_id, username,
                    first_name, last_name, message_text, message_type,
                    timestamp, media_info, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_data['message_id'],
                message_data['chat_id'],
                message_data['chat_title'],
                message_data['user_id'],
                message_data.get('username'),
                message_data['first_name'],
                message_data.get('last_name'),
                message_data['message_text'],
                message_data['message_type'],
                message_data['timestamp'],
                json.dumps(message_data.get('media_info')),
                json.dumps(message_data)
            ))
    
    def get_chat_stats(self, chat_id: int) -> Dict[str, Any]:
        """获取群组统计信息"""
        if self.config.STORAGE_FORMAT == 'sqlite':
            return self._get_sqlite_stats(chat_id)
        else:
            return self._get_file_stats(chat_id)
    
    def _get_sqlite_stats(self, chat_id: int) -> Dict[str, Any]:
        """从 SQLite 获取统计信息"""
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 总消息数
            cursor.execute('SELECT COUNT(*) FROM messages WHERE chat_id = ?', (chat_id,))
            total_messages = cursor.fetchone()[0]
            
            # 用户统计
            cursor.execute('''
                SELECT username, first_name, COUNT(*) as count
                FROM messages 
                WHERE chat_id = ? 
                GROUP BY user_id 
                ORDER BY count DESC 
                LIMIT 10
            ''', (chat_id,))
            user_stats = cursor.fetchall()
            
            # 日期范围
            cursor.execute('''
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM messages 
                WHERE chat_id = ?
            ''', (chat_id,))
            date_range = cursor.fetchone()
            
            return {
                'total_messages': total_messages,
                'top_users': user_stats,
                'date_range': date_range
            }
    
    def _get_file_stats(self, chat_id: int) -> Dict[str, Any]:
        """从文件获取统计信息"""
        # 简单的文件统计实现
        pattern = f"chat_{abs(chat_id)}_"
        message_files = [f for f in os.listdir(self.config.DATA_DIR) if f.startswith(pattern)]
        
        return {
            'total_files': len(message_files),
            'files': message_files
        }