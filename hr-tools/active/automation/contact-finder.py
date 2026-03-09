#!/usr/bin/env python3
"""
多管道聯絡資料搜尋系統
從 LinkedIn/GitHub/公司官網等多個來源交叉搜尋聯絡資料
"""
import json
import sys
import re
from urllib.parse import urlparse

def extract_email_from_text(text):
    """從文字中提取 Email"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # 去重

def extract_phone_from_text(text):
    """從文字中提取電話"""
    # 台灣電話格式
    phone_patterns = [
        r'\+886[-\s]?\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}',  # +886-2-1234-5678
        r'0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}',             # 02-1234-5678
        r'\d{4}[-\s]?\d{6}',                             # 0912-345678
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return list(set(phones))  # 去重

def search_google_contact(name, company):
    """Google 搜尋聯絡資料"""
    queries = [
        f"{name} {company} email",
        f"{name} {company} contact",
        f"{name} {company} 聯絡",
    ]
    
    results = []
    
    for query in queries:
        # 實際使用時呼叫 web_search
        # search_results = web_search(query=query, count=5)
        
        # 從搜尋結果中提取 Email/電話
        # for result in search_results:
        #     description = result.get('description', '')
        #     emails = extract_email_from_text(description)
        #     phones = extract_phone_from_text(description)
        
        results.append({
            "query": query,
            "emails": [],  # 實際提取的 emails
            "phones": []   # 實際提取的 phones
        })
    
    return results

def search_github_email(github_username):
    """從 GitHub profile 搜尋 Email"""
    
    # 方案 1: GitHub API（需要 token）
    # api_url = f"https://api.github.com/users/{github_username}"
    
    # 方案 2: 爬取公開 profile 頁面
    profile_url = f"https://github.com/{github_username}"
    
    # 實際使用時呼叫 web_fetch
    # page_content = web_fetch(profile_url)
    # emails = extract_email_from_text(page_content)
    
    return {
        "source": "github",
        "url": profile_url,
        "emails": [],  # 實際提取的 emails
        "public_repos": None,  # 可從 API 取得
        "bio": None
    }

def search_company_website_contact(company_website, candidate_name):
    """從公司官網搜尋員工聯絡資訊"""
    
    # 常見頁面
    pages_to_check = [
        "/team",
        "/about",
        "/about-us",
        "/people",
        "/our-team",
        "/contact"
    ]
    
    results = []
    
    for page in pages_to_check:
        url = f"{company_website}{page}"
        
        # 實際使用時呼叫 web_fetch
        # try:
        #     page_content = web_fetch(url)
        #     
        #     # 搜尋候選人姓名
        #     if candidate_name in page_content:
        #         emails = extract_email_from_text(page_content)
        #         phones = extract_phone_from_text(page_content)
        #         
        #         results.append({
        #             "url": url,
        #             "found": True,
        #             "emails": emails,
        #             "phones": phones
        #         })
        # except:
        #     continue
        
        results.append({
            "url": url,
            "found": False,
            "emails": [],
            "phones": []
        })
    
    return results

def find_contact_info(candidate):
    """
    多管道搜尋候選人聯絡資料
    
    candidate = {
        "name": "張三",
        "company": "台積電",
        "linkedin_url": "https://linkedin.com/in/...",
        "github_username": "zhangsan" (optional)
    }
    """
    
    name = candidate.get("name", "")
    company = candidate.get("company", "")
    github_username = candidate.get("github_username", "")
    
    print(f"🔍 搜尋聯絡資料：{name}", file=sys.stderr)
    print(f"   公司：{company}", file=sys.stderr)
    
    all_results = {
        "candidate": candidate,
        "contact_found": False,
        "emails": [],
        "phones": [],
        "sources": []
    }
    
    # 管道 1: Google 搜尋
    print("   📊 Google 交叉搜尋...", file=sys.stderr)
    google_results = search_google_contact(name, company)
    all_results["sources"].append({
        "channel": "google",
        "results": google_results
    })
    
    # 從 Google 結果彙總
    for result in google_results:
        all_results["emails"].extend(result.get("emails", []))
        all_results["phones"].extend(result.get("phones", []))
    
    # 管道 2: GitHub Email（如果有）
    if github_username:
        print("   💻 GitHub Email 搜尋...", file=sys.stderr)
        github_result = search_github_email(github_username)
        all_results["sources"].append({
            "channel": "github",
            "results": github_result
        })
        all_results["emails"].extend(github_result.get("emails", []))
    
    # 管道 3: 公司官網
    if company:
        print("   🏢 公司官網搜尋...", file=sys.stderr)
        # 先取得公司官網（需要另外搜尋或從資料庫取得）
        # company_website = get_company_website(company)
        # company_results = search_company_website_contact(company_website, name)
        # all_results["sources"].append({
        #     "channel": "company_website",
        #     "results": company_results
        # })
    
    # 去重
    all_results["emails"] = list(set(all_results["emails"]))
    all_results["phones"] = list(set(all_results["phones"]))
    
    # 判斷是否找到聯絡資料
    if all_results["emails"] or all_results["phones"]:
        all_results["contact_found"] = True
        print(f"   ✅ 找到聯絡資料", file=sys.stderr)
        if all_results["emails"]:
            print(f"      Email: {', '.join(all_results['emails'])}", file=sys.stderr)
        if all_results["phones"]:
            print(f"      電話: {', '.join(all_results['phones'])}", file=sys.stderr)
    else:
        print(f"   ⚠️  未找到聯絡資料", file=sys.stderr)
    
    return all_results

def batch_find_contacts(candidates):
    """批量搜尋聯絡資料"""
    results = []
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n[{i}/{len(candidates)}]", file=sys.stderr)
        result = find_contact_info(candidate)
        results.append(result)
    
    # 統計
    found_count = sum(1 for r in results if r["contact_found"])
    total_emails = sum(len(r["emails"]) for r in results)
    total_phones = sum(len(r["phones"]) for r in results)
    
    print(f"\n📊 批量搜尋完成", file=sys.stderr)
    print(f"   總計：{len(candidates)} 位候選人", file=sys.stderr)
    print(f"   找到聯絡資料：{found_count} 位（{found_count/len(candidates)*100:.1f}%）", file=sys.stderr)
    print(f"   Email：{total_emails} 個", file=sys.stderr)
    print(f"   電話：{total_phones} 個", file=sys.stderr)
    
    return results

if __name__ == "__main__":
    # 測試
    test_candidates = [
        {
            "name": "張三",
            "company": "台積電",
            "linkedin_url": "https://linkedin.com/in/test",
            "github_username": "zhangsan"
        }
    ]
    
    if len(sys.argv) > 1:
        # 從 JSON 檔案讀取
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            test_candidates = json.load(f)
    
    results = batch_find_contacts(test_candidates)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))
