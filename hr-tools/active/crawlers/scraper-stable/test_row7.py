#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/user/clawd/hr-tools/scraper-stable')

from scraper import CompanyScraper
from utils import setup_logging
import logging

logger = setup_logging("/tmp/test.log")
scraper = CompanyScraper(logger)

# 測試第 7 行：怡利電子
data = scraper.scrape_company(
    "怡利電子工業股份有限公司",
    "https://www.104.com.tw/company/r9abrr4",
    7
)

if data:
    print(f"\n✅ 爬取成功：")
    print(f"  電話: {data.get('phone')}")
    print(f"  Email: {data.get('email')}")
    print(f"  官網: {data.get('website')}")  
    print(f"  地址: {data.get('address')}")
    print(f"  產業: {data.get('industry')}")
    print(f"  服務: {data.get('services')}")
else:
    print("❌ 爬取失敗")
