#!/usr/bin/env python3
"""
統一人選搜尋系統 v3
整合：LinkedIn（web_search）+ GitHub（API）
"""

import sys
import json
import subprocess
import os
import time
import re
import urllib.parse
from datetime import datetime, timedelta

# 設定
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("❌ 錯誤：GITHUB_TOKEN 環境變數未設定", file=sys.stderr)
    sys.exit(1)

def search_linkedin_via_google(keywords, location="Taiwan", max_results=20):
    """使用 Google 搜尋 LinkedIn 公開資料"""
    
    print(f"🔍 搜尋 LinkedIn：{keywords} @ {location}", file=sys.stderr)
    
    query = f"{keywords} {location} site:linkedin.com/in"
    
    try:
        # 用 curl + user-agent 模擬 Google Chrome 搜尋
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"
        
        result = subprocess.run([
            'curl', '-s', '-L',
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            search_url
        ], capture_output=True, text=True, timeout=15)
        
        html = result.stdout
        
        # 用正則提取 LinkedIn URLs
        linkedin_urls = []
        
        # 模式 1：href="https://www.linkedin.com/in/..."
        urls = re.findall(r'href="(https://(?:www\.)?linkedin\.com/in/[^"]+)"', html)
        linkedin_urls.extend(urls)
        
        # 模式 2：純文字中的 LinkedIn URLs
        urls = re.findall(r'(https://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+)(?:\?|$|/|")', html)
        linkedin_urls.extend(urls)
        
        # 清理 URL（移除查詢參數）
        linkedin_urls = [url.split('?')[0].split('#')[0].rstrip('/') for url in linkedin_urls]
        
        # 去重
        linkedin_urls = list(set(linkedin_urls))[:max_results]
        
        print(f"  ✓ 找到 {len(linkedin_urls)} 位 LinkedIn 候選人", file=sys.stderr)
        return linkedin_urls
        
    except Exception as e:
        print(f"  ❌ LinkedIn 搜尋失敗：{e}", file=sys.stderr)
        return []


