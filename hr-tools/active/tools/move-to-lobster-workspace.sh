#!/bin/bash
# 自動移動獵頭系統相關檔案到 openclaw 龍蝦工作室

set -e

ACCOUNT="aiagentg888@gmail.com"

# 資料夾 ID
LOBSTER_WORKSPACE="1DwZ9LRF5D4rSvxDjNKyUVAORvhn6mhDj"  # openclaw 龍蝦工作室
HEADHUNTER_SYSTEM="12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS"  # 獵頭系統
PIPELINE_JACKY="1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M"  # Pipeline追蹤 - Jacky
PIPELINE_PHOEBE="1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk"  # Pipeline追蹤 - Phobe

echo "📂 開始自動移動檔案到 openclaw 龍蝦工作室..."
echo ""

# Step 1: 移動「獵頭系統」資料夾到「openclaw 龍蝦工作室」
echo "1️⃣ 移動「獵頭系統」資料夾 → openclaw 龍蝦工作室"
gog drive move "$HEADHUNTER_SYSTEM" \
  --parent "$LOBSTER_WORKSPACE" \
  --account "$ACCOUNT" \
  --no-input

if [ $? -eq 0 ]; then
    echo "   ✅ 成功"
else
    echo "   ❌ 失敗"
    exit 1
fi

echo ""
sleep 1

# Step 2: 移動 Pipeline 追蹤表到「獵頭系統」資料夾
echo "2️⃣ 移動「Pipeline追蹤 - Jacky」→ 獵頭系統"
gog drive move "$PIPELINE_JACKY" \
  --parent "$HEADHUNTER_SYSTEM" \
  --account "$ACCOUNT" \
  --no-input

if [ $? -eq 0 ]; then
    echo "   ✅ 成功"
else
    echo "   ❌ 失敗"
fi

echo ""
sleep 1

echo "3️⃣ 移動「Pipeline追蹤 - Phoebe」→ 獵頭系統"
gog drive move "$PIPELINE_PHOEBE" \
  --parent "$HEADHUNTER_SYSTEM" \
  --account "$ACCOUNT" \
  --no-input

if [ $? -eq 0 ]; then
    echo "   ✅ 成功"
else
    echo "   ❌ 失敗"
fi

echo ""
echo "✅ 全部完成！"
echo ""
echo "📍 新資料夾結構："
echo ""
echo "openclaw 龍蝦工作室/"
echo "└── 獵頭系統/"
echo "    ├── 履歷池索引"
echo "    ├── step1ne 職缺管理"
echo "    ├── BD客戶開發表"
echo "    ├── Pipeline追蹤 - Jacky"
echo "    └── Pipeline追蹤 - Phoebe"
echo ""
echo "🔗 連結："
echo "openclaw 龍蝦工作室: https://drive.google.com/drive/folders/$LOBSTER_WORKSPACE"
echo "獵頭系統: https://drive.google.com/drive/folders/$HEADHUNTER_SYSTEM"
