#!/bin/bash
# 自動找人選 - 直接版本
# 透過 Telegram 觸發，讓 OpenClaw agent 直接執行

echo "📋 讀取職缺清單..."

# 讀取招募中的職缺
gog sheets read 1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE --range "A2:J" --format json > /tmp/jd-list.json

# 過濾出招募中的職缺
JOB_COUNT=$(jq '[.[] | select(.[7] == "招募中")] | length' /tmp/jd-list.json)

echo "✅ 找到 $JOB_COUNT 個招募中職缺"

# 發送 Telegram 通知，請 YuQi 開始執行
message telegram send \
  --channel telegram \
  --target "-1003231629634" \
  --thread-id 304 \
  --message "🤖 自動找人選系統啟動

📊 共 $JOB_COUNT 個招募中職缺
⏳ 預計執行時間：30-40 分鐘

@YuQi 開始執行多管道搜尋（LinkedIn + GitHub + CakeResume）..."

echo "✅ 通知已發送到 Topic 304"
echo "💡 接下來由 OpenClaw agent 直接執行搜尋"
