#!/usr/bin/env python3
"""
PTT Soft_Job 版爬蟲
爬取技術人才自我介紹文章
"""

import sys
import json
import re
import time
from datetime import datetime
import subprocess

def fetch_ptt_board(board="Soft_Job", pages=5):
    """爬取 PTT 看板文章列表"""
    
    articles = []
    
    for page in range(1, pages + 1):
        # PTT 網頁版 URL
        if page == 1:
            url = f"https://www.ptt.cc/bbs/{board}/index.html"
        else:
            # 計算頁碼（PTT 是倒序）
            url = f"https://www.ptt.cc/bbs/{board}/index{page}.html"
        
        print(f"🔍 爬取 {board} 第 {page} 頁...", file=sys.stderr)
        
        try:
            result = subprocess.run(
                ['curl', '-s', '-b', 'over18=1', url],  # 加 cookie 繞過 18+ 警告
                capture_output=True,
                text=True,
                timeout=10
            )
            
            html = result.stdout
            
            # 解析文章連結
            # PTT 格式：<div class="title"><a href="/bbs/Soft_Job/M.xxx.html">標題</a></div>
            pattern = r'<div class="title">\s*<a href="(/bbs/' + board + r'/M\.\d+\.A\.[A-F0-9]+\.html)">(.+?)</a>'
            matches = re.findall(pattern, html)
            
            for link, title in matches:
                articles.append({
                    'title': title.strip(),
                    'url': f"https://www.ptt.cc{link}",
                    'board': board
                })
            
            time.sleep(1)  # 避免過快
            
        except Exception as e:
            print(f"❌ 爬取失敗：{e}", file=sys.stderr)
    
    return articles

def parse_article_content(url):
    """解析文章內容"""
    
    try:
        result = subprocess.run(
            ['curl', '-s', '-b', 'over18=1', url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        html = result.stdout
        
        # 提取文章內容（PTT 格式）
        content_match = re.search(r'<div id="main-content"[^>]*>(.*?)<div class="push"', html, re.DOTALL)
        
        if not content_match:
            return None
        
        content = content_match.group(1)
        
        # 移除 HTML 標籤
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'--\n※ 發信站.*', '', content, flags=re.DOTALL)
        content = content.strip()
        
        return content
    
    except Exception as e:
        print(f"⚠️  無法解析 {url}: {e}", file=sys.stderr)
        return None

def extract_candidate_info(title, content):
    """從文章提取候選人資訊"""
    
    if not content:
        return None
    
    # 提取技能（關鍵字）
    skills = []
    skill_keywords = [
        'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'go', 'rust',
        'react', 'vue', 'angular', 'node\\.js', 'django', 'flask',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
        'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'k8s',
        'machine learning', 'ml', 'deep learning', 'ai', 'tensorflow', 'pytorch',
        'git', 'linux', 'ci/cd', 'devops'
    ]
    
    content_lower = content.lower()
    for skill in skill_keywords:
        if re.search(r'\b' + skill + r'\b', content_lower):
            skills.append(skill.upper() if len(skill) <= 3 else skill.title())
    
    # 提取經驗年資
    exp_match = re.search(r'(\d+)\s*年', content)
    years_of_experience = int(exp_match.group(1)) if exp_match else 0
    
    # 提取聯絡方式
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
    email = email_match.group(0) if email_match else None
    
    # 提取 LINE ID
    line_match = re.search(r'LINE[：:\s]*([a-zA-Z0-9_\-]+)', content, re.IGNORECASE)
    line_id = line_match.group(1) if line_match else None
    
    return {
        'title': title,
        'skills': list(set(skills)),  # 去重
        'years_of_experience': years_of_experience,
        'email': email,
        'line_id': line_id,
        'source': 'ptt_soft_job'
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PTT Soft_Job 爬蟲')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--pages', type=int, default=3, help='爬取頁數')
    parser.add_argument('--output', default=None, help='輸出檔案')
    
    args = parser.parse_args()
    
    # 爬取文章列表
    articles = fetch_ptt_board("Soft_Job", args.pages)
    
    print(f"✅ 找到 {len(articles)} 篇文章", file=sys.stderr)
    
    # 篩選包含關鍵字的文章
    keywords_list = [k.lower() for k in args.keywords.split(',')]
    filtered_articles = []
    
    for article in articles:
        title_lower = article['title'].lower()
        if any(kw in title_lower for kw in keywords_list) or any(kw in title_lower for kw in ['自介', '徵', 'hiring']):
            filtered_articles.append(article)
    
    print(f"📝 篩選後剩 {len(filtered_articles)} 篇相關文章", file=sys.stderr)
    
    # 解析文章內容
    candidates = []
    for i, article in enumerate(filtered_articles[:10], 1):  # 最多解析 10 篇
        print(f"📖 解析 {i}/{min(10, len(filtered_articles))}: {article['title']}", file=sys.stderr)
        
        content = parse_article_content(article['url'])
        if content:
            info = extract_candidate_info(article['title'], content)
            if info and info['skills']:  # 至少要有技能
                info['ptt_url'] = article['url']
                candidates.append(info)
        
        time.sleep(2)  # 避免過快被擋
    
    # 輸出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        print(f"💾 結果已存至 {args.output}", file=sys.stderr)
    else:
        print(json.dumps(candidates, f, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 完成：{len(candidates)} 位候選人", file=sys.stderr)

if __name__ == '__main__':
    main()
