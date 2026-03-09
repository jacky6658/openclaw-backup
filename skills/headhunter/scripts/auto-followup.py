#!/usr/bin/env python3
"""
自動跟進排程系統
用途：設定候選人各階段的自動提醒
"""

import json
import os
from datetime import datetime, timedelta

# 跟進規則
FOLLOWUP_RULES = {
    'recommended': {
        'description': '推薦後跟進',
        'intervals': [3, 7, 14],  # 3天、7天、14天
        'message_template': '📋 {candidate} 推薦給 {client} 已 {days} 天，需要跟進客戶反饋'
    },
    'interview': {
        'description': '面試後跟進',
        'intervals': [1, 3],  # 1天、3天
        'message_template': '🎤 {candidate} 面試 {client} 已 {days} 天，需要確認結果'
    },
    'offer': {
        'description': 'Offer 跟進',
        'intervals': [1, 2, 3],  # 每天跟
        'message_template': '💰 {candidate} 收到 {client} Offer 已 {days} 天，確認接受狀況'
    },
    'placed': {
        'description': '報到後關懷',
        'intervals': [1, 7, 30, 90],  # Day1, Week1, Month1, 保證期
        'message_template': '✅ {candidate} 在 {client} 報到已 {days} 天，進行關懷追蹤'
    }
}

# 資料檔案路徑
DATA_DIR = os.path.expanduser("~/clawd/data/headhunter")
FOLLOWUPS_FILE = os.path.join(DATA_DIR, "followups.json")
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")

