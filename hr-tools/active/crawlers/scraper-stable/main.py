#!/usr/bin/env python3
"""
BD 爬蟲主程式 - 穩定版
處理 302 家公司的聯絡資訊補充

使用方法:
    python3 main.py              # 繼續上次進度
    python3 main.py --reset      # 重新開始
    python3 main.py --test 5     # 測試模式（只處理 5 家）
"""

import sys
import argparse
import subprocess
import logging
import re
from typing import Optional
from config import *
from utils import setup_logging
from checkpoint import CheckpointManager
from reporter import ProgressReporter
from scraper import CompanyScraper

def get_companies_from_sheets(sheet_id: str, account: str, start_row: int = 2, limit: Optional[int] = None):
    """從 Google Sheets 獲取公司清單"""
    logger = logging.getLogger(__name__)
    logger.info("正在從 Google Sheets 獲取公司清單...")
    
    try:
        # 獲取所有公司數據（A, E 欄：公司名稱、104公司頁面）
        end_row = start_row + limit - 1 if limit else 250
        range_str = f"A{start_row}:E{end_row}"
        
        cmd = f"gog sheets get {sheet_id} '{range_str}' --account {account} --json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            logger.error(f"獲取 Google Sheets 失敗: {result.stderr}")
            return []
        
        # 解析 JSON 數據
        import json
        data = json.loads(result.stdout)
        rows = data.get('values', [])
        
        companies = []
        for idx, row in enumerate(rows):
            # 確保有足夠的欄位
            while len(row) < 5:
                row.append("")
            
            company_name = row[0].strip() if len(row) > 0 else ""
            phone = row[1].strip() if len(row) > 1 else ""
            email = row[2].strip() if len(row) > 2 else ""
            website = row[3].strip() if len(row) > 3 else ""
            company_104 = row[4].strip() if len(row) > 4 else ""
            
            if not company_name:
                logger.warning(f"第 {start_row + idx} 行缺少公司名稱，跳過")
                continue
            
            if not company_104 or not company_104.startswith('http'):
                logger.warning(f"第 {start_row + idx} 行缺少有效的104連結，跳過")
                continue
            
            # 如果電話或Email是「待查」或為空，才需要爬取
            needs_phone = not phone or phone == "待查"
            needs_email = not email or email == "待查"
            
            if needs_phone or needs_email:
                companies.append({
                    'row': start_row + idx,
                    'name': company_name,
                    '104_url': company_104,
                    'needs_phone': needs_phone,
                    'needs_email': needs_email
                })
        
        logger.info(f"找到 {len(companies)} 家需要處理的公司")
        return companies
        
    except Exception as e:
        logger.error(f"獲取公司清單失敗: {str(e)}")
        return []

def main():
    """主程式"""
    # 解析命令列參數
    parser = argparse.ArgumentParser(description='BD 爬蟲穩定版')
    parser.add_argument('--reset', action='store_true', help='重新開始（清除 checkpoint）')
    parser.add_argument('--test', type=int, metavar='N', help='測試模式（只處理 N 家公司）')
    args = parser.parse_args()
    
    # 設置日誌
    logger = setup_logging(LOG_FILE)
    logger.info("="*60)
    logger.info("BD 爬蟲啟動 - 穩定版")
    logger.info("="*60)
    
    # 初始化模組
    checkpoint = CheckpointManager(CHECKPOINT_FILE)
    reporter = ProgressReporter(PROGRESS_FILE)
    scraper = CompanyScraper(logger, RETRY_TIMES, RETRY_DELAY)
    
    # 重置 checkpoint（如果需要）
    if args.reset:
        logger.info("重置 checkpoint...")
        checkpoint.reset()
    
    # 獲取起始行號
    start_row = checkpoint.get_last_row() + 1 if checkpoint.get_last_row() > 1 else 2
    logger.info(f"從第 {start_row} 行開始處理")
    
    # 獲取公司清單
    companies = get_companies_from_sheets(
        SHEET_ID, 
        ACCOUNT, 
        start_row=start_row,
        limit=args.test if args.test else None
    )
    
    if not companies:
        logger.info("沒有需要處理的公司")
        return
    
    logger.info(f"準備處理 {len(companies)} 家公司")
    
    # 處理每家公司
    for idx, company in enumerate(companies, 1):
        try:
            logger.info(f"\n--- 處理進度: {idx}/{len(companies)} ---")
            
            # 爬取公司資料
            data = scraper.scrape_company(
                company['name'], 
                company['104_url'],
                company['row']
            )
            
            if data:
                # 更新 Google Sheets
                success = scraper.update_google_sheets(
                    company['row'],
                    data,
                    ACCOUNT,
                    SHEET_ID
                )
                
                # 更新 checkpoint
                checkpoint.update_progress(
                    company['row'],
                    company['name'],
                    success,
                    data
                )
            else:
                logger.error(f"爬取失敗: {company['name']}")
                checkpoint.update_progress(
                    company['row'],
                    company['name'],
                    False
                )
            
            # 定期保存 checkpoint 和報告進度
            if checkpoint.should_save(CHECKPOINT_INTERVAL):
                checkpoint.save()
                reporter.report(checkpoint.data, f"進度更新 ({idx}/{len(companies)})")
            
        except KeyboardInterrupt:
            logger.info("\n用戶中斷，保存進度...")
            checkpoint.save()
            reporter.report(checkpoint.data, "程式中斷")
            sys.exit(0)
        
        except Exception as e:
            logger.error(f"處理出錯: {company['name']} - {str(e)}")
            checkpoint.update_progress(
                company['row'],
                company['name'],
                False
            )
    
    # 最終保存和報告
    checkpoint.save()
    reporter.report_final(checkpoint.data)
    
    # 顯示失敗清單
    failed = checkpoint.get_failed_companies()
    if failed:
        logger.info("\n失敗清單:")
        for item in failed:
            logger.info(f"  第 {item['row']} 行: {item['name']}")

if __name__ == "__main__":
    main()
