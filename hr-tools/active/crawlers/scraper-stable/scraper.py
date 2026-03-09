#!/usr/bin/env python3
"""
核心爬蟲邏輯 - BD 爬蟲穩定版
"""

import subprocess
import logging
import time
from typing import Optional, Dict
from utils import random_delay, parse_104_snapshot
from validator import DataValidator

class CompanyScraper:
    """公司資料爬蟲"""
    
    def __init__(self, logger: logging.Logger, retry_times: int = 3, retry_delay: int = 5):
        self.logger = logger
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.validator = DataValidator()
    
    def scrape_company(self, company_name: str, company_104_url: str, row: int) -> Optional[Dict]:
        """爬取單一公司資料（帶重試機制）"""
        self.logger.info(f"開始處理第 {row} 行: {company_name}")
        
        for attempt in range(1, self.retry_times + 1):
            try:
                # 訪問 104 公司頁面
                snapshot = self._fetch_104_page(company_104_url)
                
                if not snapshot:
                    self.logger.warning(f"第 {attempt}/{self.retry_times} 次嘗試失敗: 無法獲取頁面內容")
                    if attempt < self.retry_times:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
                # 解析數據
                data = parse_104_snapshot(snapshot)
                
                # 驗證數據品質
                validation = self.validator.validate_company_data(data)
                quality_score = self.validator.get_quality_score(validation)
                
                # 記錄結果
                summary = self.validator.get_data_summary(data)
                self.logger.info(f"成功: {company_name} - {summary}")
                
                # 即使數據不完整也返回（部分數據比沒有數據好）
                return data
                
            except Exception as e:
                self.logger.error(f"第 {attempt}/{self.retry_times} 次嘗試出錯: {company_name} - {str(e)}")
                if attempt < self.retry_times:
                    time.sleep(self.retry_delay)
                else:
                    return None
        
        return None
    
    def _fetch_104_page(self, url: str) -> Optional[str]:
        """使用 agent-browser 訪問 104 頁面並獲取 snapshot"""
        try:
            # 使用 agent-browser snapshot 命令
            cmd = f"agent-browser snapshot '{url}'"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"agent-browser 失敗: {result.stderr}")
                return None
            
            # 獲取輸出內容
            snapshot_text = result.stdout
            
            if not snapshot_text or len(snapshot_text) < 100:
                self.logger.warning(f"Snapshot 內容太短: {len(snapshot_text)} 字元")
                return None
            
            # 隨機延遲（反爬蟲）
            delay = random_delay()
            self.logger.debug(f"延遲 {delay:.1f} 秒")
            
            return snapshot_text
            
        except subprocess.TimeoutExpired:
            self.logger.error("agent-browser 超時（60秒）")
            return None
        except Exception as e:
            self.logger.error(f"訪問頁面失敗: {str(e)}")
            return None
    
    def update_google_sheets(self, row: int, data: Dict[str, Optional[str]], account: str, sheet_id: str) -> bool:
        """更新 Google Sheets（聯絡資訊 + 自動填寫狀態/日期/負責人）"""
        try:
            from datetime import datetime
            updates = []
            
            # 1. 聯絡資訊欄位（爬取的數據）
            if data.get('phone'):
                updates.append(('B', data['phone']))
            if data.get('email'):
                updates.append(('C', data['email']))
            if data.get('website'):
                updates.append(('D', data['website']))
            if data.get('address'):
                updates.append(('F', data['address']))
            if data.get('industry'):
                updates.append(('G', data['industry']))
            if data.get('services'):
                updates.append(('H', data['services']))
            
            # 2. 自動填寫：狀態（I欄）
            has_contact = bool(data.get('phone') or data.get('email'))
            status = "待聯繫" if has_contact else "待查"
            updates.append(('I', status))
            
            # 3. 自動填寫：開發日期（J欄）
            today = datetime.now().strftime('%Y-%m-%d')
            updates.append(('J', today))
            
            # 4. 自動填寫：負責顧問（K欄）
            # 預設為 Jacky，之後可根據規則調整
            updates.append(('K', 'Jacky'))
            
            if not updates:
                self.logger.info(f"第 {row} 行: 沒有可更新的數據")
                return True
            
            # 批量更新（使用 JSON 格式）
            import json
            for column, value in updates:
                cell = f"{column}{row}"
                # 構造正確的 JSON 格式：[[value]]
                values_json = json.dumps([[value]])
                cmd = f"gog sheets update {sheet_id} '{cell}' --values-json '{values_json}' --account {account}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.logger.error(f"更新 {cell} 失敗: {result.stderr}")
                    return False
                
                self.logger.debug(f"成功更新 {cell}: {value[:50]}...")
                
                # 小延遲（避免 API rate limit）
                time.sleep(0.5)
            
            self.logger.info(f"第 {row} 行: 成功更新 {len(updates)} 個欄位")
            return True
            
        except Exception as e:
            self.logger.error(f"更新 Google Sheets 失敗: {str(e)}")
            return False
