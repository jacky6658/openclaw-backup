#!/usr/bin/env python3
"""
公司官網爬蟲系統
從公司官網 /team, /about 等頁面提取員工資訊
"""
import json
import sys
import re
from urllib.parse import urljoin, urlparse

def get_company_website(company_name):
    """
    搜尋公司官網
    """
    # 實際使用時呼叫 web_search
    # results = web_search(query=f"{company_name} 官網", count=3)
    
    # 從搜尋結果中找官網
    # for result in results:
    #     url = result.get('url', '')
    #     if is_company_website(url, company_name):
    #         return url
    
    return None

def is_company_website(url, company_name):
    """判斷是否為公司官網"""
    domain = urlparse(url).netloc.lower()
    company_lower = company_name.lower().replace(" ", "")
    
    # 簡單判斷：domain 包含公司名稱
    return company_lower in domain.replace("www.", "").replace("-", "").replace("_", "")

def find_team_pages(base_url):
    """
    找出公司官網中可能的團隊/關於頁面
    """
    common_paths = [
        "/team",
        "/about",
        "/about-us",
        "/people",
        "/our-team",
        "/leadership",
        "/management",
        "/staff",
        "/employees",
        "/contact",
        "/關於我們",
        "/團隊",
        "/人員"
    ]
    
    pages_to_crawl = []
    
    for path in common_paths:
        url = urljoin(base_url, path)
        pages_to_crawl.append(url)
    
    return pages_to_crawl

def extract_employee_info(page_content):
    """
    從頁面內容中提取員工資訊
    """
    employees = []
    
    # 方案 1: 正則表達式提取
    # 常見格式：
    # - 姓名 + 職位 + Email
    # - <div class="team-member">...</div>
    
    # Email 模式
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, page_content)
    
    # 電話模式
    phone_pattern = r'0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}'
    phones = re.findall(phone_pattern, page_content)
    
    # 姓名模式（中文姓名：2-4 個中文字）
    # 這個比較複雜，需要上下文判斷
    
    # 方案 2: HTML 結構化解析
    # 如果頁面有結構化的 team member 區塊
    # 可以用 BeautifulSoup 解析
    
    # 暫時返回提取到的 emails 和 phones
    for email in emails:
        employees.append({
            "email": email,
            "phone": None,
            "name": None,
            "title": None
        })
    
    return employees

def crawl_company_website(company_name, base_url=None):
    """
    爬取公司官網，提取員工資訊
    """
    print(f"🕷️  爬取公司官網：{company_name}", file=sys.stderr)
    
    # Step 1: 找到公司官網
    if not base_url:
        print(f"   🔍 搜尋官網...", file=sys.stderr)
        base_url = get_company_website(company_name)
        
        if not base_url:
            print(f"   ❌ 找不到官網", file=sys.stderr)
            return {
                "company": company_name,
                "base_url": None,
                "success": False,
                "error": "找不到官網"
            }
        
        print(f"   ✅ 官網：{base_url}", file=sys.stderr)
    
    # Step 2: 找出可能的 team/about 頁面
    print(f"   📄 尋找團隊頁面...", file=sys.stderr)
    team_pages = find_team_pages(base_url)
    
    # Step 3: 爬取每個頁面
    all_employees = []
    crawled_pages = []
    
    for page_url in team_pages:
        print(f"   🔗 {page_url}", file=sys.stderr)
        
        try:
            # 實際使用時呼叫 web_fetch
            # page_content = web_fetch(page_url)
            
            # 提取員工資訊
            # employees = extract_employee_info(page_content)
            
            # all_employees.extend(employees)
            
            crawled_pages.append({
                "url": page_url,
                "success": True,
                "employees_found": 0  # len(employees)
            })
            
        except Exception as e:
            crawled_pages.append({
                "url": page_url,
                "success": False,
                "error": str(e)
            })
    
    # 去重
    unique_employees = []
    seen_emails = set()
    
    for emp in all_employees:
        email = emp.get("email")
        if email and email not in seen_emails:
            unique_employees.append(emp)
            seen_emails.add(email)
    
    print(f"   📊 找到 {len(unique_employees)} 位員工資訊", file=sys.stderr)
    
    return {
        "company": company_name,
        "base_url": base_url,
        "success": True,
        "crawled_pages": crawled_pages,
        "employees": unique_employees,
        "total_employees": len(unique_employees)
    }

def batch_crawl_companies(companies):
    """批量爬取多家公司"""
    results = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}]", file=sys.stderr)
        
        if isinstance(company, str):
            result = crawl_company_website(company)
        elif isinstance(company, dict):
            result = crawl_company_website(
                company.get("name"),
                company.get("website")
            )
        
        results.append(result)
    
    # 統計
    success_count = sum(1 for r in results if r["success"])
    total_employees = sum(r.get("total_employees", 0) for r in results)
    
    print(f"\n📊 批量爬取完成", file=sys.stderr)
    print(f"   總計：{len(companies)} 家公司", file=sys.stderr)
    print(f"   成功：{success_count} 家（{success_count/len(companies)*100:.1f}%）", file=sys.stderr)
    print(f"   員工資訊：{total_employees} 位", file=sys.stderr)
    
    return results

if __name__ == "__main__":
    # 測試
    test_companies = [
        "台積電",
        "聯發科",
        "鴻海"
    ]
    
    if len(sys.argv) > 1:
        # 從命令列參數讀取
        test_companies = sys.argv[1:]
    
    results = batch_crawl_companies(test_companies)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))
