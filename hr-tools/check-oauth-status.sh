#!/bin/bash
# OAuth 狀態檢查與提醒
# 每週六 9:00 執行，檢查是否有帳號即將過期（< 3 天）

set -e

LOG_FILE="/Users/user/clawd/hr-tools/data/oauth-check.log"
ALERT_DAYS=3

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始檢查 OAuth 狀態..." >> "$LOG_FILE"

# 獲取所有帳號狀態
oauth_list=$(gog auth list 2>&1)

# 解析每個帳號
expired_accounts=()
warning_accounts=()

while IFS=$'\t' read -r email client scopes expires auth_type; do
    # 跳過標題行
    if [[ "$email" == "email" ]]; then
        continue
    fi
    
    # 計算剩餘天數
    if [[ -n "$expires" ]]; then
        # 移除時區標記 Z，改用 UTC 時間計算
        expire_date="${expires%Z}"
        expire_timestamp=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$expire_date" "+%s" 2>/dev/null || echo "0")
        current_timestamp=$(date -u "+%s")
        days_left=$(( ($expire_timestamp - $current_timestamp) / 86400 ))
        
        echo "  帳號: $email, 剩餘天數: $days_left" >> "$LOG_FILE"
        
        # 已過期
        if [ $days_left -lt 0 ]; then
            expired_accounts+=("$email (已過期 $((0 - days_left)) 天)")
        # 即將過期（< 3 天）
        elif [ $days_left -le $ALERT_DAYS ]; then
            warning_accounts+=("$email (剩餘 $days_left 天)")
        fi
    fi
done <<< "$oauth_list"

# 發送 Telegram 通知
if [ ${#expired_accounts[@]} -gt 0 ] || [ ${#warning_accounts[@]} -gt 0 ]; then
    message="⚠️ OAuth 續期提醒\n\n"
    
    if [ ${#expired_accounts[@]} -gt 0 ]; then
        message+="❌ 已過期帳號：\n"
        for acc in "${expired_accounts[@]}"; do
            message+="  • $acc\n"
        done
        message+="\n"
    fi
    
    if [ ${#warning_accounts[@]} -gt 0 ]; then
        message+="⏰ 即將過期帳號（< $ALERT_DAYS 天）：\n"
        for acc in "${warning_accounts[@]}"; do
            message+="  • $acc\n"
        done
        message+="\n"
    fi
    
    message+="請執行：yuqi 處理 OAuth 續期"
    
    # 發送到 Telegram（For myself 群組 - 臨時筆記 Thread）
    openclaw message send \
        --channel telegram \
        --target -1003050496594 \
        --thread-id 4 \
        --message "$message" 2>&1 >> "$LOG_FILE"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 已發送提醒通知" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 所有帳號正常，無需提醒" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 檢查完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
