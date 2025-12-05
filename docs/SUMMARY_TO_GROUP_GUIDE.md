# 📨 每日总结发送到特定群组配置指南

## 功能说明

配置后，每日00:00自动生成的总结可以发送到指定的报告群组，而不是发送回原始群组。

## 使用场景

- 📊 **集中管理**: 将所有群组的总结集中发送到一个管理群组
- 🔒 **隐私保护**: 总结发送到私密群组，不在原群组显示
- 📈 **报告中心**: 创建一个专门的报告群组接收所有总结

## 配置步骤

### 1. 获取目标群组ID

**方法一：使用辅助脚本（推荐）**

```bash
python scripts/get_chat_id.py
```

然后：
1. 确保bot已添加到目标群组
2. 在目标群组中发送任意消息
3. 脚本会显示群组ID
4. 按 Ctrl+C 停止脚本

**方法二：查看日志文件**

1. 启动bot: `python src/bot.py`
2. 在目标群组中发送消息
3. 查看 `logs/telegram_notetaker.log` 中的 chat_id

### 2. 配置环境变量

编辑 `.env` 文件，设置以下配置：

```properties
# 启用发送总结到群组
SEND_SUMMARY_TO_CHAT=true

# 设置目标群组ID（替换为实际ID）
SUMMARY_REPORT_CHAT_ID=-1001234567890
```

**重要提示：**
- 群组ID通常是负数，例如 `-1001234567890`
- 私聊ID是正数，例如 `123456789`
- 如果不设置此项，总结会发送到原群组

### 3. 确保Bot权限

确保bot在目标群组中有以下权限：
- ✅ 发送消息
- ✅ 已被添加到群组

### 4. 重启Bot

```bash
# 停止现有bot
pkill -f "python.*bot.py"

# 启动bot
python src/bot.py
```

## 配置示例

### 示例1：发送到专门的报告群组

```properties
SEND_SUMMARY_TO_CHAT=true
SUMMARY_REPORT_CHAT_ID=-1001234567890
```

所有群组的总结都会发送到 `-1001234567890` 这个群组。

### 示例2：发送到私聊

```properties
SEND_SUMMARY_TO_CHAT=true
SUMMARY_REPORT_CHAT_ID=123456789
```

总结会发送到用户ID为 `123456789` 的私聊。

### 示例3：发送到原群组（默认）

```properties
SEND_SUMMARY_TO_CHAT=true
SUMMARY_REPORT_CHAT_ID=
```

或者不设置 `SUMMARY_REPORT_CHAT_ID`，总结会发送到原始群组。

### 示例4：不发送总结

```properties
SEND_SUMMARY_TO_CHAT=false
```

总结只保存为文件，不发送到任何群组。

## 总结格式

发送到群组的总结包含以下信息：

```
📊 [群组名称] - [日期] 每日总结

[AI生成的总结内容]

---
⏰ 生成时间: 2025-11-03 00:00:15
📨 消息数量: 156条
```

## 工作流程

1. **每日00:00**: 自动触发总结生成
2. **收集消息**: 获取前一天的所有消息
3. **AI分析**: 使用GPT-5生成总结
4. **保存文件**: 保存到 `data/summaries/`
5. **发送消息**: 如果启用，发送到配置的群组

## 注意事项

⚠️ **重要提示：**

1. **Bot权限**: 确保bot在目标群组中有发送消息权限
2. **群组ID格式**: 群组ID是负数，请包含负号
3. **多群组总结**: 所有被监控群组的总结都会发送到同一个目标群组
4. **隐私考虑**: 如果群组内容敏感，请谨慎设置目标群组
5. **消息限制**: Telegram单条消息最多4096字符，过长的总结会被截断

## 验证配置

运行以下命令验证配置：

```bash
python tests/test_config.py
```

检查输出中的：
- ✅ `SEND_SUMMARY_TO_CHAT: True`
- ✅ `SUMMARY_REPORT_CHAT_ID: -1001234567890`

## 故障排除

### 问题1：总结没有发送到群组

**检查清单：**
- [ ] `SEND_SUMMARY_TO_CHAT=true` 已设置
- [ ] Bot已添加到目标群组
- [ ] Bot在目标群组中有发送消息权限
- [ ] 群组ID格式正确（负数）
- [ ] Bot已重启

### 问题2：提示"Chat not found"

**原因：** Bot未加入目标群组或群组ID错误

**解决：**
1. 将bot添加到目标群组
2. 使用 `scripts/get_chat_id.py` 重新获取群组ID
3. 更新 `.env` 配置

### 问题3：总结发送失败

**查看日志：**
```bash
tail -f logs/telegram_notetaker.log
```

查找错误信息并根据提示处理。

## 测试配置

手动触发总结测试发送功能：

1. 在私聊中发送: `/menu`
2. 点击: `🔥 生成今日24小时总结`
3. 选择一个群组
4. 检查总结是否发送到配置的目标群组

## 高级配置

### 发送到多个群组

目前配置只支持单个目标群组。如果需要发送到多个群组，可以：

1. 创建一个转发bot
2. 在目标群组中设置自动转发
3. 或联系开发者添加多群组支持

### 自定义总结格式

编辑 `src/ai_summary.py` 中的 `format_summary_for_telegram` 方法来自定义总结格式。

## 相关文件

- 📝 配置文件: `.env`
- ⚙️ 配置类: `config/config.py`
- 🤖 调度器: `src/scheduler.py`
- 🔧 获取ID工具: `scripts/get_chat_id.py`