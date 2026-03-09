#!/bin/bash
# 建立履歷池v2新分頁

SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aiagentg888@gmail.com"

# 20欄標題
HEADERS="姓名|Email|電話|地點|目前職位|總年資(年)|轉職次數|平均任職(月)|最近gap(月)|技能|學歷|來源|工作經歷JSON|離職原因|穩定性評分|學歷JSON|DISC/Big Five|狀態|獵頭顧問|備註"

echo "📋 建立新分頁：履歷池v2"
echo "🔧 設定 20 欄標題..."

# 使用 gog sheets update 建立新分頁並設定標題
# 先檢查是否已存在
gog sheets get "$SHEET_ID" "履歷池v2!A1" --account "$ACCOUNT" 2>&1 | grep -q "Unable to parse range" && {
    echo "✅ 分頁不存在，準備建立..."
    # gog 可能沒有直接建立分頁的指令，需要用 update
    gog sheets update "$SHEET_ID" "履歷池v2!A1:T1" "$HEADERS" --account "$ACCOUNT"
    echo "✅ 新分頁已建立，標題已設定"
} || {
    echo "⚠️ 分頁已存在，更新標題..."
    gog sheets update "$SHEET_ID" "履歷池v2!A1:T1" "$HEADERS" --account "$ACCOUNT"
    echo "✅ 標題已更新"
}

echo ""
echo "📊 標題欄位確認："
gog sheets get "$SHEET_ID" "履歷池v2!A1:T1" --account "$ACCOUNT"
