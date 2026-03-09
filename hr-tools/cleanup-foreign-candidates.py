#!/usr/bin/env python3
"""
cleanup-foreign-candidates.py
==============================
安全清查資料庫中的外國候選人。

流程：
  1. 從 API 抓所有 Bot 自動匯入的候選人
  2. 用 GitHub API 確認 location（只抓還沒確認的）
  3. 輸出分析報表，等你確認後才刪除
  4. --delete 模式才真正刪除（預設只分析）

用法：
  python3 cleanup-foreign-candidates.py             # 分析模式（安全）
  python3 cleanup-foreign-candidates.py --delete    # 確認後刪除外國人
"""

import os, sys, requests, time, random, json, re

API_BASE = "https://backendstep1ne.zeabur.app/api"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DRY_RUN = "--delete" not in sys.argv

# ── 常數 ────────────────────────────────────────────
TAIWAN_SIGNALS = [
    'taiwan', '台灣', 'taipei', '台北', 'taichung', '台中',
    'kaohsiung', '高雄', 'tainan', '台南', 'hsinchu', '新竹',
    'new taipei', '新北', 'taoyuan', '桃園', 'keelung', '基隆',
]
FOREIGN_SIGNALS = [
    'india', 'bangalore', 'mumbai', 'delhi', 'hyderabad', 'pune', 'chennai',
    'indonesia', 'jakarta', 'bandung', 'philippines', 'manila', 'cebu',
    'vietnam', 'ho chi minh', 'hanoi', 'pakistan', 'karachi', 'lahore',
    'nigeria', 'kenya', 'ghana', 'brazil', 'são paulo', 'sao paulo',
    'egypt', 'cairo', 'bangladesh', 'dhaka',
    'united states', ' usa', 'san francisco', 'new york', 'seattle', 'austin',
    'england', 'london', 'germany', 'berlin', 'france', 'paris',
    'australia', 'sydney', 'melbourne', 'canada', 'toronto', 'vancouver',
]

def classify_location(location: str) -> str:
    if not location: return 'unknown'
    loc = location.lower().strip()
    if any(s in loc for s in TAIWAN_SIGNALS): return 'taiwan'
    if any(s in loc for s in FOREIGN_SIGNALS): return 'foreign'
    return 'unknown'

def is_chinese_name(name: str) -> bool:
    """是否含中文字（台灣人機率較高）"""
    return bool(re.search(r'[\u4e00-\u9fff]', name))

