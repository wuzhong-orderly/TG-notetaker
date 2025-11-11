#!/usr/bin/env python3
"""
测试总结发送配置
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config

def test_summary_config():
    """测试总结发送配置"""
    print("🔧 测试总结发送配置...")
    print("="*60)
    
    config = Config()
    
    # 基本配置
    print("\n📋 基本配置：")
    print(f"   ✓ AI总结功能: {'启用' if config.ENABLE_AI_SUMMARY else '未启用'}")
    print(f"   ✓ AI提供商: {config.AI_PROVIDER}")
    print(f"   ✓ 自动总结时间: {config.AUTO_SUMMARY_TIME}")
    
    # 发送配置
    print("\n📨 发送配置：")
    print(f"   ✓ 发送总结到群组: {'启用' if config.SEND_SUMMARY_TO_CHAT else '未启用'}")
    
    report_chat_id = config.get_summary_report_chat_id()
    if report_chat_id != 0:
        print(f"   ✓ 目标群组ID: {report_chat_id}")
        print(f"   ✓ 发送模式: 集中发送到指定群组")
    else:
        print(f"   ✓ 目标群组ID: 未设置")
        print(f"   ✓ 发送模式: 发送到原始群组")
    
    # 管理员配置
    print("\n👥 管理员配置：")
    admin_ids = config.get_admin_ids()
    if admin_ids:
        print(f"   ✓ 管理员ID: {admin_ids}")
    else:
        print(f"   ⚠️  未配置管理员")
    
    # 存储配置
    print("\n💾 存储配置：")
    print(f"   ✓ 数据目录: {config.DATA_DIR}")
    print(f"   ✓ 总结目录: {config.SUMMARY_DIR}")
    print(f"   ✓ 日志目录: {config.LOG_DIR}")
    
    print("\n" + "="*60)
    
    # 验证配置
    if not config.ENABLE_AI_SUMMARY:
        print("⚠️  警告: AI总结功能未启用")
        return False
    
    if config.SEND_SUMMARY_TO_CHAT and report_chat_id == 0:
        print("💡 提示: 启用了发送功能但未设置目标群组，总结将发送到原群组")
    
    if config.SEND_SUMMARY_TO_CHAT and report_chat_id != 0:
        print(f"✅ 配置完成: 总结将发送到群组 {report_chat_id}")
    
    print("\n📖 使用说明:")
    print("   1. 使用 get_chat_id.py 获取群组ID")
    print("   2. 在 .env 中设置 SUMMARY_REPORT_CHAT_ID")
    print("   3. 确保bot已加入目标群组并有发送权限")
    print("   4. 重启bot使配置生效")
    
    return True

if __name__ == "__main__":
    try:
        test_summary_config()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
