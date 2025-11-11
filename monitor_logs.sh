#!/bin/bash
# 实时监控日志
tail -f logs/telegram_notetaker.log | grep -E "(开始生成|总结结果|生成.*总结|错误|失败|Exception)"
