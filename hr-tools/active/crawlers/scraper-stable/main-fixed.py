#!/usr/bin/env python3
"""
穩定版 BD 客戶爬蟲系統 v1.1
修正：1. 正則表達式匹配 2. Sheet更新命令
"""
import json
import subprocess
import re
import time
import random
import urllib.parse
import sys
from datetime import datetime
from pathlib import Path

class StableScraper:
    def __init__(self, config_path='config.json'):
        self.base_dir = Path(__file__).parent
        self.config = self.load_config(config_path)
        self.progress = self.load_progress()
        self.log_file = self.base_dir / 'scraper.log'
        
    def load_config(self, path):
        with open(self.base_dir / path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_progress(self):
        progress_file = self.base_dir / 'progress.json'
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'processed': [],
            'failed': [],
            'success': [],
            'last_position': 0,
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'started_at': datetime.now().isoformat(),
            'last_updated': None
        }
    
    def save_progress(self):
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.base_dir / 'progress.json', 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def validate_phone(self, phone):
        if not phone or phone == '待查':
            return False
        pattern = r'0\d{1,2}-?\d{6,8}'
        return bool(re.search(pattern, phone))
    
    def validate_email(self, email):
        if not email or email == '待查':
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def search_104_company(self, company_name, retry=0):
        """在 104 搜尋公司（修正版）"""
        try:
            encoded_name = urllib.parse.quote(company_name)
            search_url = f"https://www.104.com.tw/company/search/?keyword={encoded_name}"
            
            subprocess.run(['agent-browser', 'open', search_url], 
                         timeout=15, capture_output=True, check=True)
            time.sleep(random.uniform(3, 5))
            
            result = subprocess.run(['agent-browser', 'snapshot'], 
                                  capture_output=True, text=True, timeout=10, check=True)
            
            # 修正：使用更精確的正則，排除 /search
            lines = result.stdout.split('\n')
            for line in lines:
                # 找包含 /company/ 但不包含 /search 的連結
                if '/url:' in line and '/company/' in line and '/search' not in line:
                    match = re.search(r'/url:\s*https://www\.104\.com\.tw/company/([a-z0-9]+)', line)
                    if match:
                        company_id = match.group(1)
                        return f"https://www.104.com.tw/company/{company_id}"
            
            return None
            
        except Exception as e:
            if retry < self.config['max_retries']:
                self.log(f"搜尋失敗，重試 {retry+1}/{self.config['max_retries']}: {str(e)[:50]}", 'WARN')
                time.sleep(self.config['retry_delay'])
                return self.search_104_company(company_name, retry+1)
            else:
                self.log(f"搜尋失敗，已達重試上限: {str(e)[:50]}", 'ERROR')
                return None
    
    def extract_contact(self, company_url, retry=0):
        try:
            subprocess.run(['agent-browser', 'open', company_url], 
                         timeout=15, capture_output=True, check=True)
            time.sleep(random.uniform(3, 5))
            
            result = subprocess.run(['agent-browser', 'snapshot'], 
                                  capture_output=True, text=True, timeout=10, check=True)
            lines = result.stdout.split('\n')
            
            phone = None
            email = None
            
            for i, line in enumerate(lines):
                if 'heading "電話"' in line and i+1 < len(lines):
                    match = re.search(r'paragraph:\s*(.+)', lines[i+1])
                    if match:
                        phone = match.group(1).strip()
                elif ('heading "Email"' in line or 'heading "E-mail"' in line) and i+1 < len(lines):
                    match = re.search(r'paragraph:\s*(.+)', lines[i+1])
                    if match:
                        email = match.group(1).strip()
            
            return {'phone': phone, 'email': email}
            
        except Exception as e:
            if retry < self.config['max_retries']:
                self.log(f"提取失敗，重試 {retry+1}/{self.config['max_retries']}: {str(e)[:50]}", 'WARN')
                time.sleep(self.config['retry_delay'])
                return self.extract_contact(company_url, retry+1)
            else:
                self.log(f"提取失敗，已達重試上限: {str(e)[:50]}", 'ERROR')
                return {'phone': None, 'email': None}
    
    def update_sheet(self, row, phone, email):
        """更新 Google Sheet（修正版）"""
        try:
            range_spec = f"工作表1!B{row}:C{row}"
            value = f"{phone}|{email}"
            
            # 修正：使用正確的命令格式
            result = subprocess.run([
                'gog', 'sheets', 'update',
                self.config['sheet_id'],
                range_spec,
                value,
                '--account', self.config['gog_account']
            ], capture_output=True, text=True, check=True, timeout=15)
            
            self.log(f"  Sheet更新: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"更新 Sheet 失敗 (Row {row}): {e.stderr[:100]}", 'ERROR')
            return False
        except Exception as e:
            self.log(f"更新 Sheet 失敗 (Row {row}): {str(e)[:100]}", 'ERROR')
            return False
    
    def process_company(self, company_data):
        row = company_data['row']
        name = company_data['company']
        current_phone = company_data.get('phone', '')
        current_email = company_data.get('email', '')
        
        self.log(f"處理: {name} (Row {row})")
        
        # 1. 搜尋公司
        company_url = self.search_104_company(name)
        if not company_url:
            self.log(f"  ❌ 未找到公司頁面", 'WARN')
            return False
        
        self.log(f"  ✅ 找到: {company_url}")
        
        # 2. 提取聯絡資訊
        contact = self.extract_contact(company_url)
        
        # 3. 驗證並使用現有資料補充
        phone = contact['phone'] if self.validate_phone(contact['phone']) else (current_phone if current_phone != '待查' else '待查')
        email = contact['email'] if self.validate_email(contact['email']) else (current_email if current_email != '待查' else '待查')
        
        self.log(f"  📞 電話: {phone}")
        self.log(f"  📧 Email: {email}")
        
        # 4. 更新 Sheet
        if self.update_sheet(row, phone, email):
            return True
        else:
            return False
    
    def run(self, companies):
        total = len(companies)
        self.log(f"開始處理 {total} 家公司")
        
        for i, company in enumerate(companies, 1):
            row = company['row']
            
            # 跳過已處理的
            if row in self.progress['processed']:
                self.log(f"[{i}/{total}] 跳過已處理: {company['company']}")
                continue
            
            try:
                self.log(f"[{i}/{total}] {company['company']}")
                success = self.process_company(company)
                
                # 記錄進度
                self.progress['processed'].append(row)
                self.progress['total_processed'] += 1
                
                if success:
                    self.progress['success'].append(row)
                    self.progress['total_success'] += 1
                else:
                    self.progress['failed'].append(row)
                    self.progress['total_failed'] += 1
                
                # 定期儲存進度
                if i % self.config['save_interval'] == 0:
                    self.save_progress()
                
                # 定期回報進度
                if i % self.config['batch_report_size'] == 0:
                    success_rate = self.progress['total_success'] / self.progress['total_processed'] if self.progress['total_processed'] > 0 else 0
                    report = f"📊 進度 ({i}/{total}) ✅{self.progress['total_success']} ❌{self.progress['total_failed']} 📈{success_rate:.1%}"
                    self.log(report)
                    
                    # 失敗率過高自動暫停
                    if self.progress['total_processed'] >= 5 and success_rate < (1 - self.config['auto_pause_fail_rate']):
                        msg = f"⚠️ 失敗率過高 ({(1-success_rate):.1%})，自動暫停"
                        self.log(msg, 'WARN')
                        break
                
                # 隨機延遲
                delay = random.randint(self.config['delay_min'], self.config['delay_max'])
                time.sleep(delay)
                
            except KeyboardInterrupt:
                self.log("收到中斷信號，儲存進度後退出", 'WARN')
                self.save_progress()
                sys.exit(0)
            except Exception as e:
                self.log(f"處理失敗: {str(e)[:100]}", 'ERROR')
                self.progress['failed'].append(row)
                self.progress['total_failed'] += 1
        
        # 最終報告
        self.save_progress()
        success_rate = self.progress['total_success']/self.progress['total_processed'] if self.progress['total_processed'] > 0 else 0
        final_report = f"""
✅ BD爬蟲完成
📊 總處理: {self.progress['total_processed']} / 成功: {self.progress['total_success']} / 失敗: {self.progress['total_failed']}
📈 成功率: {success_rate:.1%}
"""
        self.log(final_report)

if __name__ == '__main__':
    with open('/tmp/missing-contacts.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(companies)
    companies = companies[:limit]
    
    scraper = StableScraper()
    scraper.run(companies)
