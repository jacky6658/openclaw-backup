#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/user/clawd/hr-tools/scraper-stable')

from scraper import CompanyScraper
from utils import setup_logging
import logging

logger = setup_logging("/tmp/test.log")
scraper = CompanyScraper(logger)

# 測試第 5 行：詮欣
data = scraper.scrape_company(
    "詮欣股份有限公司",
    "https://www.104.com.tw/company/a5r2lgo",
    5
)

if data:
    print(f"爬取成功: {data}")
    success = scraper.update_google_sheets(
        5,
        data,
        "aijessie88@step1ne.com",
        "1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
    )
    print(f"更新結果: {'成功' if success else '失敗'}")
else:
    print("爬取失敗")
