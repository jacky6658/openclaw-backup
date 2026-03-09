#!/usr/bin/env python3
"""
OAuth 狀態檢查與提醒
每週六 9:00 執行，檢查是否有帳號即將過期（< 3 天）
"""
import subprocess
import json
from datetime import datetime, timezone, timedelta
import sys

LOG_FILE = "/Users/user/clawd/hr-tools/data/oauth-check.log"
ALERT_DAYS = 3

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def get_oauth_status():
    """獲取所有 OAuth 帳號狀態"""
    result = subprocess.run(
        ["gog", "auth", "list"],
        capture_output=True,
        text=True
    )
    
    accounts = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 4 and parts[0] != 'email':
            accounts.append({
                'email': parts[0],
                'client': parts[1],
                'scopes': parts[2],
                'expires': parts[3]
            })
    
    return accounts

def calculate_days_left(auth_time_str):
    """計算剩餘天數（OAuth token 有效期 = 授權時間 + 8 天）"""
    try:
        # 解析 ISO 時間格式：2026-02-22T12:45:53Z
        auth_time = datetime.strptime(auth_time_str, "%Y-%m-%dT%H:%M:%SZ")
        auth_time = auth_time.replace(tzinfo=timezone.utc)
        
        # OAuth token 有效期：授權時間 + 8 天
        expires = auth_time + timedelta(days=8)
        
        now = datetime.now(timezone.utc)
        delta = expires - now
        return int(delta.total_seconds() / 86400)
    except Exception as e:
        log(f"  ⚠️ 解析時間失敗: {auth_time_str}, 錯誤: {e}")
        return 999  # 返回大數字，避免誤報

def send_telegram_alert(message):
    """發送 Telegram 通知"""
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", "-1003050496594",
        "--thread-id", "4",
        "--message", message
    ], capture_output=True)

def main():
    log("開始檢查 OAuth 狀態...")
    
    accounts = get_oauth_status()
    expired = []
    warning = []
    
    for acc in accounts:
        days_left = calculate_days_left(acc['expires'])
        log(f"  帳號: {acc['email']}, 剩餘天數: {days_left}")
        
        if days_left < 0:
            expired.append(f"{acc['email']} (已過期 {abs(days_left)} 天)")
        elif days_left <= ALERT_DAYS:
            warning.append(f"{acc['email']} (剩餘 {days_left} 天)")
    
    # 發送通知
    if expired or warning:
        message = "⚠️ OAuth 續期提醒\n\n"
        
        if expired:
            message += "❌ 已過期帳號：\n"
            for acc in expired:
                message += f"  • {acc}\n"
            message += "\n"
        
        if warning:
            message += f"⏰ 即將過期帳號（< {ALERT_DAYS} 天）：\n"
            for acc in warning:
                message += f"  • {acc}\n"
            message += "\n"
        
        message += "請執行：yuqi 處理 OAuth 續期"
        
        send_telegram_alert(message)
        log("✅ 已發送提醒通知")
    else:
        log("✅ 所有帳號正常，無需提醒")
    
    log("檢查完成")
    log("---")

if __name__ == "__main__":
    main()
