#!/usr/bin/env python3
"""
Mike 專用 - LinkedIn 搜尋台灣 BIM 工程師
使用 Brave Search API（正確策略：英文關鍵字 + 台灣城市）
"""

import os
import sys
import json
import requests
from datetime import datetime
from urllib.parse import unquote

# ==================== 配置 ====================

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', 'BSAGYPKNGT7tKInGsjI9EQxO9AkHBls')
STEP1NE_API = "https://backendstep1ne.zeabur.app/api"

# ==================== 搜尋策略（修正版）====================
# 關鍵：英文職位 + 台灣城市名 → 找到台灣本地 LinkedIn 個人頁

SEARCH_QUERIES = {
    "BIM工程師": [
        "BIM Engineer Taiwan Taipei Revit Navisworks site:linkedin.com/in",
        "BIM Coordinator Taiwan New Taipei AutoCAD site:linkedin.com/in",
        "BIM Manager Taiwan Taichung Revit site:linkedin.com/in",
        "BIM Specialist 台灣 Revit site:linkedin.com/in",
    ],
    "文件管理師": [
        "Document Controller Taiwan Taipei site:linkedin.com/in",
        "Document Management Engineer Taiwan site:linkedin.com/in",
        "文管 台灣 工程師 site:linkedin.com/in",
    ]
}


# ==================== 函數 ====================

def brave_search(query, count=10):
    """使用 Brave Search API 搜尋"""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "count": count,
        "country": "TW"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ❌ 搜尋失敗：{e}")
        return None


def clean_url(url):
    """清理 LinkedIn URL（解碼中文字元）"""
    # tw.linkedin.com 統一轉為 linkedin.com 格式
    url = url.replace("tw.linkedin.com", "www.linkedin.com")
    # 解碼 URL 編碼（%E9%99%B3 → 正常文字）
    try:
        decoded = unquote(url)
        # 如果解碼後有中文，保持原本 URL（避免無效連結）
        if any('\u4e00' <= c <= '\u9fff' for c in decoded):
            return url
        return url
    except:
        return url


def extract_skills_from_text(text):
    """從文字中提取技能關鍵字"""
    skill_map = {
        "BIM": "BIM", "Revit": "Revit", "AutoCAD": "AutoCAD",
        "Navisworks": "Navisworks", "Tekla": "Tekla", "Civil 3D": "Civil 3D",
        "MEP": "MEP", "4D": "4D BIM", "5D": "5D BIM",
        "ISO 19650": "ISO 19650", "BEP": "BEP", "BIM 360": "BIM 360",
        "Dynamo": "Dynamo", "Lumion": "Lumion", "Rhino": "Rhino",
        "SketchUp": "SketchUp", "Blender": "Blender",
        "Python": "Python", "C#": "C#",
        "Project Management": "專案管理", "Construction": "營建管理",
        "Structural": "結構設計", "Architecture": "建築設計",
    }
    found = []
    text_lower = text.lower()
    for keyword, skill_name in skill_map.items():
        if keyword.lower() in text_lower and skill_name not in found:
            found.append(skill_name)
    return found


def parse_result(result):
    """解析單筆搜尋結果"""
    title = result.get('title', '')
    url = result.get('url', '')
    desc = result.get('description', '')

    # 提取姓名
    name = title
    for separator in [' - ', ' | ', ' – ']:
        if separator in title:
            name = title.split(separator)[0].strip()
            break

    # 提取職位（title 第二段）
    position = ""
    parts = title.split(' - ')
    if len(parts) >= 2:
        position = parts[1].strip()
    elif ' | ' in title:
        position = title.split(' | ')[0].replace(name, '').strip(' -|')

    # 提取技能
    combined_text = title + " " + desc
    skills = extract_skills_from_text(combined_text)

    # 清理 URL
    clean = clean_url(url)

    return {
        "name": name,
        "position": position or "BIM工程師",
        "skills": ", ".join(skills) if skills else "BIM, Revit",
        "linkedin_url": clean,
        "raw_title": title,
        "description": desc[:200]
    }


