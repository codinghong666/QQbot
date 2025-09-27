#!/bin/bash
# QQ Bot Scheduler启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置日志文件
LOG_FILE="scheduler.log"

echo "Starting QQ Bot Scheduler..."
echo "Log file: $LOG_FILE"
echo "Press Ctrl+C to stop"

# 启动调度器
python3 simple_scheduler.py 2>&1 | tee -a "$LOG_FILE"
