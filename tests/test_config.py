#!/usr/bin/env python3
"""
Telegram Note Taker 配置测试脚本
在运行 Bot 之前使用此脚本验证配置
"""

import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from config.config import Config
        print("✅ config.config 导入成功")
    except ImportError as e:
        print(f"❌ config.config 导入失败: {e}")
        return False
    
    try:
        from src.storage import MessageStorage
        print("✅ src.storage 导入成功")
    except ImportError as e:
        print(f"❌ src.storage 导入失败: {e}")
        return False
    
    try:
        import telegram
        print("✅ python-telegram-bot 导入成功")
    except ImportError as e:
        print(f"❌ python-telegram-bot 导入失败: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        return False
    
    return True

def test_config():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    try:
        from config.config import Config
        
        # 检查环境变量
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("⚠️  未设置 TELEGRAM_BOT_TOKEN 环境变量")
            print("💡 请创建 .env 文件并设置 Bot Token")
            return False
        else:
            print("✅ TELEGRAM_BOT_TOKEN 已设置")
            # 隐藏 token 的大部分内容
            masked_token = bot_token[:10] + "..." + bot_token[-4:]
            print(f"   Token: {masked_token}")
        
        # 测试配置验证
        if Config.validate():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_storage():
    """测试存储功能"""
    print("\n💾 测试存储功能...")
    
    try:
        from src.storage import MessageStorage
        
        storage = MessageStorage()
        print("✅ 存储模块初始化成功")
        
        # 测试目录创建
        from config.config import Config
        if os.path.exists(Config.DATA_DIR):
            print(f"✅ 数据目录存在: {Config.DATA_DIR}")
        else:
            print(f"❌ 数据目录不存在: {Config.DATA_DIR}")
            return False
        
        if os.path.exists(Config.LOG_DIR):
            print(f"✅ 日志目录存在: {Config.LOG_DIR}")
        else:
            print(f"❌ 日志目录不存在: {Config.LOG_DIR}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ 存储测试失败: {e}")
        return False

def test_env_file():
    """检查环境文件"""
    print("\n📄 检查环境文件...")
    
    env_file = os.path.join(project_root, '.env')
    env_example = os.path.join(project_root, '.env.example')
    
    if os.path.exists(env_file):
        print("✅ .env 文件存在")
    else:
        print("⚠️  .env 文件不存在")
        if os.path.exists(env_example):
            print("💡 请复制 .env.example 为 .env 并配置")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🤖 Telegram Note Taker 配置测试")
    print("=" * 50)
    
    all_passed = True
    
    # 运行所有测试
    tests = [
        test_env_file,
        test_imports,
        test_config,
        test_storage
    ]
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！可以启动 Bot 了")
        print("💡 运行命令: ./run.sh 或 cd src && python bot.py")
    else:
        print("❌ 部分测试失败，请检查上述错误并修复")
        print("💡 常见解决方案:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 创建配置: cp .env.example .env")
        print("   3. 设置 Token: 编辑 .env 文件")
    
    return all_passed

if __name__ == "__main__":
    # 加载 .env 文件
    try:
        from dotenv import load_dotenv
        env_file = os.path.join(project_root, '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
    except ImportError:
        # 如果没有 python-dotenv，手动加载环境变量
        env_file = os.path.join(project_root, '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    success = main()
    sys.exit(0 if success else 1)