#!/bin/bash
# 每週學習報告（Cron Job 用）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TELEGRAM_GROUP="-1003231629634"
TELEGRAM_TOPIC="326"  # 總覽看板

echo "📊 生成每週學習報告..."

# 執行 Python 生成報告
REPORT=$(python3 "$SCRIPT_DIR/learning-engine.py" 2>/dev/null | tail -20)

# 如果報告為空，使用預設訊息
if [ -z "$REPORT" ]; then
  REPORT="📊 每週學習報告

本週尚無足夠決策資料（需至少 5 個決策）

請繼續使用系統，累積更多決策以啟用主動學習功能。

💡 如何累積決策：
- 當收到候選人推薦時，回覆「聯繫 [姓名]」或「略過 [姓名]」
- 系統會自動記錄並學習你的偏好"
fi

# 發送到 Telegram
openclaw message send \
  --channel telegram \
  --target "$TELEGRAM_GROUP" \
  --thread-id "$TELEGRAM_TOPIC" \
  --message "$REPORT"

echo "✅ 報告已發送到 Topic $TELEGRAM_TOPIC"
