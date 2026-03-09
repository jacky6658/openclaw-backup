#!/usr/bin/env python3
"""
GitHub 人才搜尋工具
用途：搜尋 GitHub 開發者，提取聯絡資訊用於招募
"""

import subprocess
import json
import re
import sys
import time
from datetime import datetime

def run_browser(cmd):
    """執行 agent-browser 指令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()

def search_github_users(location="taipei", language="python", min_repos=5, min_followers=10, max_results=20):
    """
    搜尋 GitHub 用戶
    
    Args:
        location: 地點 (taipei, taiwan, etc.)
        language: 程式語言 (python, javascript, java, etc.)
        min_repos: 最少 repo 數
        min_followers: 最少 followers 數
        max_results: 最多回傳數量
    """
    print(f"🔍 搜尋條件: location:{location} language:{language} repos:>{min_repos} followers:>{min_followers}")
    
    # 構建搜尋 URL
    query = f"location:{location}"
    if language:
        query += f" language:{language}"
    if min_repos:
        query += f" repos:>{min_repos}"
    if min_followers:
        query += f" followers:>{min_followers}"
    
    url = f"https://github.com/search?q={query.replace(' ', '+')}&type=users"
    
    # 開啟搜尋頁面
    run_browser(f'agent-browser open "{url}"')
    time.sleep(2)
    
    # 取得快照
    snapshot = run_browser('agent-browser snapshot -i --json')
    
    try:
        data = json.loads(snapshot)
        refs = data.get('data', {}).get('refs', {})
    except:
        print("❌ 無法解析搜尋結果")
        return []
    
    # 提取用戶名
    users = []
    for ref_id, ref_data in refs.items():
        name = ref_data.get('name', '')
        role = ref_data.get('role', '')
        
        # 尋找 Follow 按鈕前面的用戶名連結
        if role == 'link' and name and not name.startswith('Page') and name != 'Follow':
            # 檢查是否為用戶名格式 (通常是小寫+數字)
            if re.match(r'^[a-zA-Z0-9_-]+$', name) and len(name) < 40:
                # 排除常見非用戶名的連結
                if name.lower() not in ['code', 'repositories', 'issues', 'pull', 'discussions', 
                                         'users', 'more', 'javascript', 'python', 'java', 'html',
                                         'c++', 'c#', 'css', 'php', 'homepage', 'pricing', 'sign',
                                         'advanced', 'search', 'sponsorable']:
                    if name not in [u.get('username') for u in users]:
                        users.append({'username': name, 'ref': ref_id})
        
        if len(users) >= max_results:
            break
    
    print(f"📊 找到 {len(users)} 個開發者")
    return users

def get_user_profile(username):
    """
    取得用戶詳細資料
    
    Args:
        username: GitHub 用戶名
    
    Returns:
        dict: 用戶資料
    """
    print(f"  📄 讀取 {username} 的資料...")
    
    # 開啟用戶頁面
    run_browser(f'agent-browser open "https://github.com/{username}"')
    time.sleep(1)
    
    # 取得頁面內容
    snapshot = run_browser('agent-browser snapshot -i --json')
    
    profile = {
        'username': username,
        'url': f'https://github.com/{username}',
        'name': None,
        'bio': None,
        'location': None,
        'email': None,
        'company': None,
        'website': None,
        'twitter': None,
        'repos': None,
        'followers': None,
    }
    
    try:
        data = json.loads(snapshot)
        refs = data.get('data', {}).get('refs', {})
        snapshot_text = data.get('data', {}).get('snapshot', '')
        
        for ref_id, ref_data in refs.items():
            name = ref_data.get('name', '')
            
            # 提取各種資訊
            if '@' in name and '.' in name:  # Email
                profile['email'] = name
            elif name.startswith('http'):  # Website
                if 'twitter.com' in name or 'x.com' in name:
                    profile['twitter'] = name
                else:
                    profile['website'] = name
            elif 'followers' in name.lower():
                # 嘗試提取 followers 數量
                match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?[kK]?)', name)
                if match:
                    profile['followers'] = match.group(1)
        
        # 從 snapshot 文本中提取更多資訊
        lines = snapshot_text.split('\n')
        for line in lines:
            if 'location' in line.lower() and profile['location'] is None:
                # 嘗試提取位置
                match = re.search(r'"([^"]+)"', line)
                if match:
                    profile['location'] = match.group(1)
                    
    except Exception as e:
        print(f"  ⚠️ 解析 {username} 資料時出錯: {e}")
    
    return profile

def search_and_extract(location="taipei", language="python", min_repos=5, min_followers=10, max_results=10, get_details=True):
    """
    完整搜尋流程：搜尋 + 提取詳細資料
    """
    print("=" * 60)
    print("🎯 GitHub 人才搜尋工具")
    print("=" * 60)
    
    # 搜尋用戶
    users = search_github_users(location, language, min_repos, min_followers, max_results)
    
    if not users:
        print("❌ 沒有找到符合條件的用戶")
        return []
    
    results = []
    
    if get_details:
        print(f"\n📋 正在提取 {len(users)} 位開發者的詳細資料...\n")
        for i, user in enumerate(users):
            profile = get_user_profile(user['username'])
            results.append(profile)
            
            # 顯示進度
            print(f"  [{i+1}/{len(users)}] {profile['username']}")
            if profile.get('email'):
                print(f"       📧 {profile['email']}")
            if profile.get('location'):
                print(f"       📍 {profile['location']}")
            
            time.sleep(0.5)  # 避免太快被擋
    else:
        results = [{'username': u['username'], 'url': f"https://github.com/{u['username']}"} for u in users]
    
    # 關閉瀏覽器
    run_browser('agent-browser close')
    
    return results

def main():
    """主函數"""
    # 預設參數
    location = sys.argv[1] if len(sys.argv) > 1 else "taipei"
    language = sys.argv[2] if len(sys.argv) > 2 else "python"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    results = search_and_extract(
        location=location,
        language=language,
        min_repos=5,
        min_followers=10,
        max_results=max_results,
        get_details=True
    )
    
    # 輸出結果
    print("\n" + "=" * 60)
    print("📊 搜尋結果摘要")
    print("=" * 60)
    
    # 有 email 的
    with_email = [r for r in results if r.get('email')]
    print(f"\n✅ 有 Email 的開發者: {len(with_email)} 人")
    for r in with_email:
        print(f"   • {r['username']} - {r['email']}")
    
    # 所有結果
    print(f"\n📋 全部開發者: {len(results)} 人")
    for r in results:
        print(f"   • {r['username']} - {r['url']}")
    
    # 存檔
    output_file = f"/tmp/github-talent-{location}-{language}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果已存至: {output_file}")

if __name__ == "__main__":
    main()
