#!/bin/bash

# Telegram Note Taker 启动脚本

echo "🤖 正在启动 Telegram Note Taker Bot..."

# 检查是否安装了依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到 requirements.txt 文件"
    exit 1
fi

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    exit 1
fi

# 安装依赖（如果需要）
echo "📦 检查并安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，请复制 .env.example 并配置"
    if [ -f ".env.example" ]; then
        echo "💡 你可以运行: cp .env.example .env"
    fi
    exit 1
fi

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 检查必要的环境变量
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ 请在 .env 文件中设置 TELEGRAM_BOT_TOKEN"
    exit 1
fi

# 创建必要的目录
mkdir -p data logs

echo "✅ 环境检查完成"
echo "🚀 启动 Bot..."

# 进入 src 目录并运行 Bot
cd src
python bot.py