#!/bin/bash
# 清理 /tmp/talent-* 日志文件，只保留最新 10 笔
# 用途：定期清理爬虫日志，避免占用空间

LOG_PATTERN="/tmp/talent-*"
KEEP_COUNT=30

# 计算总文件数
total=$(ls $LOG_PATTERN 2>/dev/null | wc -l | tr -d ' ')

if [ "$total" -eq 0 ]; then
    echo "📋 无需清理（无日志文件）"
    exit 0
fi

if [ "$total" -le "$KEEP_COUNT" ]; then
    echo "📋 无需清理（总数 $total <= 保留数 $KEEP_COUNT）"
    exit 0
fi

# 计算需要删除的数量
delete=$((total - KEEP_COUNT))

echo "🧹 开始清理 talent 日志..."
echo "  • 总文件: $total"
echo "  • 保留: $KEEP_COUNT"
echo "  • 删除: $delete"

# 删除旧文件（保留最新 10 个）
deleted=$(ls -t $LOG_PATTERN 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | xargs rm -f 2>&1)

# 确认结果
remaining=$(ls $LOG_PATTERN 2>/dev/null | wc -l | tr -d ' ')
echo "✅ 清理完成！剩余 $remaining 个文件"

# 释放的空间（可选）
if command -v du &> /dev/null; then
    space=$(du -sh /tmp/talent* 2>/dev/null | tail -1 | awk '{print $1}')
    echo "💾 当前占用: $space"
fi