def search_github(keywords, location="Taiwan", max_results=20):
    """使用 GitHub API 搜尋開發者"""
    
    print(f"🐙 搜尋 GitHub：{keywords} @ {location}", file=sys.stderr)
    
    candidates = []
    
    try:
        # 構建搜尋查詢
        # 範例：language:python location:Taiwan followers:>10
        query = f"language:{keywords.split()[0].lower()} location:{location} followers:>5"
        
        # GitHub Search API
        search_url = "https://api.github.com/search/users"
        params = {
            "q": query,
            "sort": "followers",
            "order": "desc",
            "per_page": min(max_results, 100)
        }
        
        # 構建完整 URL
        full_url = search_url + "?" + urllib.parse.urlencode(params)
        
        # 呼叫 GitHub API
        result = subprocess.run([
            'curl', '-s',
            '-H', f'Authorization: token {GITHUB_TOKEN}',
            '-H', 'Accept: application/vnd.github.v3+json',
            full_url
        ], capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            data = json.loads(result.stdout)
            
            if 'items' in data:
                for user in data['items'][:max_results]:
                    # 獲取完整用戶資料
                    user_detail = get_github_user_detail(user['login'])
                    if user_detail:
                        candidates.append(user_detail)
        
        print(f"  ✓ 找到 {len(candidates)} 位 GitHub 開發者", file=sys.stderr)
        return candidates
        
    except Exception as e:
        print(f"  ❌ GitHub 搜尋失敗：{e}", file=sys.stderr)
        return []


def get_github_user_detail(username):
    """獲取 GitHub 用戶詳細資料"""
    
    try:
        result = subprocess.run([
            'curl', '-s',
            '-H', f'Authorization: token {GITHUB_TOKEN}',
            '-H', 'Accept: application/vnd.github.v3+json',
            f'https://api.github.com/users/{username}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            user = json.loads(result.stdout)
            
            # 獲取技能（從 repos 推斷）
            skills = extract_github_skills(username)
            
            # 檢查是否待業
            available = check_github_availability(user)
            
            return {
                'name': user.get('name') or username,
                'login': username,
                'company': user.get('company'),
                'bio': user.get('bio'),
                'location': user.get('location'),
                'github_url': user.get('html_url'),
                'followers': user.get('followers'),
                'public_repos': user.get('public_repos'),
                'skills': skills,
                'available': available,
                'source': 'github'
            }
    except Exception as e:
        print(f"  ⚠️  無法獲取 {username} 詳細資料：{e}", file=sys.stderr)
        return None


def extract_github_skills(username):
    """從 GitHub repos 提取技能"""
    
    try:
        result = subprocess.run([
            'curl', '-s',
            '-H', f'Authorization: token {GITHUB_TOKEN}',
            '-H', 'Accept: application/vnd.github.v3+json',
            f'https://api.github.com/users/{username}/repos?sort=stars&per_page=10'
        ], capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            repos = json.loads(result.stdout)
            
            # 統計語言
            languages = {}
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            # 按出現次數排序
            skills = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            return [skill[0] for skill in skills[:5]]  # Top 5
    except Exception as e:
        pass
    
    return []


def check_github_availability(user):
    """檢查用戶是否可能待業"""
    
    # 簡單啟發式：
    # - bio 包含「找工作」等關鍵字
    # - company = null
    # - 最近有提交（活躍）
    
    bio = (user.get('bio') or '').lower()
    company = user.get('company')
    
    available_keywords = ['looking for', '求職', '找工作', 'hiring', 'open to opportunities']
    
    for keyword in available_keywords:
        if keyword in bio:
            return True
    
    if not company:
        return True
    
    return False


def parse_linkedin_candidate(url):
    """解析 LinkedIn URL 為候選人"""
    
    # 從 URL 提取用戶名
    username = url.split('/in/')[-1].split('?')[0].split('/')[0]
    
    # 簡單的名字轉換
    name = username.replace('-', ' ').title()
    
    return {
        'name': name,
        'linkedin_url': url,
        'source': 'linkedin'
    }


def merge_candidates(linkedin_candidates, github_candidates):
    """合併 LinkedIn + GitHub 候選人"""
    
    all_candidates = []
    
    # LinkedIn 候選人
    for url in linkedin_candidates:
        candidate = parse_linkedin_candidate(url)
        all_candidates.append(candidate)
    
    # GitHub 候選人
    for candidate in github_candidates:
        all_candidates.append(candidate)
    
    # 去重（基於 email/github_url）
    seen = set()
    unique = []
    for c in all_candidates:
        key = c.get('github_url') or c.get('linkedin_url') or c.get('name')
        if key not in seen:
            seen.add(key)
            unique.append(c)
    
    return unique


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='統一人選搜尋系統 v3')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=20, help='最大結果數')
    parser.add_argument('--linkedin-only', action='store_true', help='只搜 LinkedIn')
    parser.add_argument('--github-only', action='store_true', help='只搜 GitHub')
    
    args = parser.parse_args()
    
    print(f"🚀 開始搜尋：{args.keywords} @ {args.location}", file=sys.stderr)
    print(f"📍 最大結果：{args.max_results}", file=sys.stderr)
    print("", file=sys.stderr)
    
    linkedin_candidates = []
    github_candidates = []
    
    # 搜尋
    if not args.github_only:
        linkedin_candidates = search_linkedin_via_google(
            args.keywords,
            args.location,
            args.max_results
        )
    
    if not args.linkedin_only:
        github_candidates = search_github(
            args.keywords,
            args.location,
            args.max_results
        )
    
    # 合併
    all_candidates = merge_candidates(linkedin_candidates, github_candidates)
    
    print(f"", file=sys.stderr)
    print(f"✅ 完成：共找到 {len(all_candidates)} 位候選人", file=sys.stderr)
    print(f"  - LinkedIn：{len(linkedin_candidates)} 位", file=sys.stderr)
    print(f"  - GitHub：{len(github_candidates)} 位", file=sys.stderr)
    
    # 輸出 JSON
    print(json.dumps(all_candidates, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
