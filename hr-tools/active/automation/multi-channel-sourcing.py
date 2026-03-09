#!/usr/bin/env python3
"""
多管道候選人搜尋系統
自動根據職缺類型選擇最佳搜尋管道
"""
import json
import sys
from datetime import datetime

# 職缺類型分類
TECH_POSITIONS = [
    "AI工程師", "數據分析師", "全端工程師", "後端開發工程師",
    "前端工程師", "BIM工程師", "軟體測試工程師", "資安工程師",
    "雲端維運工程師", "DevOps", "SRE", ".NET工程師",
    "Machine Learning Engineer", "Data Scientist", "Software Engineer"
]

# 管道分配策略
CHANNEL_STRATEGY = {
    "tech": {
        "linkedin": 30,
        "github": 50,
        "cakeresume": 20
    },
    "non_tech": {
        "linkedin": 60,
        "cakeresume": 30,
        "company_website": 10
    }
}

def is_tech_position(position):
    """判斷是否為技術職缺"""
    position_lower = position.lower()
    
    # 關鍵字判斷
    tech_keywords = [
        "工程師", "engineer", "developer", "programmer",
        "architect", "tech", "軟體", "software", "開發"
    ]
    
    for keyword in tech_keywords:
        if keyword in position_lower:
            return True
    
    # 完全比對
    for tech_pos in TECH_POSITIONS:
        if tech_pos.lower() in position_lower:
            return True
    
    return False

def calculate_channel_counts(total_count, is_tech):
    """計算各管道應搜尋的人數"""
    strategy = CHANNEL_STRATEGY["tech"] if is_tech else CHANNEL_STRATEGY["non_tech"]
    
    counts = {}
    for channel, percentage in strategy.items():
        counts[channel] = max(1, int(total_count * percentage / 100))
    
    return counts

def search_linkedin(position, skills, count):
    """LinkedIn 公開搜尋"""
    query = f"{position} {skills} Taiwan site:linkedin.com/in"
    
    # 實際使用時呼叫 OpenClaw web_search
    # results = web_search(query=query, count=count)
    
    return {
        "channel": "linkedin",
        "query": query,
        "count": count,
        "candidates": []  # 實際搜尋結果
    }

def search_github(position, skills, count):
    """GitHub Talent Search"""
    query = f"{skills} Taiwan site:github.com"
    
    # 實際使用時呼叫 OpenClaw web_search
    # results = web_search(query=query, count=count)
    
    return {
        "channel": "github",
        "query": query,
        "count": count,
        "candidates": []
    }

def search_cakeresume(position, skills, count):
    """CakeResume 搜尋"""
    query = f"{position} {skills} site:cakeresume.com"
    
    # 實際使用時呼叫 OpenClaw web_search
    # results = web_search(query=query, count=count)
    
    return {
        "channel": "cakeresume",
        "query": query,
        "count": count,
        "candidates": []
    }

def search_company_website(position, target_companies, count):
    """公司官網搜尋"""
    results = []
    
    for company in target_companies[:count]:
        # 搜尋公司官網 /team 或 /about 頁面
        query = f"{company} team site:{company}"
        
        # 實際使用時呼叫 web_fetch
        # page_content = web_fetch(f"https://{company}/team")
        
        results.append({
            "company": company,
            "query": query,
            "candidates": []
        })
    
    return {
        "channel": "company_website",
        "count": count,
        "results": results
    }

def multi_channel_search(position, skills, total_count=20, target_companies=None):
    """多管道搜尋主函數"""
    
    # 判斷職缺類型
    is_tech = is_tech_position(position)
    position_type = "技術職缺" if is_tech else "非技術職缺"
    
    print(f"📊 職缺分析", file=sys.stderr)
    print(f"   職位：{position}", file=sys.stderr)
    print(f"   類型：{position_type}", file=sys.stderr)
    print(f"   技能：{skills}", file=sys.stderr)
    print(f"   目標：{total_count} 人", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 計算各管道搜尋人數
    channel_counts = calculate_channel_counts(total_count, is_tech)
    
    print(f"🎯 管道分配", file=sys.stderr)
    for channel, count in channel_counts.items():
        print(f"   {channel}: {count} 人", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 執行多管道搜尋
    all_results = []
    
    if "linkedin" in channel_counts:
        print(f"🔍 LinkedIn 搜尋（{channel_counts['linkedin']} 人）...", file=sys.stderr)
        linkedin_results = search_linkedin(position, skills, channel_counts["linkedin"])
        all_results.append(linkedin_results)
    
    if "github" in channel_counts:
        print(f"🔍 GitHub 搜尋（{channel_counts['github']} 人）...", file=sys.stderr)
        github_results = search_github(position, skills, channel_counts["github"])
        all_results.append(github_results)
    
    if "cakeresume" in channel_counts:
        print(f"🍰 CakeResume 搜尋（{channel_counts['cakeresume']} 人）...", file=sys.stderr)
        cakeresume_results = search_cakeresume(position, skills, channel_counts["cakeresume"])
        all_results.append(cakeresume_results)
    
    if "company_website" in channel_counts and target_companies:
        print(f"🏢 公司官網搜尋（{channel_counts['company_website']} 家）...", file=sys.stderr)
        company_results = search_company_website(position, target_companies, channel_counts["company_website"])
        all_results.append(company_results)
    
    # 彙總結果
    result = {
        "position": position,
        "skills": skills,
        "position_type": position_type,
        "is_tech": is_tech,
        "total_count": total_count,
        "channel_strategy": channel_counts,
        "search_results": all_results,
        "timestamp": datetime.now().isoformat()
    }
    
    print("", file=sys.stderr)
    print("✅ 多管道搜尋完成", file=sys.stderr)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 multi-channel-sourcing.py <職位> <技能> [數量]")
        print("範例: python3 multi-channel-sourcing.py 'AI工程師' 'Python Machine Learning' 20")
        sys.exit(1)
    
    position = sys.argv[1]
    skills = sys.argv[2]
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    result = multi_channel_search(position, skills, count)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
