#!/usr/bin/env python3
"""
獵頭顧問總覽看板
用途：追蹤所有案子狀態，顯示 Pipeline 進度
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# 案子狀態定義
PIPELINE_STAGES = {
    'new': '🆕 新進件',
    'matching': '🔍 匹配中',
    'recommended': '📤 已推薦',
    'interview': '🎤 面試中',
    'offer': '💰 Offer中',
    'placed': '✅ 已報到',
    'closed': '❌ 已結案',
    'pool': '📋 履歷池'
}

# 資料檔案路徑
DATA_DIR = os.path.expanduser("~/clawd/data/headhunter")
JOBS_FILE = os.path.join(DATA_DIR, "jobs.json")
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")
DASHBOARD_FILE = os.path.join(DATA_DIR, "dashboard.json")

def ensure_data_dir():
    """確保資料目錄存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 初始化檔案
    if not os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, 'w') as f:
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

def add_job(client, title, requirements=None, salary=None, notes=None):
    """新增職缺"""
    ensure_data_dir()
    jobs = load_data(JOBS_FILE)
    
    job = {
        'id': f"JOB-{len(jobs)+1:03d}",
        'client': client,
        'title': title,
        'requirements': requirements or [],
        'salary': salary,
        'notes': notes,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'candidates': []
    }
    
    jobs.append(job)
    save_data(JOBS_FILE, jobs)
    
    print(f"✅ 新增職缺: {job['id']} - {client} / {title}")
    return job

def add_candidate(name, current_company=None, current_title=None, skills=None, 
                  experience=None, expected_salary=None, status='pool'):
    """新增候選人"""
    ensure_data_dir()
    candidates = load_data(CANDIDATES_FILE)
    
    candidate = {
        'id': f"CAN-{len(candidates)+1:03d}",
        'name': name,
        'current_company': current_company,
        'current_title': current_title,
        'skills': skills or [],
        'experience': experience,
        'expected_salary': expected_salary,
        'status': status,
        'jobs': [],  # 關聯的職缺
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    candidates.append(candidate)
    save_data(CANDIDATES_FILE, candidates)
    
    print(f"✅ 新增候選人: {candidate['id']} - {name}")
    return candidate

def update_candidate_status(candidate_id, new_status, job_id=None, notes=None):
    """更新候選人狀態"""
    ensure_data_dir()
    candidates = load_data(CANDIDATES_FILE)
    
    for c in candidates:
        if c['id'] == candidate_id:
            c['status'] = new_status
            c['updated_at'] = datetime.now().isoformat()
            
            if job_id:
                if job_id not in c['jobs']:
                    c['jobs'].append(job_id)
            
            if notes:
                if 'history' not in c:
                    c['history'] = []
                c['history'].append({
                    'status': new_status,
                    'job_id': job_id,
                    'notes': notes,
                    'timestamp': datetime.now().isoformat()
                })
            
            save_data(CANDIDATES_FILE, candidates)
            print(f"✅ 更新 {candidate_id} 狀態: {PIPELINE_STAGES.get(new_status, new_status)}")
            return c
    
    print(f"❌ 找不到候選人: {candidate_id}")
    return None

def generate_dashboard():
    """生成總覽看板"""
    ensure_data_dir()
    jobs = load_data(JOBS_FILE)
    candidates = load_data(CANDIDATES_FILE)
    
    # 統計各階段人數
    stage_counts = defaultdict(int)
    for c in candidates:
        stage_counts[c.get('status', 'pool')] += 1
    
    # 統計活躍職缺
    active_jobs = [j for j in jobs if j.get('status') == 'active']
    
    # 最近更新的候選人
    recent_candidates = sorted(candidates, 
                               key=lambda x: x.get('updated_at', ''), 
                               reverse=True)[:5]
    
    # 需要跟進的案子（推薦後超過 3 天未更新）
    three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
    need_followup = [c for c in candidates 
                    if c.get('status') == 'recommended' 
                    and c.get('updated_at', '') < three_days_ago]
    
    dashboard = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_jobs': len(jobs),
            'active_jobs': len(active_jobs),
            'total_candidates': len(candidates),
            'in_pool': stage_counts['pool'],
            'in_process': sum(stage_counts[s] for s in ['matching', 'recommended', 'interview', 'offer']),
            'placed': stage_counts['placed']
        },
        'pipeline': {
            stage: stage_counts[stage] for stage in PIPELINE_STAGES.keys()
        },
        'need_followup': len(need_followup),
        'recent_activity': [
            {
                'id': c['id'],
                'name': c['name'],
                'status': PIPELINE_STAGES.get(c.get('status', 'pool'), c.get('status')),
                'updated': c.get('updated_at', '')[:10]
            } for c in recent_candidates
        ]
    }
    
    save_data(DASHBOARD_FILE, dashboard)
    return dashboard

def print_dashboard():
    """印出看板"""
    dashboard = generate_dashboard()
    
    print("=" * 60)
    print("📊 獵頭顧問總覽看板")
    print(f"   更新時間: {dashboard['generated_at'][:19]}")
    print("=" * 60)
    
    s = dashboard['summary']
    print(f"\n📈 總覽")
    print(f"   職缺: {s['active_jobs']} 個活躍 / {s['total_jobs']} 個總計")
    print(f"   候選人: {s['total_candidates']} 人")
    print(f"   履歷池: {s['in_pool']} 人")
    print(f"   進行中: {s['in_process']} 人")
    print(f"   已成交: {s['placed']} 人")
    
    print(f"\n🔄 Pipeline 狀態")
    for stage, label in PIPELINE_STAGES.items():
        count = dashboard['pipeline'].get(stage, 0)
        if count > 0:
            bar = "█" * min(count, 20)
            print(f"   {label}: {bar} {count}")
    
    if dashboard['need_followup'] > 0:
        print(f"\n⚠️ 需要跟進: {dashboard['need_followup']} 人")
    
    if dashboard['recent_activity']:
        print(f"\n📋 最近動態")
        for r in dashboard['recent_activity']:
            print(f"   • {r['id']} {r['name']} - {r['status']} ({r['updated']})")
    
    print("\n" + "=" * 60)
    return dashboard

def format_for_telegram():
    """格式化為 Telegram 訊息"""
    dashboard = generate_dashboard()
    s = dashboard['summary']
    
    msg = "📊 **總覽看板**\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    msg += f"📋 職缺: {s['active_jobs']} 個活躍\n"
    msg += f"👥 候選人: {s['total_candidates']} 人\n"
    msg += f"📥 履歷池: {s['in_pool']} 人\n"
    msg += f"⏳ 進行中: {s['in_process']} 人\n"
    msg += f"✅ 已成交: {s['placed']} 人\n"
    
    if dashboard['need_followup'] > 0:
        msg += f"\n⚠️ **需跟進: {dashboard['need_followup']} 人**\n"
    
    msg += f"\n🔄 **Pipeline**\n"
    for stage, label in PIPELINE_STAGES.items():
        count = dashboard['pipeline'].get(stage, 0)
        if count > 0:
            msg += f"  {label}: {count}\n"
    
    msg += f"\n⏰ 更新: {dashboard['generated_at'][:16]}"
    
    return msg

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "add-job" and len(sys.argv) >= 4:
            add_job(sys.argv[2], sys.argv[3])
        elif cmd == "add-candidate" and len(sys.argv) >= 3:
            add_candidate(sys.argv[2])
        elif cmd == "update" and len(sys.argv) >= 4:
            update_candidate_status(sys.argv[2], sys.argv[3])
        elif cmd == "telegram":
            print(format_for_telegram())
        else:
            print_dashboard()
    else:
        print_dashboard()
