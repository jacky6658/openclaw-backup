#!/usr/bin/env python3
"""
將搜尋結果通知到 Telegram
"""

import json
import sys
import subprocess
from datetime import datetime

def format_results(data):
    """格式化結果為 Markdown"""
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))
    companies = data.get('companies', [])
    candidates = data.get('candidates', [])
    
    message = f"📊 **獵頭每日報告** ({timestamp})\n\n"
    
    # 公司
    if companies:
        message += f"## 🏢 新公司 ({len(companies)} 筆)\n\n"
        for idx, item in enumerate(companies[:5], 1):  # 只顯示前 5 筆
            message += f"{idx}. **{item['title']}**\n"
            message += f"   🔗 {item['url']}\n"
            message += f"   📝 {item['description'][:100]}...\n\n"
        
        if len(companies) > 5:
            message += f"_...還有 {len(companies) - 5} 筆_\n\n"
    else:
        message += "## 🏢 新公司\n無新資料\n\n"
    
    # 求職者
    if candidates:
        message += f"## 👤 求職者 ({len(candidates)} 筆)\n\n"
        for idx, item in enumerate(candidates[:5], 1):
            message += f"{idx}. **{item['title']}**\n"
            message += f"   🔗 {item['url']}\n"
            message += f"   📝 {item['description'][:100]}...\n\n"
        
        if len(candidates) > 5:
            message += f"_...還有 {len(candidates) - 5} 筆_\n\n"
    else:
        message += "## 👤 求職者\n無新資料\n\n"
    
    message += "---\n💡 完整資料請查看 `/Users/user/clawd/projects/headhunter-scraper/data/`"
    
    return message

def send_telegram(message):
    """使用 openclaw message tool 發送到 Telegram"""
    # 使用 openclaw message send
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'telegram',
        '--target', '8365775688',  # Jacky 的 Telegram ID
        '--message', message
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ 已發送到 Telegram")
            return True
        else:
            print(f"❌ 發送失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 發送錯誤: {e}")
        return False

def main():
    """主程式"""
    if len(sys.argv) < 2:
        print("Usage: python3 notify_telegram.py <result_json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        message = format_results(data)
        print("📝 訊息內容：")
        print(message)
        print("\n發送中...")
        
        send_telegram(message)
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
