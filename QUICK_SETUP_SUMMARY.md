# 📨 快速设置：每日总结发送到特定群组

## 3步快速配置

### 步骤1：获取群组ID

运行获取群组ID的工具：

```bash
python get_chat_id.py
```

然后在目标群组中发送任意消息，工具会显示群组ID。

### 步骤2：配置.env文件

编辑 `.env` 文件，找到并修改以下配置：

```properties
# 启用发送功能
SEND_SUMMARY_TO_CHAT=true

# 设置目标群组ID（替换为步骤1获取的ID）
SUMMARY_REPORT_CHAT_ID=-1001234567890
```

### 步骤3：重启Bot

```bash
# 停止bot
pkill -f "python.*bot.py"

# 启动bot
python src/bot.py
```

## 验证配置

```bash
python test_summary_config.py
```

应该看到：
```
✅ 配置完成: 总结将发送到群组 -1001234567890
```

## 完成！

现在每天00:00，所有群组的总结都会自动发送到你设置的群组。

---

**详细文档**: 查看 `SUMMARY_TO_GROUP_GUIDE.md`