def ensure_data_dir():
    """確保資料目錄存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(FOLLOWUPS_FILE):
        with open(FOLLOWUPS_FILE, 'w') as f:
            json.dump([], f)

def load_data(filepath):
    """載入 JSON 資料"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(filepath, data):
    """儲存 JSON 資料"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def schedule_followup(candidate_id, candidate_name, client_name, status, 
                      start_date=None, notes=None):
    """
    為候選人排程跟進提醒
    
    Args:
        candidate_id: 候選人 ID
        candidate_name: 候選人姓名
        client_name: 客戶名稱
        status: 狀態 (recommended, interview, offer, placed)
        start_date: 起始日期 (預設今天)
        notes: 備註
    """
    ensure_data_dir()
    
    if status not in FOLLOWUP_RULES:
        print(f"❌ 不支援的狀態: {status}")
        return []
    
    rule = FOLLOWUP_RULES[status]
    start = datetime.fromisoformat(start_date) if start_date else datetime.now()
    followups = load_data(FOLLOWUPS_FILE)
    
    scheduled = []
    for days in rule['intervals']:
        due_date = start + timedelta(days=days)
        
        followup = {
            'id': f"FU-{len(followups)+len(scheduled)+1:04d}",
            'candidate_id': candidate_id,
            'candidate_name': candidate_name,
            'client_name': client_name,
            'status': status,
            'days': days,
            'due_date': due_date.isoformat()[:10],
            'message': rule['message_template'].format(
                candidate=candidate_name,
                client=client_name,
                days=days
            ),
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'notes': notes
        }
        
        scheduled.append(followup)
    
    followups.extend(scheduled)
    save_data(FOLLOWUPS_FILE, followups)
    
    print(f"✅ 已排程 {len(scheduled)} 個跟進提醒 ({rule['description']})")
    for f in scheduled:
        print(f"   • {f['due_date']}: {f['message']}")
    
    return scheduled

def get_due_today():
    """取得今天到期的跟進"""
    ensure_data_dir()
    followups = load_data(FOLLOWUPS_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    
    due = [f for f in followups 
           if f['due_date'] <= today and not f['completed']]
    
    return due

def get_upcoming(days=7):
    """取得未來 N 天的跟進"""
    ensure_data_dir()
    followups = load_data(FOLLOWUPS_FILE)
    
    today = datetime.now()
    end_date = (today + timedelta(days=days)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    upcoming = [f for f in followups 
                if today_str <= f['due_date'] <= end_date and not f['completed']]
    
    return sorted(upcoming, key=lambda x: x['due_date'])

def complete_followup(followup_id, notes=None):
    """標記跟進完成"""
    ensure_data_dir()
    followups = load_data(FOLLOWUPS_FILE)
    
    for f in followups:
        if f['id'] == followup_id:
            f['completed'] = True
            f['completed_at'] = datetime.now().isoformat()
            if notes:
                f['completion_notes'] = notes
            
            save_data(FOLLOWUPS_FILE, followups)
            print(f"✅ 已完成: {f['message']}")
            return f
    
    print(f"❌ 找不到跟進: {followup_id}")
    return None

def format_daily_reminder():
    """格式化每日提醒訊息"""
    due_today = get_due_today()
    upcoming = get_upcoming(7)
    
    msg = "🔔 **每日跟進提醒**\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    
    if due_today:
        msg += f"\n⚠️ **今天需跟進 ({len(due_today)} 件)**\n"
        for f in due_today:
            msg += f"• {f['message']}\n"
    else:
        msg += f"\n✅ 今天沒有待跟進項目\n"
    
    future = [u for u in upcoming if u['due_date'] > datetime.now().strftime('%Y-%m-%d')]
    if future:
        msg += f"\n📅 **未來 7 天 ({len(future)} 件)**\n"
        for f in future[:5]:  # 最多顯示 5 件
            msg += f"• {f['due_date']}: {f['candidate_name']} ({f['status']})\n"
        if len(future) > 5:
            msg += f"  ...還有 {len(future)-5} 件\n"
    
    msg += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return msg

def print_status():
    """印出跟進狀態"""
    due_today = get_due_today()
    upcoming = get_upcoming(7)
    
    print("=" * 60)
    print("🔔 跟進排程狀態")
    print("=" * 60)
    
    if due_today:
        print(f"\n⚠️ 今天需跟進: {len(due_today)} 件")
        for f in due_today:
            print(f"   [{f['id']}] {f['message']}")
    else:
        print(f"\n✅ 今天沒有待跟進項目")
    
    if upcoming:
        print(f"\n📅 未來 7 天: {len(upcoming)} 件")
        for f in upcoming[:10]:
            status_icon = "⬜" if not f['completed'] else "✅"
            print(f"   {status_icon} {f['due_date']}: {f['candidate_name']} - {f['status']}")
    
    print("\n" + "=" * 60)

def demo():
    """示範用法"""
    print("🎯 自動跟進排程系統示範")
    print("-" * 40)
    
    # 範例：推薦候選人後排程
    schedule_followup(
        candidate_id="CAN-001",
        candidate_name="王小明",
        client_name="ABC科技",
        status="recommended"
    )
    
    print()
    
    # 範例：報到後排程關懷
    schedule_followup(
        candidate_id="CAN-002", 
        candidate_name="李大華",
        client_name="XYZ公司",
        status="placed"
    )
    
    print()
    print_status()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "demo":
            demo()
        elif cmd == "status":
            print_status()
        elif cmd == "today":
            due = get_due_today()
            for f in due:
                print(f"[{f['id']}] {f['message']}")
        elif cmd == "telegram":
            print(format_daily_reminder())
        elif cmd == "schedule" and len(sys.argv) >= 6:
            schedule_followup(
                candidate_id=sys.argv[2],
                candidate_name=sys.argv[3],
                client_name=sys.argv[4],
                status=sys.argv[5]
            )
        elif cmd == "complete" and len(sys.argv) >= 3:
            complete_followup(sys.argv[2])
        else:
            print("用法:")
            print("  python auto-followup.py status")
            print("  python auto-followup.py today")
            print("  python auto-followup.py telegram")
            print("  python auto-followup.py schedule <candidate_id> <name> <client> <status>")
            print("  python auto-followup.py complete <followup_id>")
            print("  python auto-followup.py demo")
    else:
        print_status()
