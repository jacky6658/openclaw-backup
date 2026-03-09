#!/usr/bin/env python3
"""
CakeResume 人才搜尋工具
用途：從 CakeResume 公開搜尋頁面抓取候選人資料
特點：台灣本地人才庫、設計/創意/新創職位豐富
"""

import subprocess
import json
import re
import sys
import time
from datetime import datetime

def run_browser(cmd):
    """執行 agent-browser 指令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        print(f"⚠️  Browser 指令執行失敗: {e}")
        return ""

def search_cakeresume(keyword, location="台灣", max_results=15):
    """
    搜尋 CakeResume 公開職涯資料
    
    Args:
        keyword: 搜尋關鍵字（職位名稱或技能）
        location: 地點（台灣、台北、新竹等）
        max_results: 最多回傳數量
    
    Returns:
        list: 候選人資料
    """
    print(f"🔍 CakeResume 搜尋: {keyword} @ {location}")
    
    # CakeResume 搜尋 URL（使用 Google 搜尋 CakeResume 公開資料）
    # 格式：site:cakeresume.com/s/ "關鍵字" "地點"
    query = f'site:cakeresume.com/s/ "{keyword}" "{location}"'
    
    # 使用 web_search 工具（OpenClaw 內建）
    # 注意：這裡我們需要用 shell 呼叫 openclaw 的 web_search
    # 但因為在 Python 中，我們改用 agent-browser + Google
    
    google_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
    
    print(f"📡 開啟搜尋頁面...")
    run_browser(f'agent-browser open "{google_url}"')
    time.sleep(3)
    
    # 取得快照
    snapshot_raw = run_browser('agent-browser snapshot')
    
    # 提取 CakeResume 連結
    candidates = []
    
    # 用正則提取 CakeResume 個人頁面連結
    # 格式：https://www.cakeresume.com/s/xxxxx
    urls = re.findall(r'https://www\.cakeresume\.com/s/([a-zA-Z0-9_-]+)', snapshot_raw)
    urls = list(set(urls))[:max_results]  # 去重並限制數量
    
    print(f"📊 找到 {len(urls)} 個候選人")
    
    for i, user_id in enumerate(urls):
        profile_url = f"https://www.cakeresume.com/s/{user_id}"
        
        print(f"  [{i+1}/{len(urls)}] 讀取 {user_id}...")
        
        # 開啟個人頁面
        run_browser(f'agent-browser open "{profile_url}"')
        time.sleep(2)
        
        # 取得頁面快照
        snapshot = run_browser('agent-browser snapshot')
        
        # 提取資訊
        profile = extract_profile_info(snapshot, user_id, profile_url)
        candidates.append(profile)
        
        # 顯示進度
        if profile.get('name'):
            print(f"       👤 {profile['name']}")
        if profile.get('title'):
            print(f"       💼 {profile['title']}")
        if profile.get('location'):
            print(f"       📍 {profile['location']}")
        
        time.sleep(1)  # 避免太快
    
    # 關閉瀏覽器
    run_browser('agent-browser close')
    
    return candidates

def extract_profile_info(snapshot_text, user_id, url):
    """
    從 CakeResume 頁面快照中提取個人資訊
    
    Args:
        snapshot_text: 頁面快照文字
        user_id: CakeResume 用戶 ID
        url: 個人頁面 URL
    
    Returns:
        dict: 個人資料
    """
    profile = {
        'user_id': user_id,
        'url': url,
        'source': 'CakeResume',
        'name': None,
        'title': None,
        'location': None,
        'email': None,
        'skills': [],
        'experience': [],
        'education': [],
        'extracted_at': datetime.now().isoformat()
    }
    
    lines = snapshot_text.split('\n')
    
    # 嘗試提取姓名（通常在頁面前面）
    for i, line in enumerate(lines[:20]):
        # CakeResume 姓名通常是較短的文字，且不包含特殊字元
        if len(line) > 2 and len(line) < 30 and not any(x in line for x in ['https://', '@', 'CakeResume', '分享', '聯絡']):
            # 檢查是否為人名格式（中文或英文）
            if re.match(r'^[a-zA-Z\s\u4e00-\u9fff]+$', line.strip()):
                if not profile['name']:
                    profile['name'] = line.strip()
                    break
    
    # 提取職稱（通常在姓名後面）
    for line in lines[:30]:
        # 職稱關鍵字
        if any(keyword in line for keyword in ['Engineer', 'Designer', 'Manager', '工程師', '設計師', '經理', '主管', '開發', 'Developer']):
            if len(line) < 50 and not profile['title']:
                profile['title'] = line.strip()
                break
    
    # 提取地點
    for line in lines:
        if any(loc in line for loc in ['台北', '新北', '台中', '台南', '高雄', '新竹', '台灣', 'Taipei', 'Taiwan']):
            if len(line) < 30:
                profile['location'] = line.strip()
                break
    
    # 提取 Email（如果有公開）
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', snapshot_text)
    if emails:
        profile['email'] = emails[0]
    
    # 提取技能（常見技術關鍵字）
    skill_keywords = [
        'Python', 'JavaScript', 'React', 'Vue', 'Node.js', 'Java', 'C++', 'Go', 'Rust',
        'Django', 'Flask', 'Spring', 'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
        'Machine Learning', 'AI', 'Data Science', 'DevOps', 'Frontend', 'Backend',
        'UI', 'UX', 'Figma', 'Sketch', 'Adobe', 'Photoshop', 'Illustrator',
        'SQL', 'MongoDB', 'PostgreSQL', 'Redis', 'Git', 'CI/CD'
    ]
    
    for skill in skill_keywords:
        if skill in snapshot_text:
            profile['skills'].append(skill)
    
    # 提取工作經驗（公司名稱）
    company_patterns = [
        r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:Inc\.|Ltd\.|Corp\.|Co\.)',
        r'([\u4e00-\u9fff]{2,10}(?:科技|資訊|軟體|網路|數位|創意|設計|顧問|股份有限公司))',
    ]
    
    for pattern in company_patterns:
        companies = re.findall(pattern, snapshot_text)
        profile['experience'].extend(companies[:3])  # 最多 3 家
    
    return profile

def format_for_import(candidates, position_name):
    """
    格式化為履歷池匯入格式
    
    Args:
        candidates: 候選人列表
        position_name: 職位名稱
    
    Returns:
        list: 格式化後的資料
    """
    formatted = []
    
    for c in candidates:
        row = {
            '候選人姓名': c.get('name') or c.get('user_id'),
            '聯絡方式': c.get('email') or '',
            '目前公司': c['experience'][0] if c.get('experience') else '',
            '職位': c.get('title') or '',
            '技能標籤': ', '.join(c.get('skills', [])[:5]),
            '來源': 'CakeResume',
            '狀態': '待聯繫',
            '應徵職位': position_name,
            '備註': f"CakeResume: {c['url']}\n地點: {c.get('location', '')}"
        }
        formatted.append(row)
    
    return formatted

def main():
    """主函數"""
    # 命令列參數
    keyword = sys.argv[1] if len(sys.argv) > 1 else "UI Designer"
    location = sys.argv[2] if len(sys.argv) > 2 else "台灣"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    print("=" * 60)
    print("🎯 CakeResume 人才搜尋工具")
    print("=" * 60)
    
    # 搜尋
    candidates = search_cakeresume(keyword, location, max_results)
    
    if not candidates:
        print("❌ 沒有找到符合條件的候選人")
        return
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("📊 搜尋結果摘要")
    print("=" * 60)
    
    print(f"\n📋 總計: {len(candidates)} 人\n")
    
    for i, c in enumerate(candidates):
        print(f"{i+1}. {c.get('name') or c.get('user_id')}")
        if c.get('title'):
            print(f"   💼 {c['title']}")
        if c.get('location'):
            print(f"   📍 {c['location']}")
        if c.get('email'):
            print(f"   📧 {c['email']}")
        if c.get('skills'):
            print(f"   🔧 {', '.join(c['skills'][:3])}")
        print(f"   🔗 {c['url']}")
        print()
    
    # 存檔
    output_file = f"/tmp/cakeresume-candidates-{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    
    print(f"💾 結果已存至: {output_file}")
    
    # 格式化為匯入格式
    formatted = format_for_import(candidates, keyword)
    formatted_file = f"/tmp/cakeresume-formatted-{int(time.time())}.json"
    with open(formatted_file, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)
    
    print(f"📋 匯入格式已存至: {formatted_file}")

if __name__ == "__main__":
    main()