def search_candidates(job_title):
    """用多個搜尋查詢找候選人"""
    print(f"\n{'='*60}")
    print(f"🔍 搜尋職位：{job_title}")
    print(f"{'='*60}")

    queries = SEARCH_QUERIES.get(job_title, [])
    all_candidates = []
    seen_urls = set()

    for query in queries:
        print(f"\n   查詢：{query[:60]}...")
        data = brave_search(query, count=10)
        if not data:
            continue

        results = data.get('web', {}).get('results', [])
        found_this_round = 0

        for r in results:
            url = r.get('url', '')
            if 'linkedin.com/in/' not in url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)

            candidate = parse_result(r)
            candidate['job_title'] = job_title
            all_candidates.append(candidate)
            found_this_round += 1

            print(f"\n   ✅ {candidate['name']}")
            print(f"      職位：{candidate['position']}")
            print(f"      技能：{candidate['skills']}")
            print(f"      🔗 {candidate['linkedin_url']}")

        print(f"   → 本輪找到 {found_this_round} 位")

    print(f"\n📊 {job_title} 合計：{len(all_candidates)} 位")
    return all_candidates


def import_to_step1ne(candidates):
    """批量匯入到 Step1ne API"""
    print(f"\n{'='*60}")
    print(f"📤 匯入 {len(candidates)} 位候選人到 Step1ne")
    print(f"{'='*60}")

    success, fail = 0, 0
    for c in candidates:
        payload = {
            "name": c['name'],
            "position": c['job_title'],
            "location": "台灣",
            "skills": c['skills'],
            "source": "LinkedIn 公開搜尋",
            "recruiter": "Jacky",
            "notes": f"職位：{c['position']} | 來源：{c['linkedin_url']}",
            "linkedin_url": c['linkedin_url'],
            "actor": "Jacky-aibot"
        }
        try:
            r = requests.post(f"{STEP1NE_API}/candidates", json=payload, timeout=10)
            if r.status_code in [200, 201]:
                print(f"   ✅ {c['name']}")
                success += 1
            else:
                print(f"   ❌ {c['name']} ({r.status_code})")
                fail += 1
        except Exception as e:
            print(f"   ❌ {c['name']} → {e}")
            fail += 1

    print(f"\n✅ 成功：{success}  ❌ 失敗：{fail}")
    return success, fail


def save_json(candidates, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(candidates),
            "candidates": candidates
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已儲存：{path}")


# ==================== 主程式 ====================

def main():
    print("\n" + "="*60)
    print("🦞 Mike 專用 - 台灣 LinkedIn 人選搜尋工具（修正版）")
    print("="*60)

    if not BRAVE_API_KEY:
        print("❌ 找不到 BRAVE_API_KEY")
        sys.exit(1)

    print(f"✅ Brave API Key: {BRAVE_API_KEY[:10]}...")

    # 搜尋所有職位
    all_candidates = []
    for job_title in SEARCH_QUERIES.keys():
        candidates = search_candidates(job_title)
        all_candidates.extend(candidates)

    # 儲存結果
    out = f"/tmp/linkedin-tw-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    save_json(all_candidates, out)

    # 顯示摘要
    print(f"\n{'='*60}")
    print(f"📋 總計找到 {len(all_candidates)} 位候選人")
    print(f"{'='*60}")
    for c in all_candidates:
        print(f"   • {c['name']} | {c['skills'][:40]}")
        print(f"     🔗 {c['linkedin_url']}")

    # 確認匯入
    ans = input(f"\n匯入全部 {len(all_candidates)} 位到 Step1ne？(y/n): ").strip().lower()
    if ans == 'y':
        import_to_step1ne(all_candidates)
    else:
        print(f"⏭️  跳過匯入，結果在：{out}")

    print("\n✅ 完成！")


if __name__ == '__main__':
    main()
