#!/usr/bin/env python3
"""從 104 公司頁面抓取官網"""

import subprocess
import json
import sys
import time

SHEET_ID = "1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT = "aijessie88@step1ne.com"

def run(cmd):
    """執行指令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_sheet_data():
    """讀取 Sheet 資料"""
    cmd = f'gog sheets get {SHEET_ID} "A2:F17" --account {ACCOUNT} --json'
    output = run(cmd)
    data = json.loads(output)
    return data.get('values', [])

def update_cell(row, col, value):
    """更新單一儲存格"""
    cmd = f'gog sheets update {SHEET_ID} "{col}{row}" "{value}" --account {ACCOUNT}'
    run(cmd)

def fetch_website(company_name, existing_104_url=None):
    """從 104 抓取公司官網"""
    
    # 如果已有 104 公司頁面連結，直接使用
    if existing_104_url and existing_104_url.startswith('https://www.104.com.tw/company/'):
        company_url = existing_104_url
        print(f"  → 使用現有連結")
    else:
        # 搜尋公司
        print(f"  → 搜尋中...")
        run(f'agent-browser open "https://www.104.com.tw/company/search/?keyword={company_name}"')
        run('agent-browser wait --load networkidle --timeout 10000')
        
        # 找公司連結
        js = f"""
            Array.from(document.querySelectorAll('a[href*="/company/"]'))
                .find(a => a.textContent.includes('{company_name}'))?.href || null
        """
        company_url = run(f"agent-browser eval '{js}'").strip('"')
        
        if not company_url or company_url == 'null':
            return "找不到公司"
    
    # 進入公司頁面
    run(f'agent-browser open "{company_url}"')
    run('agent-browser wait --load networkidle --timeout 10000')
    
    # 抓取公司網址
    js = """
        (function() {
            const rows = Array.from(document.querySelectorAll('tr, div'));
            for (const row of rows) {
                const text = row.textContent;
                if (text.includes('公司網址') || text.includes('公司網站')) {
                    const link = row.querySelector('a[href^="http"]');
                    if (link) return link.href;
                }
            }
            return null;
        })()
    """
    website = run(f"agent-browser eval '{js}'").strip('"')
    
    if not website or website == 'null':
        return "暫不提供"
    
    return website

def main():
    print("開始抓取 104 公司官網...")
    
    rows = get_sheet_data()
    
    for idx, row_data in enumerate(rows, start=2):
        company = row_data[0] if len(row_data) > 0 else ""
        existing_url = row_data[4] if len(row_data) > 4 else ""
        
        if not company:
            continue
        
        print(f"\n[{idx}] {company}")
        
        try:
            website = fetch_website(company, existing_url)
            print(f"  ✓ {website}")
            
            # 更新到 Sheet
            update_cell(idx, "D", website)
            
        except Exception as e:
            print(f"  ✗ 錯誤: {e}")
            update_cell(idx, "D", "錯誤")
        
        time.sleep(2)
    
    run('agent-browser close')
    print("\n✅ 完成")

if __name__ == "__main__":
    main()
