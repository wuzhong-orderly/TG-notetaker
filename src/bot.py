"""
Telegram Note Taker Bot 主程序
"""
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.error import TelegramError

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from storage import MessageStorage
from scheduler import TaskScheduler
from ai_summary import create_ai_summarizer

class TelegramNoteTaker:
    """Telegram 笔记记录器主类"""
    
    def __init__(self):
        self.config = Config()
        self.storage = MessageStorage()
        self.logger = self._setup_logging()
        self.scheduler = None
        self.ai_summarizer = None
        
        # 验证配置
        if not self.config.validate():
            sys.exit(1)
        
        # 初始化 AI 总结功能
        if self.config.ENABLE_AI_SUMMARY:
            self.ai_summarizer = create_ai_summarizer()
            if self.ai_summarizer:
                self.logger.info(f"AI 总结功能已启用 (提供商: {self.config.AI_PROVIDER})")
            else:
                self.logger.warning("AI 总结功能启用失败")
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('telegram_notetaker')
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # 创建文件处理器
        log_file = os.path.join(self.config.LOG_DIR, 'telegram_notetaker.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _is_allowed_chat(self, chat_id: int) -> bool:
        """检查是否允许记录此群组"""
        allowed_groups = self.config.get_allowed_groups()
        # 默认允许所有群组，只有明确配置了限制才检查
        if not allowed_groups:
            print(f"✅ 允许所有群组，当前群组 ID: {chat_id}", flush=True)
            return True
        
        # 如果配置了限制，则检查
        is_allowed = chat_id in allowed_groups
        print(f"🔍 群组权限检查: {chat_id} - {'允许' if is_allowed else '拒绝'}", flush=True)
        return is_allowed
    
    def _is_admin(self, user_id: int) -> bool:
        """检查是否为管理员"""
        return user_id in self.config.get_admin_ids()
    
    def _extract_message_data(self, message: Message) -> Optional[Dict[str, Any]]:
        """提取消息数据"""
        if not message.from_user:
            return None
        
        # 检查是否应该忽略此消息
        if self.config.IGNORE_BOTS and message.from_user.is_bot:
            return None
        
        if self.config.IGNORE_COMMANDS and message.text and message.text.startswith('/'):
            return None
        
        # 确定消息类型和文本内容
        message_type = 'text'
        message_text = message.text or ''
        media_info = None
        
        if message.photo:
            message_type = 'photo'
            message_text = message.caption or '[图片]'
            media_info = {
                'type': 'photo',
                'file_id': message.photo[-1].file_id,
                'file_size': message.photo[-1].file_size
            }
        elif message.video:
            message_type = 'video'
            message_text = message.caption or '[视频]'
            media_info = {
                'type': 'video',
                'file_id': message.video.file_id,
                'file_size': message.video.file_size,
                'duration': message.video.duration
            }
        elif message.audio:
            message_type = 'audio'
            message_text = message.caption or '[音频]'
            media_info = {
                'type': 'audio',
                'file_id': message.audio.file_id,
                'file_size': message.audio.file_size,
                'duration': message.audio.duration
            }
        elif message.voice:
            message_type = 'voice'
            message_text = '[语音消息]'
            media_info = {
                'type': 'voice',
                'file_id': message.voice.file_id,
                'file_size': message.voice.file_size,
                'duration': message.voice.duration
            }
        elif message.document:
            message_type = 'document'
            message_text = message.caption or f'[文档: {message.document.file_name}]'
            media_info = {
                'type': 'document',
                'file_id': message.document.file_id,
                'file_name': message.document.file_name,
                'file_size': message.document.file_size
            }
        elif message.sticker:
            message_type = 'sticker'
            message_text = f'[贴纸: {message.sticker.emoji or ""}]'
            media_info = {
                'type': 'sticker',
                'file_id': message.sticker.file_id,
                'emoji': message.sticker.emoji
            }
        elif message.location:
            message_type = 'location'
            message_text = f'[位置: {message.location.latitude}, {message.location.longitude}]'
        elif message.contact:
            message_type = 'contact'
            message_text = f'[联系人: {message.contact.first_name}]'
        
        return {
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'chat_title': message.chat.title or 'Private Chat',
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'message_text': message_text,
            'message_type': message_type,
            'timestamp': message.date.strftime(self.config.TIME_FORMAT),
            'media_info': media_info
        }
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理接收到的消息"""
        message = update.message
        if not message:
            return
        
        # 打印收到的消息基本信息
        chat_info = f"群组: {message.chat.title}" if message.chat.title else f"Chat ID: {message.chat.id}"
        user_info = f"{message.from_user.first_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"
        
        print(f"📨 收到消息 - {chat_info} | {user_info}", flush=True)
        if message.text:
            print(f"💬 内容: {message.text}", flush=True)
        else:
            print(f"🎵 消息类型: {self._get_message_type_description(message)}", flush=True)
        print("-" * 50, flush=True)
        
        # 同时记录到日志
        self.logger.info(f"收到消息 - {chat_info} | {user_info} | 类型: {message.chat.type}")
        
        # 如果是私聊消息，显示但不记录
        if message.chat.type not in ['group', 'supergroup']:
            print(f"💭 私聊消息（不记录到文件）", flush=True)
            # 对于调试，我们仍然继续处理，但不保存
            print(f"🔍 调试：这是一条私聊消息", flush=True)
            return
        
        # 检查是否允许记录此群组
        if not self._is_allowed_chat(message.chat.id):
            print(f"🚫 群组不在允许列表中: {message.chat.id}", flush=True)
            return
        
        try:
            # 提取消息数据
            message_data = self._extract_message_data(message)
            if message_data:
                # 保存消息
                self.storage.save_message(message_data)
                
                print(f"✅ 消息已保存: {message_data['chat_title']} - {message_data['first_name']}", flush=True)
                
                self.logger.info(
                    f"记录消息: {message_data['chat_title']} - "
                    f"{message_data['first_name']}: {message_data['message_text'][:50]}"
                )
            else:
                print(f"⚠️ 消息被过滤，未保存", flush=True)
        
        except Exception as e:
            print(f"❌ 处理消息时发生错误: {e}", flush=True)
            self.logger.error(f"处理消息时发生错误: {e}")
    
    def _get_message_type_description(self, message: Message) -> str:
        """获取消息类型描述"""
        if message.photo:
            return "图片"
        elif message.video:
            return "视频"
        elif message.audio:
            return "音频"
        elif message.voice:
            return "语音消息"
        elif message.document:
            return f"文档 ({message.document.file_name})"
        elif message.sticker:
            return "贴纸"
        elif message.location:
            return "位置信息"
        elif message.contact:
            return "联系人"
        else:
            return "其他类型"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令 - 显示欢迎信息和交互式菜单"""
        message = update.message
        if not message:
            return
        
        # 检查用户权限
        is_admin = self._is_admin(message.from_user.id)
        
        # 基础欢迎信息
        welcome_text = """
🤖 **Telegram Note Taker Bot**

欢迎使用智能群组消息记录和总结机器人！
"""
        
        # 如果是管理员且启用了AI总结，显示交互式菜单
        if is_admin and self.config.ENABLE_AI_SUMMARY:
            welcome_text += """
**📱 功能菜单**

点击下方按钮生成今日总结：
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("� 生成今日总结", callback_data="generate_today")
                ]
                # 其他功能按钮保留在代码中，以后可以启用
                # [
                #     InlineKeyboardButton("� 获取24小时总结", callback_data="summary_24h"),
                #     InlineKeyboardButton("� 获取3天总结", callback_data="summary_3d")
                # ],
                # [
                #     InlineKeyboardButton("📋 查看已保存的总结", callback_data="get_saved")
                # ],
                # [
                #     InlineKeyboardButton("📅 生成指定日期总结", callback_data="show_summary_options"),
                #     InlineKeyboardButton("📚 查看历史总结", callback_data="show_history_options")
                # ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self._safe_send_text(message, welcome_text, reply_markup=reply_markup)
        else:
            # 非管理员或未启用AI功能，只显示欢迎信息
            if not is_admin:
                welcome_text += """
**ℹ️ 提示**
您需要管理员权限才能使用AI总结功能。
请使用 /myid 获取您的用户 ID，然后联系管理员添加权限。
"""
            else:
                welcome_text += """
**ℹ️ 提示**
AI总结功能未启用。请检查配置文件。
"""
            await message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令 - 显示详细的帮助信息"""
        message = update.message
        if not message:
            return
        
        # 检查用户权限
        is_admin = self._is_admin(message.from_user.id)
        
        help_text = """
🤖 **Telegram Note Taker Bot - 帮助文档**

**📝 功能介绍**
这是一个智能群组消息记录机器人，可以：
• 自动记录群组中的所有消息
• 生成AI智能总结（需管理员权限）
• 提供多种时间范围的总结选项
• 支持查看历史总结记录

**🎯 基本使用**
1️⃣ 将机器人添加到您的群组
2️⃣ 机器人会自动开始记录消息
3️⃣ 管理员可以使用 /start 命令访问功能菜单
4️⃣ 通过菜单按钮生成和查看总结

**📋 可用命令**

🔹 **所有用户**
/start - 打开功能菜单（管理员可看到完整菜单）
/help - 显示此帮助信息
/myid - 获取您的 Telegram 用户 ID

🔹 **管理员专用**
/stats - 查看当前群组的统计信息
/status - 查看机器人运行状态

**🔒 隐私说明**
• 只记录配置的群组消息
• 私聊消息不会被记录
"""
        
        if not is_admin:
            help_text += """
**ℹ️ 提示**
您当前不是管理员，只能使用基本功能。
如需使用AI总结功能，请联系机器人管理员。
"""
        
        await message.reply_text(help_text)
    
    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /myid 命令 - 获取用户ID"""
        message = update.message
        if not message:
            return
        
        user = message.from_user
        if not user:
            return
        
        # 构建用户信息
        user_info = f"""
🆔 **你的 Telegram 信息**

👤 用户 ID: `{user.id}`
📛 名字: {user.first_name}
"""
        
        if user.last_name:
            user_info += f"📛 姓氏: {user.last_name}\n"
        
        if user.username:
            user_info += f"🏷️ 用户名: @{user.username}\n"
        
        user_info += f"""
🤖 是否为机器人: {'是' if user.is_bot else '否'}

📋 **配置说明**:
要将你设为管理员，请在 .env 文件中设置：
`ADMIN_IDS={user.id}`

如果有多个管理员，用逗号分隔：
`ADMIN_IDS={user.id},其他用户ID`
"""
        
        await message.reply_text(user_info)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /stats 命令"""
        message = update.message
        if not message:
            return
        
        # 检查是否为管理员
        if not self._is_admin(message.from_user.id):
            await message.reply_text("⚠️ 只有管理员可以使用此命令")
            return
        
        # 只在群组中使用
        if message.chat.type not in ['group', 'supergroup']:
            await message.reply_text("⚠️ 此命令只能在群组中使用")
            return
        
        try:
            stats = self.storage.get_chat_stats(message.chat.id)
            
            if self.config.STORAGE_FORMAT == 'sqlite':
                stats_text = f"""
📊 群组统计信息

💬 总消息数: {stats['total_messages']}
📅 记录时间范围: {stats['date_range'][0] or '无'} ~ {stats['date_range'][1] or '无'}

👥 最活跃用户 (Top 5):
"""
                for i, (username, first_name, count) in enumerate(stats['top_users'][:5], 1):
                    user_display = first_name
                    if username:
                        user_display += f" (@{username})"
                    stats_text += f"{i}. {user_display}: {count} 条消息\n"
            
            else:
                stats_text = f"""
📊 群组统计信息

📁 记录文件数: {stats['total_files']}
📄 文件列表: {', '.join(stats['files'][:5])}
"""
            
            await message.reply_text(stats_text)
        
        except Exception as e:
            self.logger.error(f"获取统计信息时发生错误: {e}")
            await message.reply_text("❌ 获取统计信息失败")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        message = update.message
        if not message:
            return
        
        # 检查是否为管理员
        if not self._is_admin(message.from_user.id):
            await message.reply_text("⚠️ 只有管理员可以使用此命令")
            return
        
        status_text = f"""
🤖 机器人状态

✅ 运行正常
📊 存储格式: {self.config.STORAGE_FORMAT}
📁 数据目录: {self.config.DATA_DIR}
🎵 记录媒体: {'是' if self.config.LOG_MEDIA else '否'}
💾 下载媒体: {'是' if self.config.DOWNLOAD_MEDIA else '否'}

⚙️ 配置信息:
- 忽略命令: {'是' if self.config.IGNORE_COMMANDS else '否'}
- 忽略机器人: {'是' if self.config.IGNORE_BOTS else '否'}
- 允许的群组数: {len(self.config.ALLOWED_GROUPS) if self.config.ALLOWED_GROUPS else '无限制'}

🤖 AI 总结功能:
- 状态: {'启用' if self.config.ENABLE_AI_SUMMARY else '禁用'}
"""
        
        if self.config.ENABLE_AI_SUMMARY and self.scheduler:
            summary_stats = self.scheduler.get_summary_stats()
            status_text += f"- 提供商: {summary_stats['provider']}\n"
            status_text += f"- 自动总结时间: {summary_stats['auto_summary_time']}\n"
            status_text += f"- 已生成总结数: {summary_stats['total_summaries']}\n"
        
        await message.reply_text(status_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()
        
        # 检查是否为管理员
        if not self._is_admin(query.from_user.id):
            await query.edit_message_text("⚠️ 只有管理员可以使用此功能")
            return
        
        data = query.data
        
        if data == "close_menu":
            await query.edit_message_text("✅ 菜单已关闭")
            return
        
        if data == "summary_24h":
            await self._show_group_selection(query, "24h")
        elif data == "summary_3d":
            await self._show_group_selection(query, "3d")
        elif data == "generate_today":
            await self._show_group_selection(query, "today")
        elif data == "get_saved":
            await self._show_saved_summary_options(query)
        elif data == "show_summary_options":
            # 显示日期输入提示或群组选择
            await self._show_summary_date_selection(query)
        elif data == "show_history_options":
            # 显示历史总结的群组选择
            await self._show_history_group_selection_callback(query)
        elif data.startswith("group_"):
            # 处理群组选择
            parts = data.split("_")
            if len(parts) >= 3:
                period = parts[1]  # 24h 或 3d 或 today
                chat_id = int(parts[2])
                await self._generate_realtime_summary(query, chat_id, period)
        elif data.startswith("saved_"):
            # 处理已保存总结的选择
            parts = data.split("_")
            if len(parts) >= 3:
                period = parts[1]  # 1d 或 3d
                chat_id = int(parts[2]) if parts[2] != "all" else None
                await self._show_saved_summaries(query, chat_id, period)
        elif data == "back_main":
            # 返回主菜单 - 重新调用 start_command 的逻辑
            await self._show_main_menu(query)
        elif data.startswith("sum_"):
            # 处理总结请求
            parts = data.split("_")
            if len(parts) >= 3:
                chat_id = int(parts[1])
                date_param = parts[2]
                await self._handle_summary_request(query, chat_id, date_param)
        elif data.startswith("hist_"):
            # 处理历史总结请求
            parts = data.split("_")
            if len(parts) >= 2:
                chat_id = int(parts[1])
                await self._handle_history_request(query, chat_id)
        elif data == "cancel":
            await query.edit_message_text("❌ 操作已取消")
        elif data.startswith("sumdate_"):
            # 处理指定日期的总结
            parts = data.split("_")
            if len(parts) >= 2:
                days_ago = int(parts[1])
                await self._show_group_selection_for_date(query, days_ago)
    
    async def _show_group_selection(self, query, period: str):
        """显示群组选择界面"""
        # 获取可用的群组
        available_groups = self._get_available_groups()
        
        if not available_groups:
            await query.edit_message_text("❌ 没有找到可用的群组数据")
            return
        
        period_text = "24小时" if period == "24h" else "3天"
        keyboard = []
        
        # 为每个群组添加按钮
        for chat_id, group_info in available_groups.items():
            group_name = group_info.get('title', f'群组 {chat_id}')[:30]  # 限制长度
            callback_data = f"group_{period}_{chat_id}"
            keyboard.append([InlineKeyboardButton(f"📱 {group_name}", callback_data=callback_data)])
        
        # 添加返回按钮
        keyboard.append([InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
📊 **选择要生成{period_text}总结的群组**

以下是有消息记录的群组：

👆 请选择一个群组来生成实时AI总结
        """
        
        await self._safe_send_text(query, text, reply_markup=reply_markup)
    
    async def _show_saved_summary_options(self, query):
        """显示已保存总结的选项"""
        keyboard = [
            [
                InlineKeyboardButton("📅 过去1天", callback_data="saved_1d_all"),
                InlineKeyboardButton("📈 过去3天", callback_data="saved_3d_all")
            ],
            [
                InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
📋 **查看已保存的总结**

选择时间范围：

📅 **过去1天** - 查看昨天的总结
📈 **过去3天** - 查看最近3天的总结

👆 请选择时间范围
        """
        
        await self._safe_send_text(query, text, reply_markup=reply_markup)
    
    async def _generate_realtime_summary(self, query, chat_id: int, period: str):
        """生成实时总结"""
        if period == "today":
            period_text = "今日24小时"
        elif period == "24h":
            period_text = "24小时"
        else:
            period_text = "3天"
        
        # 显示处理中消息
        await query.edit_message_text(f"🤖 正在生成{period_text}总结，请稍候...")
        
        try:
            # 计算日期范围
            end_date = datetime.now()
            if period == "24h":
                start_date = end_date - timedelta(days=1)
            elif period == "today":
                start_date = end_date - timedelta(days=1)
            else:  # 3d
                start_date = end_date - timedelta(days=3)
            
            # 获取消息数据
            messages = self._get_messages_in_range(chat_id, start_date, end_date)
            
            if not messages:
                await query.edit_message_text(f"❌ 在{period_text}内没有找到消息记录")
                return
            
            if len(messages) < self.config.MIN_MESSAGES_FOR_SUMMARY:
                await query.edit_message_text(
                    f"⚠️ 消息数量不足（{len(messages)}条），最少需要{self.config.MIN_MESSAGES_FOR_SUMMARY}条消息"
                )
                return
            
            # 使用AI生成总结
            if self.ai_summarizer:
                if period == "today":
                    # 使用新的今日总结方法，会自动保存到当天的文件
                    self.logger.info(f"开始生成今日总结 - 群组: {chat_id}")
                    summary = await self.scheduler.generate_today_summary(chat_id)
                    self.logger.info(f"今日总结结果: {'成功' if summary else '失败(None)'}")
                elif period == "24h":
                    # 24小时总结也使用今日总结方法
                    self.logger.info(f"开始生成24小时实时总结 - 群组: {chat_id}")
                    summary = await self.ai_summarizer.generate_today_summary(chat_id)
                    self.logger.info(f"24小时实时总结结果: {'成功' if summary else '失败(None)'}")
                else:
                    # 3天总结，使用特殊处理
                    self.logger.info(f"开始生成3天实时总结 - 群组: {chat_id}")
                    summary = await self.ai_summarizer.generate_daily_summary(chat_id, end_date)
                    self.logger.info(f"3天实时总结结果: {'成功' if summary else '失败(None)'}")
                
                if summary:
                    # 限制总结长度以适应Telegram消息限制
                    if len(summary) > 4000:
                        summary = summary[:4000] + "\n\n... (总结已截断)"
                    
                    group_name = self._get_group_name(chat_id)
                    
                    # 为today类型添加保存提示
                    save_note = "\n💾 **此总结已自动保存到历史记录**" if period == "today" else ""
                    
                    result_text = f"""
📊 **{group_name} - {period_text}总结**

{summary}
{save_note}

---
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📨 消息数量: {len(messages)}条
                    """
                    
                    # 添加返回按钮
                    keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(result_text, reply_markup=reply_markup)
                else:
                    await query.edit_message_text("❌ AI总结生成失败，请稍后重试")
            else:
                await query.edit_message_text("❌ AI总结服务不可用")
                
        except Exception as e:
            self.logger.error(f"生成实时总结时出错: {e}")
            await query.edit_message_text(f"❌ 生成总结时发生错误: {str(e)}")
    
    async def _show_saved_summaries(self, query, chat_id: Optional[int], period: str):
        """显示已保存的总结"""
        period_text = "1天" if period == "1d" else "3天"
        
        try:
            # 这里应该从存储中获取已保存的总结
            # 暂时显示占位信息
            text = f"""
📋 **过去{period_text}的已保存总结**

⚠️ 此功能正在开发中...

当前会显示：
- 自动生成的日常总结
- 手动保存的总结记录
- 总结的生成时间和统计信息

---
💡 提示：使用实时总结功能可以立即生成最新的对话分析
            """
            
            keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self._safe_send_text(query, text, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"获取已保存总结时出错: {e}")
            await query.edit_message_text("❌ 获取已保存总结失败")
    
    def _get_available_groups(self) -> Dict[int, Dict[str, Any]]:
        """获取有消息记录的群组"""
        try:
            groups = {}
            data_dir = self.config.DATA_DIR
            
            if not os.path.exists(data_dir):
                return groups
            
            # 扫描数据文件
            for filename in os.listdir(data_dir):
                if filename.startswith('chat_') and filename.endswith('.json'):
                    try:
                        parts = filename.split('_')
                        if len(parts) >= 3:
                            chat_id = int(parts[1])
                            
                            # 尝试读取文件获取群组信息
                            filepath = os.path.join(data_dir, filename)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                import json
                                messages = json.load(f)
                                if messages:
                                    groups[chat_id] = {
                                        'title': messages[0].get('chat_title', f'群组 {chat_id}'),
                                        'message_count': len(messages)
                                    }
                    except (ValueError, json.JSONDecodeError, IOError):
                        continue
            
            return groups
            
        except Exception as e:
            self.logger.error(f"获取群组信息时出错: {e}")
            return {}
    
    def _get_messages_in_range(self, chat_id: int, start_date: datetime, end_date: datetime):
        """获取指定时间范围内的消息"""
        try:
            all_messages = []
            data_dir = self.config.DATA_DIR
            
            # 遍历日期范围内的所有日期
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_str = current_date.strftime('%Y%m%d')
                # 使用绝对值来匹配文件名（文件存储时使用abs(chat_id)）
                filename = f'chat_{abs(chat_id)}_{date_str}.json'
                filepath = os.path.join(data_dir, filename)
                
                self.logger.info(f"尝试读取文件: {filename}, 存在: {os.path.exists(filepath)}")
                
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            import json
                            messages = json.load(f)
                            all_messages.extend(messages)
                            self.logger.info(f"从 {filename} 读取 {len(messages)} 条消息")
                    except (json.JSONDecodeError, IOError) as e:
                        self.logger.error(f"读取文件 {filename} 失败: {e}")
                        pass
                
                current_date += timedelta(days=1)
            
            self.logger.info(f"总共获取 {len(all_messages)} 条消息，日期范围: {start_date.date()} 到 {end_date.date()}")
            return all_messages
            
        except Exception as e:
            self.logger.error(f"获取时间范围消息时出错: {e}")
            return []
    
    def _get_group_name(self, chat_id: int) -> str:
        """获取群组名称"""
        groups = self._get_available_groups()
        return groups.get(chat_id, {}).get('title', f'群组 {chat_id}')
    
    def _escape_markdown(self, text: str) -> str:
        """转义Markdown特殊字符"""
        # 转义Markdown特殊字符
        special_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    async def _safe_send_text(self, message_or_query, text: str, reply_markup=None, use_markdown=False):
        """安全地发送文本，处理Markdown解析错误"""
        try:
            if use_markdown:
                if hasattr(message_or_query, 'reply_text'):
                    await message_or_query.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await message_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                if hasattr(message_or_query, 'reply_text'):
                    await message_or_query.reply_text(text, reply_markup=reply_markup)
                else:
                    await message_or_query.edit_message_text(text, reply_markup=reply_markup)
        except Exception as e:
            # 如果Markdown解析失败，尝试不使用格式化
            self.logger.warning(f"Markdown解析失败，使用纯文本: {e}")
            # 移除所有Markdown格式
            clean_text = text.replace('**', '').replace('*', '').replace('_', '').replace('`', '')
            if hasattr(message_or_query, 'reply_text'):
                await message_or_query.reply_text(clean_text, reply_markup=reply_markup)
            else:
                await message_or_query.edit_message_text(clean_text, reply_markup=reply_markup)
    
    async def _show_main_menu(self, query):
        """显示主菜单"""
        welcome_text = """
🤖 **Telegram Note Taker Bot**

欢迎使用智能群组消息记录和总结机器人！

我可以帮助您：
✅ 自动记录群组消息
✅ 生成AI智能总结
✅ 分析对话内容和趋势
✅ 保存和查看历史记录

💡 **快速开始**
• 使用 /help 查看详细使用说明
• 使用 /myid 获取您的用户 ID
• 使用下方按钮访问所有功能

**📱 功能菜单**

点击下方按钮生成今日总结：
"""
        
        keyboard = [
            [
                InlineKeyboardButton("� 生成今日总结", callback_data="generate_today")
            ]
            # 其他功能按钮保留在代码中，以后可以启用
            # [
            #     InlineKeyboardButton("� 获取24小时总结", callback_data="summary_24h"),
            #     InlineKeyboardButton("� 获取3天总结", callback_data="summary_3d")
            # ],
            # [
            #     InlineKeyboardButton("📋 查看已保存的总结", callback_data="get_saved")
            # ],
            # [
            #     InlineKeyboardButton("📅 生成指定日期总结", callback_data="show_summary_options"),
            #     InlineKeyboardButton("📚 查看历史总结", callback_data="show_history_options")
            # ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self._safe_send_text(query, welcome_text, reply_markup=reply_markup)
    
    async def _show_summary_date_selection(self, query):
        """显示日期选择界面（用于生成指定日期的总结）"""
        keyboard = [
            [
                InlineKeyboardButton("📅 昨天", callback_data="sumdate_1"),
                InlineKeyboardButton("📅 前天", callback_data="sumdate_2")
            ],
            [
                InlineKeyboardButton("📅 3天前", callback_data="sumdate_3"),
                InlineKeyboardButton("📅 7天前", callback_data="sumdate_7")
            ],
            [
                InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
📅 **选择要生成总结的日期**

请选择时间范围：

👆 点击按钮选择日期，或在群组中使用命令：
`/summary 1` - 昨天
`/summary 2024-11-10` - 指定日期
"""
        
        await self._safe_send_text(query, text, reply_markup=reply_markup)
    
    async def _show_group_selection_for_date(self, query, days_ago: int):
        """为指定日期显示群组选择"""
        available_groups = self._get_available_groups()
        
        if not available_groups:
            await query.edit_message_text("❌ 没有找到可用的群组数据")
            return
        
        target_date = datetime.now() - timedelta(days=days_ago)
        date_str = target_date.strftime('%Y-%m-%d')
        
        keyboard = []
        for chat_id, group_info in available_groups.items():
            group_name = group_info.get('title', f'群组 {chat_id}')[:30]
            callback_data = f"sum_{chat_id}_{days_ago}"
            keyboard.append([InlineKeyboardButton(f"📱 {group_name}", callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="show_summary_options")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
📊 **选择要生成总结的群组**

日期：{date_str}

以下是有消息记录的群组：

👆 请选择一个群组来生成总结
"""
        
        await self._safe_send_text(query, text, reply_markup=reply_markup)
    
    async def _show_history_group_selection_callback(self, query):
        """显示历史总结的群组选择（回调版本）"""
        available_groups = self._get_available_groups()
        
        if not available_groups:
            await query.edit_message_text("❌ 没有找到可用的群组数据")
            return
        
        keyboard = []
        for chat_id, group_info in available_groups.items():
            group_name = group_info.get('title', f'群组 {chat_id}')[:30]
            callback_data = f"hist_{chat_id}"
            keyboard.append([InlineKeyboardButton(f"📱 {group_name}", callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
📚 **选择要查看历史总结的群组**

以下是有消息记录的群组：

👆 请选择一个群组来查看总结历史
"""
        
        await self._safe_send_text(query, text, reply_markup=reply_markup)
    
    async def _handle_summary_request(self, query, chat_id: int, date_param: str):
        """处理总结请求"""
        await query.edit_message_text("🤖 正在生成总结，请稍候...")
        
        try:
            # 解析日期参数
            if date_param.isdigit():
                days_ago = int(date_param)
                target_date = datetime.now() - timedelta(days=days_ago)
            else:
                target_date = datetime.strptime(date_param, '%Y-%m-%d')
            
            # 生成总结
            if self.ai_summarizer:
                summary = await self.ai_summarizer.generate_daily_summary(chat_id, target_date)
                
                if summary:
                    # 获取群组名称
                    group_name = self._get_group_name(chat_id)
                    date_str = target_date.strftime('%Y-%m-%d')
                    
                    # 限制总结长度
                    if len(summary) > 4000:
                        summary = summary[:4000] + "\n\n... (总结已截断)"
                    
                    result_text = f"""
📊 **{group_name} - {date_str} 总结**

{summary}

---
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(result_text, reply_markup=reply_markup)
                else:
                    await query.edit_message_text(f"❌ 无法生成 {target_date.strftime('%Y-%m-%d')} 的总结（消息数量不足或其他错误）")
            else:
                await query.edit_message_text("❌ AI总结服务不可用")
                
        except ValueError:
            await query.edit_message_text("❌ 日期格式错误")
        except Exception as e:
            self.logger.error(f"总结生成错误: {e}")
            await query.edit_message_text(f"❌ 生成总结时发生错误: {str(e)}")
    
    async def _handle_history_request(self, query, chat_id: int):
        """处理历史总结请求"""
        await query.edit_message_text("📚 正在获取历史总结，请稍候...")
        
        try:
            if self.ai_summarizer:
                # 获取历史总结
                summaries = self.ai_summarizer.get_summary_history(chat_id, 7)
                
                if not summaries:
                    group_name = self._get_group_name(chat_id)
                    await query.edit_message_text(f"📝 {group_name} 暂无历史总结记录")
                    return
                
                group_name = self._get_group_name(chat_id)
                
                if len(summaries) == 1:
                    # 如果只有一个总结，显示完整内容
                    summary = summaries[0]
                    date = summary.get('date', '未知日期')
                    message_count = summary.get('message_count', 0)
                    generated_at = summary.get('generated_at', '未知时间')
                    summary_content = summary.get('summary', '总结内容不可用')
                    
                    # 限制总结长度
                    if len(summary_content) > 3500:
                        summary_content = summary_content[:3500] + "\n\n... (总结已截断)"
                    
                    history_text = f"""📚 {group_name} - {date} 总结

{summary_content}

---
📊 消息数: {message_count} 条
⏰ 生成时间: {generated_at}"""
                
                else:
                    # 如果有多个总结，显示列表
                    history_text = f"📚 {group_name} - 最近的总结历史\n\n"
                    
                    for i, summary in enumerate(summaries[:5], 1):  # 最多显示5个
                        date = summary.get('date', '未知日期')
                        message_count = summary.get('message_count', 0)
                        generated_at = summary.get('generated_at', '未知时间')
                        
                        history_text += f"{i}. 📅 {date}\n"
                        history_text += f"   💬 消息数: {message_count}\n"
                        history_text += f"   ⏰ 生成时间: {generated_at}\n\n"
                    
                    if len(summaries) > 5:
                        history_text += f"... 还有 {len(summaries) - 5} 个历史总结\n\n"
                    
                    history_text += "💡 提示：选择特定日期可查看完整总结内容"
                
                keyboard = [[InlineKeyboardButton("🔙 返回主菜单", callback_data="back_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await self._safe_send_text(query, history_text, reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ AI总结服务不可用")
                
        except Exception as e:
            self.logger.error(f"获取历史总结错误: {e}")
            await query.edit_message_text(f"❌ 获取历史总结失败: {str(e)}")
    
    async def _setup_bot_commands(self, application):
        """设置机器人命令菜单"""
        try:
            # 基础命令（所有用户都能看到）
            commands = [
                BotCommand("start", "打开功能菜单和快速开始指南"),
                BotCommand("help", "查看详细帮助文档和使用说明"),
                BotCommand("myid", "获取你的用户ID"),
            ]
            
            # 管理员命令（如果启用了AI总结功能）
            if self.config.ENABLE_AI_SUMMARY:
                commands.extend([
                    BotCommand("stats", "查看群组统计信息"),
                    BotCommand("status", "查看机器人状态"),
                ])
            
            # 设置命令菜单
            await application.bot.set_my_commands(commands)
            self.logger.info(f"已设置 {len(commands)} 个机器人命令")
            print(f"✅ 命令菜单已设置（共{len(commands)}个命令）", flush=True)
            
        except Exception as e:
            self.logger.error(f"设置机器人命令失败: {e}")
            print(f"⚠️ 设置命令菜单失败: {e}", flush=True)
    
    def run(self):
        """启动机器人"""
        self.logger.info("正在启动 Telegram Note Taker Bot...")
        
        # 创建应用程序
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # 初始化任务调度器（但不立即启动异步任务）
        if self.config.ENABLE_AI_SUMMARY:
            self.scheduler = TaskScheduler(application)
            self.scheduler.start()
        
        # 添加处理器
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("myid", self.myid_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("status", self.status_command))
        
        # 添加回调查询处理器
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 添加消息处理器
        application.add_handler(MessageHandler(
            filters.ALL & ~filters.COMMAND,
            self.handle_message
        ))
        
        self.logger.info("Bot 已启动，正在监听消息...")
        print("🤖 Bot 已启动，正在监听消息...", flush=True)
        print("📋 配置信息:", flush=True)
        allowed_groups = self.config.get_allowed_groups()
        print(f"   - 允许的群组: {allowed_groups if allowed_groups else '所有群组'}", flush=True)
        print(f"   - 管理员: {self.config.get_admin_ids()}", flush=True)
        print("=" * 50, flush=True)
        
        # 注册启动和关闭回调
        async def post_init(application):
            # 设置机器人命令菜单
            await self._setup_bot_commands(application)
            
            if self.scheduler:
                await self.scheduler.start_async()
        
        async def post_shutdown(application):
            if self.scheduler:
                self.scheduler.stop()
        
        application.post_init = post_init
        application.post_shutdown = post_shutdown
        
        try:
            # 启动机器人
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        finally:
            # 停止调度器
            if self.scheduler:
                self.scheduler.stop()

def main():
    """主函数"""
    bot = TelegramNoteTaker()
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.logger.info("收到停止信号，正在关闭...")
    except Exception as e:
        bot.logger.error(f"运行时发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()