def get_github_location(login: str) -> str:
    """從 GitHub API 確認 location"""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    try:
        r = requests.get(f"https://api.github.com/users/{login}",
                         headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json().get('location') or ''
    except Exception:
        pass
    return ''

def extract_github_login(github_url: str) -> str:
    if not github_url: return ''
    m = re.search(r'github\.com/([^/?#]+)', github_url)
    return m.group(1) if m else ''

def score_foreign_risk(c: dict, github_location: str) -> tuple:
    """
    計算外國人機率（0-100），回傳 (score, 理由list)
    ≥70 → 高風險，建議刪除
    40-69 → 中等，人工確認
    <40 → 低風險，保留
    """
    score = 0
    reasons = []

    name = c.get('name', '')
    notes = (c.get('notes') or '').lower()
    skills = (c.get('skills') or '').lower()

    # 有 GitHub location 是最可靠的訊號
    gh_loc_class = classify_location(github_location)
    if gh_loc_class == 'foreign':
        score += 60
        reasons.append(f"GitHub location={github_location}")
    elif gh_loc_class == 'taiwan':
        score -= 30
        reasons.append(f"GitHub location=台灣 ✅")

    # 中文名字 → 不是外國人的強訊號
    if is_chinese_name(name):
        score -= 20
        reasons.append("中文名字（台灣/華人）")

    # notes 含外國地名
    for s in FOREIGN_SIGNALS:
        if s in notes:
            score += 20
            reasons.append(f"notes 含 {s}")
            break

    # 台灣訊號
    for s in TAIWAN_SIGNALS:
        if s in notes or s in skills:
            score -= 15
            reasons.append(f"台灣訊號: {s}")
            break

    # 名字是純英文（不含華人姓名）→ 稍微升高風險
    if not is_chinese_name(name) and not re.search(r'[\u3000-\u9fff]', name):
        # 英文名不直接判斷，僅加小分
        if '-' not in name and len(name.split()) == 1:  # 只有一個單詞（像 GitHub handle）
            score += 10
            reasons.append("疑似外國 GitHub handle")

    score = max(0, min(100, score))
    return score, reasons

# ── 主流程 ────────────────────────────────────────────
def main():
    print("=" * 60)
    print("🔍 外國候選人清查工具")
    print(f"   模式: {'⚠️  真實刪除（--delete）' if not DRY_RUN else '🔒 分析模式（不刪除）'}")
    print("=" * 60)

    # 1. 抓所有候選人
    print("\n📥 載入候選人...")
    all_candidates = []
    offset = 0
    limit = 100
    while True:
        r = requests.get(f"{API_BASE}/candidates", params={'limit': limit, 'offset': offset}, timeout=15)
        data = r.json().get('data', [])
        if not data: break
        all_candidates.extend(data)
        offset += limit
        if len(data) < limit: break

    print(f"   共 {len(all_candidates)} 筆")

    # 2. 只處理 Bot 自動匯入的
    bot_candidates = [c for c in all_candidates if
                      c.get('source') in ['GitHub', 'LinkedIn', '自動爬蟲'] or
                      c.get('githubUrl') or c.get('github_url')]
    print(f"   Bot 自動匯入: {len(bot_candidates)} 筆")

    # 3. 逐一分析
    results = {'taiwan': [], 'high_risk': [], 'medium_risk': [], 'safe': []}
    print(f"\n🔍 分析中（抓 GitHub location，每人間隔 1-2s）...")

    for i, c in enumerate(bot_candidates):
        cid = c.get('id')
        name = c.get('name', '')
        gh_url = c.get('githubUrl') or c.get('github_url') or ''
        login = extract_github_login(gh_url)

        # 抓 GitHub location
        gh_location = ''
        if login:
            gh_location = get_github_location(login)
            time.sleep(random.uniform(1.0, 2.0))  # 速率控制

        risk_score, reasons = score_foreign_risk(c, gh_location)

        entry = {
            'id': cid,
            'name': name,
            'github': gh_url,
            'github_location': gh_location,
            'risk_score': risk_score,
            'reasons': reasons,
        }

        if risk_score >= 70:
            results['high_risk'].append(entry)
            label = "🔴 高風險"
        elif risk_score >= 40:
            results['medium_risk'].append(entry)
            label = "🟡 中風險"
        elif classify_location(gh_location) == 'taiwan' or is_chinese_name(name):
            results['taiwan'].append(entry)
            label = "✅ 台灣"
        else:
            results['safe'].append(entry)
            label = "⚪ 保留"

        print(f"  [{i+1:3d}/{len(bot_candidates)}] {label} {name:20s} | {gh_location or '(無location)'} | {risk_score}分")

    # 4. 報表
    print("\n" + "=" * 60)
    print("📊 清查結果")
    print("=" * 60)
    print(f"  ✅ 台灣（安全）:   {len(results['taiwan'])} 人")
    print(f"  ⚪ 不確定（保留）: {len(results['safe'])} 人")
    print(f"  🟡 中風險（確認）: {len(results['medium_risk'])} 人")
    print(f"  🔴 高風險（刪除）: {len(results['high_risk'])} 人")

    if results['high_risk']:
        print(f"\n🔴 建議刪除名單（{len(results['high_risk'])} 人）：")
        for e in results['high_risk']:
            print(f"  ID:{e['id']:5d} | {e['name']:25s} | location: {e['github_location']:20s} | {', '.join(e['reasons'][:2])}")

    if results['medium_risk']:
        print(f"\n🟡 需人工確認（{len(results['medium_risk'])} 人）：")
        for e in results['medium_risk']:
            print(f"  ID:{e['id']:5d} | {e['name']:25s} | location: {e['github_location']:20s} | 分數:{e['risk_score']}")

    # 5. 儲存報告
    report_path = '/tmp/foreign-cleanup-report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📄 完整報告已存: {report_path}")

    # 6. 刪除（需要 --delete 且只刪高風險）
    if not DRY_RUN and results['high_risk']:
        print(f"\n⚠️  即將刪除 {len(results['high_risk'])} 筆高風險外國候選人...")
        deleted = 0
        for e in results['high_risk']:
            try:
                r = requests.delete(f"{API_BASE}/candidates/{e['id']}", timeout=10)
                if r.status_code in [200, 204]:
                    print(f"  ✅ 已刪除: {e['name']} (ID:{e['id']})")
                    deleted += 1
                else:
                    print(f"  ❌ 刪除失敗: {e['name']} ({r.status_code})")
                time.sleep(0.5)
            except Exception as ex:
                print(f"  ❌ 錯誤: {e['name']} - {ex}")
        print(f"\n  刪除完成: {deleted}/{len(results['high_risk'])} 筆")
    elif DRY_RUN and results['high_risk']:
        print(f"\n💡 確認無誤後，執行：")
        print(f"   python3 cleanup-foreign-candidates.py --delete")

if __name__ == '__main__':
    main()
