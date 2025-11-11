"""
定时任务模块
负责管理自动总结和其他定时任务
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Optional, List, Set
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config
from ai_summary import create_ai_summarizer

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, telegram_app=None):
        self.config = Config()
        self.logger = logging.getLogger('task_scheduler')
        self.telegram_app = telegram_app
        self.ai_summarizer = create_ai_summarizer()
        self.running = False
        self._tasks: Set[asyncio.Task] = set()
        
        # 解析自动总结时间
        self.auto_summary_time = self._parse_time(self.config.AUTO_SUMMARY_TIME)
    
    def _parse_time(self, time_str: str) -> Optional[time]:
        """解析时间字符串"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except (ValueError, AttributeError):
            self.logger.error(f"无效的时间格式: {time_str}，使用默认时间 23:30")
            return time(23, 30)
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.logger.info("任务调度器已启动")
        
        # 启动定时任务 - 但不在初始化时创建任务
        # 任务将在 start_async 中创建
    
    async def start_async(self):
        """异步启动调度器任务"""
        if not self.running:
            return
        
        # 启动定时任务
        if self.config.ENABLE_AI_SUMMARY and self.ai_summarizer:
            task = asyncio.create_task(self._daily_summary_scheduler())
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            self.logger.info("AI 总结定时任务已启动")
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("正在停止任务调度器...")
        
        # 取消所有任务
        for task in self._tasks.copy():
            if not task.done():
                task.cancel()
        
        # 清空任务集合
        self._tasks.clear()
        self.logger.info("任务调度器已停止")
    
    async def _daily_summary_scheduler(self):
        """每日总结调度器"""
        self.logger.info(f"每日总结调度器已启动，将在 {self.auto_summary_time} 执行")
        
        while self.running:
            try:
                # 计算下次执行时间
                now = datetime.now()
                next_run = datetime.combine(now.date(), self.auto_summary_time)
                
                # 如果今天的执行时间已过，安排明天执行
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                # 计算等待时间
                wait_seconds = (next_run - now).total_seconds()
                self.logger.info(f"下次自动总结时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待到执行时间
                await asyncio.sleep(wait_seconds)
                
                if not self.running:
                    break
                
                # 执行自动总结
                await self._execute_daily_summary()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"每日总结调度器错误: {e}")
                # 发生错误时等待1小时后重试
                await asyncio.sleep(3600)
    
    async def _execute_daily_summary(self):
        """执行每日总结"""
        self.logger.info("开始执行每日自动总结...")
        
        if not self.ai_summarizer:
            self.logger.warning("AI 总结器未初始化")
            return
        
        # 获取昨天的日期（在00:00执行时，总结前一天的对话）
        yesterday = datetime.now() - timedelta(days=1)
        
        # 获取需要总结的群组列表
        chat_ids = await self._get_active_chats(yesterday)
        
        summary_count = 0
        
        for chat_id in chat_ids:
            try:
                summary = await self.ai_summarizer.generate_daily_summary(chat_id, yesterday)
                
                if summary:
                    summary_count += 1
                    self.logger.info(f"群组 {chat_id} 总结完成")
                    
                    # 如果配置了发送到群组，则发送总结
                    if self.config.SEND_SUMMARY_TO_CHAT and self.telegram_app:
                        await self._send_summary_to_chat(chat_id, summary, yesterday)
                
                # 避免 API 限制，稍微延迟
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"群组 {chat_id} 总结失败: {e}")
                continue
        
        self.logger.info(f"每日自动总结完成，共处理 {summary_count} 个群组")
    
    async def _get_active_chats(self, target_date: datetime) -> List[int]:
        """获取指定日期有活动的群组列表"""
        chat_ids = []
        
        if self.config.STORAGE_FORMAT == 'sqlite':
            chat_ids = self._get_active_chats_from_sqlite(target_date)
        elif self.config.STORAGE_FORMAT == 'json':
            chat_ids = self._get_active_chats_from_json(target_date)
        
        # 如果配置了允许的群组列表，则过滤
        if self.config.ALLOWED_GROUPS:
            chat_ids = [cid for cid in chat_ids if cid in self.config.ALLOWED_GROUPS]
        
        return chat_ids
    
    def _get_active_chats_from_sqlite(self, target_date: datetime) -> List[int]:
        """从 SQLite 获取活跃群组"""
        import sqlite3
        
        db_path = os.path.join(self.config.DATA_DIR, 'messages.db')
        if not os.path.exists(db_path):
            return []
        
        start_date = target_date.strftime('%Y-%m-%d 00:00:00')
        end_date = target_date.strftime('%Y-%m-%d 23:59:59')
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT chat_id, COUNT(*) as message_count
                FROM messages 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY chat_id
                HAVING message_count >= ?
            ''', (start_date, end_date, self.config.MIN_MESSAGES_FOR_SUMMARY))
            
            return [row[0] for row in cursor.fetchall()]
    
    def _get_active_chats_from_json(self, target_date: datetime) -> List[int]:
        """从 JSON 文件获取活跃群组"""
        chat_ids = set()
        date_str = target_date.strftime(self.config.FILENAME_TIME_FORMAT)
        
        for filename in os.listdir(self.config.DATA_DIR):
            if filename.endswith('.json') and date_str in filename:
                # 从文件名提取 chat_id
                try:
                    parts = filename.replace('.json', '').split('_')
                    if len(parts) >= 3 and parts[0] == 'chat':
                        chat_id = -int(parts[1])  # 群组 ID 是负数
                        chat_ids.add(chat_id)
                except (ValueError, IndexError):
                    continue
        
        return list(chat_ids)
    
    async def _send_summary_to_chat(self, chat_id: int, summary: str, date: datetime):
        """发送总结到群组"""
        if not self.telegram_app:
            return
        
        try:
            # 获取群组标题（从最近的消息中）
            messages = self.ai_summarizer.get_messages_for_date(chat_id, date)
            chat_title = messages[0].get('chat_title', f'Chat {abs(chat_id)}') if messages else f'Chat {abs(chat_id)}'
            
            # 格式化总结
            formatted_summary = self.ai_summarizer.format_summary_for_telegram(
                summary, chat_title, date, len(messages)
            )
            
            # 确定发送目标：优先使用配置的报告群组，否则发送到原群组
            target_chat_id = self.config.get_summary_report_chat_id()
            if target_chat_id == 0:
                target_chat_id = chat_id
            
            # 发送到目标群组
            await self.telegram_app.bot.send_message(
                chat_id=target_chat_id,
                text=formatted_summary,
                parse_mode='Markdown'
            )
            
            if target_chat_id != chat_id:
                self.logger.info(f"总结已从群组 {chat_id} 发送到报告群组 {target_chat_id}")
            else:
                self.logger.info(f"总结已发送到群组 {chat_id}")
            
        except Exception as e:
            self.logger.error(f"发送总结失败 (源群组: {chat_id}): {e}")
    
    async def manual_summary(self, chat_id: int, date: Optional[datetime] = None) -> Optional[str]:
        """手动触发总结"""
        if not self.ai_summarizer:
            return None
        
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        try:
            return await self.ai_summarizer.generate_daily_summary(chat_id, date)
        except Exception as e:
            self.logger.error(f"手动总结失败: {e}")
            return None
    
    async def generate_today_summary(self, chat_id: int) -> Optional[str]:
        """生成今日(过去24小时)总结并保存到当天的文件"""
        if not self.ai_summarizer:
            return None
        
        try:
            # 使用新的今日总结方法（过去24小时消息，保存为今天文件）
            summary = await self.ai_summarizer.generate_today_summary(chat_id)
            
            if summary:
                today = datetime.now()
                self.logger.info(f"今日总结生成成功 - 群组: {chat_id}, 日期: {today.strftime('%Y-%m-%d')}")
            
            return summary
        except Exception as e:
            self.logger.error(f"生成今日总结失败: {e}")
            return None
    
    def get_summary_stats(self) -> dict:
        """获取总结统计信息"""
        stats = {
            'enabled': self.config.ENABLE_AI_SUMMARY,
            'provider': self.config.AI_PROVIDER,
            'auto_summary_time': str(self.auto_summary_time),
            'send_to_chat': self.config.SEND_SUMMARY_TO_CHAT,
            'min_messages': self.config.MIN_MESSAGES_FOR_SUMMARY,
            'running': self.running
        }
        
        # 统计已生成的总结数量
        try:
            summary_files = [f for f in os.listdir(self.config.SUMMARY_DIR) if f.endswith('.json')]
            stats['total_summaries'] = len(summary_files)
        except (FileNotFoundError, OSError):
            stats['total_summaries'] = 0
        
        return stats