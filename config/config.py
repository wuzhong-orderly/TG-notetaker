"""
Telegram Note Taker 配置文件
"""
import os
from typing import List

# 自动加载 .env 文件
def _load_env_file():
    """加载 .env 文件中的环境变量"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        try:
            # 尝试使用 python-dotenv
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            # 如果没有 python-dotenv，手动解析
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# 在导入时自动加载环境变量
_load_env_file()

class Config:
    """应用程序配置类"""
    
    # Telegram Bot Token (必须设置)
    BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # 管理员用户ID列表 (可以管理bot的用户)
    @classmethod
    def get_admin_ids(cls) -> List[int]:
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if admin_ids_str:
            try:
                return [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]
            except ValueError:
                return []
        return []
    
    ADMIN_IDS: List[int] = []  # 将在运行时动态获取
    
    # 允许记录的群组ID列表 (留空表示允许所有群组)
    @classmethod
    def get_allowed_groups(cls) -> List[int]:
        allowed_groups_str = os.getenv('ALLOWED_GROUPS', '')
        if allowed_groups_str:
            try:
                return [int(x.strip()) for x in allowed_groups_str.split(',') if x.strip().lstrip('-').isdigit()]
            except ValueError:
                return []
        return []
    
    ALLOWED_GROUPS: List[int] = []  # 将在运行时动态获取
    
    # 数据存储设置
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    LOG_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    # 消息存储格式 ('json', 'txt', 'sqlite')
    STORAGE_FORMAT: str = 'json'
    
    # 每个文件最大消息数量 (用于分割大文件)
    MAX_MESSAGES_PER_FILE: int = 10000
    
    # 是否记录媒体文件信息
    LOG_MEDIA: bool = True
    
    # 是否下载媒体文件
    DOWNLOAD_MEDIA: bool = False
    
    # 媒体文件下载路径
    MEDIA_DIR: str = os.path.join(DATA_DIR, 'media')
    
    # 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    LOG_LEVEL: str = 'INFO'
    
    # 消息过滤设置
    IGNORE_COMMANDS: bool = True  # 忽略以 / 开头的命令
    IGNORE_BOTS: bool = True      # 忽略其他机器人的消息
    
    # 时间格式
    TIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    
    # 文件名时间格式
    FILENAME_TIME_FORMAT: str = '%Y%m%d'
    
    # ============= AI 总结功能配置 =============
    
    # 是否启用 AI 总结功能
    ENABLE_AI_SUMMARY: bool = os.getenv('ENABLE_AI_SUMMARY', 'false').lower() == 'true'
    
    # AI 服务提供商 ('openai', 'claude', 'gemini', 'local')
    AI_PROVIDER: str = os.getenv('AI_PROVIDER', 'openai')
    
    # AI API 配置
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_BASE_URL: str = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    
    # AI 总结配置
    SUMMARY_LANGUAGE: str = os.getenv('SUMMARY_LANGUAGE', 'zh')  # 总结语言
    SUMMARY_LENGTH: str = os.getenv('SUMMARY_LENGTH', 'medium')  # 'short', 'medium', 'long'
    SUMMARY_STYLE: str = os.getenv('SUMMARY_STYLE', 'bullet')   # 'bullet', 'paragraph', 'structured'
    
    # 自动总结时间 (24小时格式，例如 "23:30")
    AUTO_SUMMARY_TIME: str = os.getenv('AUTO_SUMMARY_TIME', '23:30')
    
    # 最小消息数量才触发总结
    MIN_MESSAGES_FOR_SUMMARY: int = int(os.getenv('MIN_MESSAGES_FOR_SUMMARY', '10'))
    
    # 总结存储目录
    SUMMARY_DIR: str = os.path.join(DATA_DIR, 'summaries')
    
    # 是否在群组中发送总结
    SEND_SUMMARY_TO_CHAT: bool = os.getenv('SEND_SUMMARY_TO_CHAT', 'false').lower() == 'true'

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        if not cls.BOT_TOKEN:
            print("错误: 请设置 TELEGRAM_BOT_TOKEN 环境变量")
            return False
        
        # 创建必要的目录
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        if cls.DOWNLOAD_MEDIA:
            os.makedirs(cls.MEDIA_DIR, exist_ok=True)
        if cls.ENABLE_AI_SUMMARY:
            os.makedirs(cls.SUMMARY_DIR, exist_ok=True)
        
        # 验证 AI 配置
        if cls.ENABLE_AI_SUMMARY:
            if cls.AI_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
                print("警告: 启用了 AI 总结但未设置 OPENAI_API_KEY")
            elif cls.AI_PROVIDER == 'claude' and not cls.ANTHROPIC_API_KEY:
                print("警告: 启用了 AI 总结但未设置 ANTHROPIC_API_KEY")
        
        return True