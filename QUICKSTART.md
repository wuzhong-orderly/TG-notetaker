# 🚀 快速开始指南

## 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 输入机器人名称（例如：My Note Taker）
4. 输入机器人用户名（必须以 `bot` 结尾，例如：my_note_taker_bot）
5. 保存获得的 Bot Token（类似：`123456789:ABCdefGHIjklMNOpqrSTUvwxyz`）

## 2. 配置项目

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Bot Token
# TELEGRAM_BOT_TOKEN=你的机器人token
```

## 3. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

## 4. 测试配置

```bash
# 运行配置测试
python test_config.py
```

## 5. 启动机器人

```bash
# 方法一：使用启动脚本
./run.sh

# 方法二：直接运行
cd src && python bot.py
```

## 6. 使用机器人

1. 将机器人添加到你想记录的群组
2. 给机器人管理员权限（确保能看到所有消息）
3. 机器人会自动开始记录消息
4. 使用 `/stats` 查看统计信息

## Docker 部署

```bash
# 1. 创建 .env 文件并配置
cp .env.example .env

# 2. 启动容器
docker-compose up -d

# 3. 查看日志
docker-compose logs -f telegram-notetaker
```

## 常见问题

**Q: 机器人无法接收消息？**
A: 确保机器人有管理员权限，或者群组允许机器人看到消息

**Q: 如何找到群组 ID？**
A: 将机器人添加到群组后，在群组发送任意消息，查看日志文件中的 `chat_id`

**Q: 如何设置管理员？**
A: 在 `config/config.py` 的 `ADMIN_IDS` 列表中添加用户 ID

**Q: 消息存储在哪里？**
A: 默认存储在 `data/` 目录，可以在配置中修改存储格式和位置