#!/usr/bin/env python3
"""
配置文件 - BD 爬蟲穩定版
"""

import os

# Google Sheets 配置
SHEET_ID = "1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT = "aijessie88@step1ne.com"

# 爬蟲配置
DELAY_MIN = 8  # 最小延遲（秒）
DELAY_MAX = 15  # 最大延遲（秒）
RETRY_TIMES = 3  # 重試次數
RETRY_DELAY = 5  # 重試延遲（秒）

# 進度報告配置
REPORT_INTERVAL = 5  # 每處理 5 家公司報告一次
CHECKPOINT_INTERVAL = 5  # 每處理 5 家公司保存一次 checkpoint

# 檔案路徑
CHECKPOINT_FILE = "/Users/user/clawd/hr-tools/scraper-stable/checkpoint.json"
LOG_FILE = "/Users/user/clawd/hr-tools/scraper-stable/scraper.log"
PROGRESS_FILE = "/Users/user/clawd/hr-tools/scraper-stable/progress.json"

# Agent Browser 配置
AGENT_BROWSER_CMD = "agent-browser"

# 欄位配置（Google Sheets 欄位對應）
COLUMNS = {
    "company_name": "A",      # 公司名稱
    "phone": "B",             # 聯絡電話
    "email": "C",             # Email
    "website": "D",           # 公司官網
    "company_104": "E",       # 104公司頁面
    "address": "F",           # 公司地址/區域
    "industry": "G",          # 產業類別
    "services": "H",          # 服務項目
    "status": "I",            # 狀態
    "date": "J",              # 開發日期
    "consultant": "K",        # 負責顧問
    "dev_status": "L",        # 開發狀況
    "job_assist": "M"         # 協助職缺
}
