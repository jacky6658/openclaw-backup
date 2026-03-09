#!/bin/bash
# AI 配對 Telegram 整合腳本
# 用途：從 Telegram 觸發 AI 配對，結果發回群組

set -e

# 配置
HR_GROUP_ID="-1003231629634"
TOPIC_304="304"  # 履歷池
JD_SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_POOL_SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

# 參數
JOB_TITLE="$1"

if [ -z "$JOB_TITLE" ]; then
    echo "使用方式: $0 <職位名稱>"
    echo "範例: $0 'AI工程師'"
    exit 1
fi

# 步驟 1：從職缺管理表讀取 JD
echo "📋 讀取職缺：$JOB_TITLE"

JD_DATA=$(python3 << EOF
import sys
sys.path.insert(0, '/Users/user/clawd/hr-tools')

# 這裡應該從 Google Sheets 讀取 JD
# 簡化版：使用測試資料
jd = {
    "title": "$JOB_TITLE",
    "required_skills": ["Python", "Machine Learning", "AI"],
    "preferred_skills": ["TensorFlow", "PyTorch"],
    "min_experience": 3,
    "industry": "科技"
}

print(str(jd))
EOF
)

echo "✅ JD 已讀取"

# 步驟 2：從履歷池讀取候選人
echo "👥 讀取履歷池候選人..."

# 步驟 3：執行 AI 配對
echo "🤖 開始 AI 配對..."

RESULT=$(python3 /Users/user/clawd/hr-tools/ai-matching-batch.py "$JOB_TITLE")

# 步驟 4：產生 Telegram 訊息
MESSAGE="✅ AI 配對完成！

📊 職缺：$JOB_TITLE

配對結果：
$RESULT

完整報告：https://docs.google.com/spreadsheets/d/$RESUME_POOL_SHEET_ID"

# 步驟 5：發送到 Telegram
echo "📤 發送結果到 Telegram..."

# 使用 openclaw message tool
# message --action send --channel telegram --target "$HR_GROUP_ID" --thread "$TOPIC_304" --message "$MESSAGE"

# 或直接輸出（供測試）
echo "======================================"
echo "$MESSAGE"
echo "======================================"

echo ""
echo "✅ 完成！"
echo "提示：實際發送到 Telegram 需啟用上方 message 指令"
