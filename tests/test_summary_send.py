#!/usr/bin/env python3
"""
测试总结发送功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import Config

def test_config():
    """测试配置"""
    config = Config()
    
    print("📋 总结发送配置测试")
    print("=" * 50)
    
    print(f"✅ 启用AI总结: {config.ENABLE_AI_SUMMARY}")
    print(f"✅ 发送总结到聊天: {config.SEND_SUMMARY_TO_CHAT}")
    print(f"🎯 总结发送目标: {config.SUMMARY_SEND_TARGET}")
    print(f"👥 管理员ID列表: {config.get_admin_ids()}")
    print()
    
    if config.SUMMARY_SEND_TARGET == 'admin':
        print("📱 总结将发送到：管理员私聊")
        admin_ids = config.get_admin_ids()
        if admin_ids:
            print(f"   目标管理员: {len(admin_ids)} 个")
            for admin_id in admin_ids:
                print(f"   - {admin_id}")
        else:
            print("⚠️  警告：未配置管理员ID！")
    elif config.SUMMARY_SEND_TARGET == 'group':
        print("📱 总结将发送到：原群组")
    else:
        print(f"⚠️  未知的发送目标: {config.SUMMARY_SEND_TARGET}")
    
    print()
    print("=" * 50)
    print("💡 提示：")
    print("   - 在 .env 中设置 SUMMARY_SEND_TARGET=admin 发送到管理员")
    print("   - 在 .env 中设置 SUMMARY_SEND_TARGET=group 发送到群组")
    print("   - 确保 SEND_SUMMARY_TO_CHAT=true 以启用自动发送")

if __name__ == "__main__":
    test_config()
