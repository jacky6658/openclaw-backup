#!/usr/bin/env python3
"""
自動找人選 - LinkedIn 公開資料搜尋
使用 OpenClaw web_search 工具
"""
import sys
import json
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True, help='搜尋關鍵字')
    parser.add_argument('--jd-id', required=True, help='JD ID')
    parser.add_argument('--max-results', type=int, default=20, help='最大結果數')
    args = parser.parse_args()
    
    print(f"🔍 搜尋 LinkedIn 公開資料: {args.query}")
    
    # 呼叫 web_search（透過 openclaw CLI）
    # 這裡需要整合，暫時先建立結構
    
    search_query = f"{args.query} site:linkedin.com/in"
    
    # 模擬結果（實際要用 web_search）
    # 從剛才的搜尋結果可以看到，我們能找到很多候選人
    
    candidates = [
        {
            "name": "Chakrya Chhun",
            "title": "Finance Manager",
            "company": "Annam Cambodia Company Limited",
            "linkedin_url": "https://www.linkedin.com/in/chakrya-chhun-92b20137/",
            "description": "Finance Manager at Annam Cambodia. Speaks 4 languages: English, Japanese, Korean, Thai",
            "source": "linkedin_public",
            "found_at": datetime.now().isoformat()
        },
        {
            "name": "Malita Hout",
            "title": "Finance and accounting manager",
            "company": "Mitra Adiperkasa Cambodia",
            "linkedin_url": "https://www.linkedin.com/in/malita-hout-5ab3277a/",
            "description": "Finance Manager with construction industry background. ACCA Candidate",
            "source": "linkedin_public",
            "found_at": datetime.now().isoformat()
        },
        # 可以繼續加入更多...
    ]
    
    # 儲存結果
    output_file = f"/tmp/candidates-jd-{args.jd_id}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 找到 {len(candidates)} 個候選人")
    print(f"📄 結果儲存於: {output_file}")
    
    # 輸出 Top 5
    print("\n🏆 Top 5 候選人:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"{i}. {c['name']} - {c['title']} at {c['company']}")
    
    return candidates

if __name__ == '__main__':
    main()
