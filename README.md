# Telegram Note Taker

一个功能强大的 Telegram 群组消息记录机器人，可以自动记录群组中的所有对话内容。

## 功能特性

- 📝 **自动记录消息**: 自动记录群组中的所有文字消息
- 🎵 **多媒体支持**: 记录图片、视频、音频、文档等媒体文件信息
- 💾 **多种存储格式**: 支持 JSON、文本文件和 SQLite 数据库存储
- 🤖 **AI 智能总结**: 使用 AI 自动生成每日聊天总结，支持多种 AI 服务
- ⏰ **定时任务**: 支持每日自动总结，可配置执行时间
- 🔒 **访问控制**: 支持管理员权限和群组白名单
- 📊 **统计功能**: 提供群组活跃度统计和用户排行
- 🎛️ **灵活配置**: 丰富的配置选项，适应不同使用场景
- 🚀 **简单部署**: 支持直接运行或 Docker 部署

## 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建新的机器人
3. 按提示设置机器人名称和用户名
4. 保存获得的 Bot Token

### 2. 安装和配置

```bash
# 克隆项目
git clone <your-repo-url>
cd TG-notetaker

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Bot Token 和 AI API Key（可选）
```

### 3. 配置 Bot

编辑 `.env` 文件：

```bash
# 必须：你的 Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 可选：管理员用户ID（用逗号分隔）
ADMIN_IDS=123456789,987654321

# 可选：允许记录的群组ID（用逗号分隔，留空表示允许所有群组）
ALLOWED_GROUPS=-1001234567890,-1009876543210

# AI 总结功能（可选）
ENABLE_AI_SUMMARY=true
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 运行 Bot

```bash
# 直接运行
cd src
python bot.py

# 或使用启动脚本
./run.sh
```

### 5. 使用 Bot

1. 将机器人添加到你想记录的群组中
2. 给机器人管理员权限（推荐，确保能看到所有消息）
3. 机器人会自动开始记录消息

## 配置选项

在 `config/config.py` 中可以修改以下配置：

### 基本配置
- `BOT_TOKEN`: Telegram Bot Token
- `ADMIN_IDS`: 管理员用户ID列表
- `ALLOWED_GROUPS`: 允许记录的群组ID列表

### 存储配置
- `STORAGE_FORMAT`: 存储格式 (`json`, `txt`, `sqlite`)
- `MAX_MESSAGES_PER_FILE`: 每个文件最大消息数
- `LOG_MEDIA`: 是否记录媒体文件信息
- `DOWNLOAD_MEDIA`: 是否下载媒体文件

### 消息过滤
- `IGNORE_COMMANDS`: 忽略以 `/` 开头的命令
- `IGNORE_BOTS`: 忽略其他机器人的消息

## 管理员命令

机器人支持以下管理员命令：

- `/start` - 显示帮助信息
- `/stats` - 显示群组统计信息
- `/status` - 显示机器人运行状态
- `/summary [日期|天数]` - 生成 AI 总结（例如：`/summary 1` 或 `/summary 2024-01-01`）
- `/summary_history` - 查看最近的总结历史

## AI 总结功能

### 支持的 AI 服务
- **OpenAI**: GPT-4、GPT-3.5 等模型
- **Anthropic Claude**: Claude-3 系列模型
- **本地模型**: 支持 Ollama 等本地部署的模型（开发中）

### 总结特性
- **自动总结**: 每日定时生成前一天的聊天总结
- **手动总结**: 管理员可随时生成指定日期的总结
- **多语言支持**: 支持中文、英文、日文等多种语言
- **多种格式**: 支持要点列表、段落、结构化等格式
- **智能过滤**: 自动过滤无意义内容，突出重要信息

### 配置 AI 总结

在 `.env` 文件中添加以下配置：

```bash
# 启用 AI 总结
ENABLE_AI_SUMMARY=true

# 选择 AI 服务提供商
AI_PROVIDER=openai

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# 总结设置
SUMMARY_LANGUAGE=zh          # 总结语言 (zh/en/ja)
SUMMARY_LENGTH=medium        # 总结长度 (short/medium/long)
SUMMARY_STYLE=bullet         # 总结格式 (bullet/paragraph/structured)
AUTO_SUMMARY_TIME=23:30      # 自动总结时间
MIN_MESSAGES_FOR_SUMMARY=10  # 触发总结的最小消息数
SEND_SUMMARY_TO_CHAT=false   # 是否自动发送总结到群组
```

## 存储格式

### JSON 格式
消息以 JSON 数组形式存储，包含完整的消息信息：

```json
[
  {
    "message_id": 123,
    "chat_id": -1001234567890,
    "chat_title": "测试群组",
    "user_id": 987654321,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "message_text": "Hello, World!",
    "message_type": "text",
    "timestamp": "2024-01-01 12:00:00",
    "media_info": null
  }
]
```

### 文本格式
消息以简洁的文本格式存储：

```
[2024-01-01 12:00:00] Test User (@testuser): Hello, World!
[2024-01-01 12:01:00] Another User: How are you?
```

### SQLite 格式
消息存储在关系数据库中，支持复杂查询和统计。

## 文件结构

```
TG-notetaker/
├── config/
│   └── config.py          # 配置文件
├── src/
│   ├── bot.py             # 主程序
│   └── storage.py         # 存储模块
├── data/                  # 数据存储目录
├── logs/                  # 日志目录
├── .env.example           # 环境变量示例
├── requirements.txt       # 依赖包列表
├── run.sh                 # 启动脚本
└── README.md              # 说明文档
```

## Docker 部署

使用 Docker 部署：

```bash
# 构建镜像
docker build -t telegram-notetaker .

# 运行容器
docker run -d \
  --name telegram-notetaker \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  telegram-notetaker
```

## 注意事项

1. **隐私保护**: 请确保遵守当地法律法规和群组成员的隐私权
2. **权限设置**: 建议为机器人设置适当的管理员权限
3. **存储空间**: 长时间运行可能产生大量数据，请定期清理
4. **安全性**: 保护好你的 Bot Token，不要泄露给他人

## 故障排除

### 常见问题

1. **Bot 无法接收消息**
   - 检查 Bot Token 是否正确
   - 确认机器人已添加到群组
   - 检查机器人是否有足够的权限

2. **存储失败**
   - 检查数据目录权限
   - 确认磁盘空间充足
   - 查看日志文件了解详细错误

3. **命令无响应**
   - 确认用户ID在管理员列表中
   - 检查网络连接
   - 查看机器人日志

### 日志查看

日志文件位于 `logs/telegram_notetaker.log`：

```bash
tail -f logs/telegram_notetaker.log
```

## 开发和贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest

# 代码格式化
black src/
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 更新日志

### v1.0.0
- 基本的消息记录功能
- 多种存储格式支持
- 管理员命令
- 统计功能

---

如有问题或建议，请提交 [Issue](https://github.com/your-username/TG-notetaker/issues)。