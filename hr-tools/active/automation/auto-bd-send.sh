#!/bin/bash

# 自動檢查並發送 BD 郵件 - Final Version
# 修復狀態更新問題，即使更新失敗也繼續

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT="aiagentg888@gmail.com"
EMAIL_FROM="aijessie88@step1ne.com"
ATTACHMENT="/Users/user/clawd/projects/step1nehrai/hr-tools/docs/Step1ne公司簡介.pdf"
LOG_FILE="$SCRIPT_DIR/auto-bd-send.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 開始自動 BD 發信檢查 =========="

# 檢查附件
if [[ ! -f "$ATTACHMENT" ]]; then
    log "❌ 找不到附件：$ATTACHMENT"
    exit 1
fi

# 讀取資料
log "📊 讀取 BD 客戶開發表..."
SHEET_JSON=$(gog sheets get "$SHEET_ID" "工作表1!A2:L100" --json --account "$ACCOUNT" 2>&1)

if [[ $? -ne 0 ]]; then
    log "❌ 讀取失敗"
    exit 1
fi

SEND_COUNT=0
FAIL_COUNT=0
TODAY=$(date '+%Y-%m-%d')

# 逐行處理
echo "$SHEET_JSON" | jq -c '.values[] | select(length >= 12) | {
  row_index: (. | keys | max),
  company: .[0],
  email: .[2],
  mail_status: .[11]
}' | while read -r row; do
    
    company=$(echo "$row" | jq -r '.company')
    email=$(echo "$row" | jq -r '.email')
    mail_status=$(echo "$row" | jq -r '.mail_status')
    
    # 檢查是否為「待寄信」
    if [[ "$mail_status" != "待寄信" ]]; then
        continue
    fi
    
    log "📧 發現待寄信公司：$company"
    log "   Email: $email"
    
    # 檢查 Email
    if [[ "$email" == "待查" ]] || [[ -z "$email" ]] || [[ "$email" == "null" ]]; then
        log "   ⚠️ Email 無效，跳過"
        continue
    fi
    
    # 生成郵件內容
    SUBJECT="【Step1ne】獵頭合作邀請 - 協助您快速找到優秀人才"
    
    BODY="您好：

我是 Step1ne 的招募顧問 \"Jacky\"，專注於協助企業快速找到優秀的科技人才。

我們想與 ${company} 分享我們的服務如何協助企業提升招募效率：

✅ 我們的優勢：
• AI 驅動的履歷匹配系統 - 精準度達 90% 以上
• 豐富的人才庫 - 涵蓋 AI、後端、前端、數據分析等領域
• 快速交付 - 平均 7 天內推薦合適人選
• 保證期服務 - 90 天內免費替換

📊 近期成功案例：
• 協助某金融科技公司 2 週內找到 3 位資深後端工程師
• 為某 AI 新創公司建立完整的技術團隊（5人）
• 幫助多家企業降低 40% 的招募成本

🎯 如果 ${company} 有以下需求，歡迎與我們聯繫：
• 急需特定技能的人才（AI/ML/後端/前端/數據）
• 想建立長期的招募合作關係
• 希望了解市場薪資與人才趨勢

期待與您進一步交流，協助 ${company} 找到最合適的人才！

---
Step1ne 招募顧問團隊
📧 Email: aijessie88@step1ne.com
🌐 Website: step1ne.com"

    # 發送郵件
    log "   ⏳ 正在發送..."
    
    if echo "$BODY" | gog gmail send \
        --account "$EMAIL_FROM" \
        --to "$email" \
        --subject "$SUBJECT" \
        --body-file - \
        --attach "$ATTACHMENT" >/dev/null 2>&1; then
        
        log "   ✅ 發送成功"
        SEND_COUNT=$((SEND_COUNT + 1))
        
        # 更新狀態（簡化版：直接搜尋並更新，不依賴行號）
        # 先獲取所有 A 欄資料找行號
        ALL_COMPANIES=$(gog sheets get "$SHEET_ID" "工作表1!A:A" --plain --account "$ACCOUNT" 2>/dev/null)
        ROW_NUM=$(echo "$ALL_COMPANIES" | grep -Fn "$company" | head -1 | cut -d':' -f1)
        
        if [[ -n "$ROW_NUM" ]] && [[ "$ROW_NUM" -gt 1 ]]; then
            log "   📝 更新狀態（Row $ROW_NUM）"
            # 使用正確的 JSON 格式
            echo "[\"已寄出 ($TODAY)\"]" | gog sheets update "$SHEET_ID" "工作表1!L$ROW_NUM" \
                --values-json "$(cat -)" \
                --input USER_ENTERED \
                --account "$ACCOUNT" >/dev/null 2>&1 || log "   ⚠️ 更新狀態失敗（但郵件已發送）"
        fi
    else
        log "   ❌ 發送失敗"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    # 延遲 3 秒
    sleep 3
done

log "========== BD 發信完成 =========="
log "✅ 成功發送：$SEND_COUNT 封"
log "❌ 失敗：$FAIL_COUNT 封"

if [[ $SEND_COUNT -gt 0 ]]; then
    echo "📧 BD 自動發信完成：成功 $SEND_COUNT 封，失敗 $FAIL_COUNT 封"
fi

exit 0
