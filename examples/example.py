"""
Telegram Note Taker 使用示例

本文件展示如何使用和配置 Telegram Note Taker
"""

# 示例 1: 基本配置
"""
1. 复制 .env.example 为 .env
2. 在 .env 中填入你的 Bot Token：
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz

3. 运行机器人：
   ./run.sh
   
   或者直接运行：
   cd src && python bot.py
"""

# 示例 2: 高级配置
"""
在 config/config.py 中自定义设置：

class Config:
    # 只允许特定群组
    ALLOWED_GROUPS = [-1001234567890, -1009876543210]
    
    # 设置管理员
    ADMIN_IDS = [123456789, 987654321]
    
    # 使用 SQLite 存储
    STORAGE_FORMAT = 'sqlite'
    
    # 下载媒体文件
    DOWNLOAD_MEDIA = True
    
    # 忽略机器人消息
    IGNORE_BOTS = True
"""

# 示例 3: Docker 部署
"""
1. 创建 .env 文件：
   TELEGRAM_BOT_TOKEN=your_token_here
   
2. 使用 Docker Compose：
   docker-compose up -d
   
3. 查看日志：
   docker-compose logs -f telegram-notetaker
"""

# 示例 4: 获取群组和用户 ID
"""
要获取群组 ID：
1. 将机器人添加到群组
2. 在群组中发送任意消息
3. 查看日志文件，找到 chat_id

要获取用户 ID：
1. 私聊机器人发送 /start
2. 查看日志文件，找到 user_id
"""

if __name__ == "__main__":
    print("这是 Telegram Note Taker 的示例文件")
    print("请查看代码注释了解使用方法")