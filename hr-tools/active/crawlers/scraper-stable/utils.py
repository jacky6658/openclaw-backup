#!/usr/bin/env python3
"""
工具函數 - BD 爬蟲穩定版
"""

import re
import time
import random
import logging
from datetime import datetime
from typing import Optional

def setup_logging(log_file: str):
    """設置日誌系統"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def random_delay(min_sec: int = 8, max_sec: int = 15):
    """隨機延遲（反爬蟲）"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def extract_phone(text: str) -> Optional[str]:
    """從文字中提取電話號碼"""
    if not text:
        return None
    
    # 台灣電話格式
    patterns = [
        r'0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}',  # 02-1234-5678 或 04-2327-3199
        r'0\d{9,10}',  # 0912345678
        r'\(\d{2,3}\)\s?\d{3,4}[-\s]?\d{4}'  # (02) 1234-5678
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(0)
            # 標準化格式（移除空白和括號）
            phone = re.sub(r'[\s\(\)]', '', phone)
            # 加上連字號
            if len(phone) == 10 and phone.startswith('0'):
                if phone[1] in ['2', '3', '4', '5', '6', '7', '8']:
                    # 市話：02-1234-5678
                    return f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"
                else:
                    # 手機：0912-345-678
                    return f"{phone[:4]}-{phone[4:7]}-{phone[7:]}"
            return phone
    
    return None

def extract_email(text: str) -> Optional[str]:
    """從文字中提取 Email"""
    if not text:
        return None
    
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    if match:
        return match.group(0).lower()
    
    return None

def extract_website(text: str) -> Optional[str]:
    """從文字中提取公司官網（排除 104 的連結）"""
    if not text:
        return None
    
    # 1. 優先尋找「公司網址」或「官網」關鍵字後面的網址
    keyword_patterns = [
        r'(?:公司網址|官網|網址|Website|官方網站)[:：\s]+([^\s\n\)]+)',
    ]
    
    for pattern in keyword_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(1)
            # 清理網址
            url = url.strip('.,;、。，；\'")')
            # 排除 104 的連結
            if '104.com.tw' in url:
                continue
            # 確保有協議
            if not url.startswith('http'):
                url = 'https://' + url
            return url
    
    # 2. 找所有 http 開頭的連結，排除 104
    all_urls = re.findall(r'https?://[^\s\n\)]+', text)
    for url in all_urls:
        url = url.strip('.,;、。，；\'")')
        # 排除 104 的連結
        if '104.com.tw' not in url:
            return url
    
    # 3. 找 www. 開頭的連結
    www_match = re.search(r'(www\.[^\s\n\)]+)', text)
    if www_match:
        url = www_match.group(1).strip('.,;、。，；\'")')
        if '104.com.tw' not in url:
            if not url.startswith('http'):
                url = 'https://' + url
            return url
    
    return None

def parse_104_snapshot(snapshot_text: str) -> dict:
    """解析 104 公司頁面 snapshot"""
    data = {
        'phone': None,
        'email': None,
        'website': None,
        'address': None,
        'industry': None,
        'services': None
    }
    
    if not snapshot_text:
        return data
    
    # 提取電話
    data['phone'] = extract_phone(snapshot_text)
    
    # 提取 Email
    data['email'] = extract_email(snapshot_text)
    
    # 提取網址（特殊處理：找「公司網址」heading 後的 /url:）
    website_pattern = r'heading "公司網址".*?/url:\s*([^\s\n]+)'
    match = re.search(website_pattern, snapshot_text, re.DOTALL)
    if match:
        url = match.group(1).strip()
        if '104.com.tw' not in url:
            data['website'] = url
    
    # 如果沒找到，用通用方法
    if not data['website']:
        data['website'] = extract_website(snapshot_text)
    
    # 提取地址（尋找「地址」「位置」關鍵字）
    address_pattern = r'(?:地址|位置|Address)[:：\s]+([^\n]{10,100})'
    match = re.search(address_pattern, snapshot_text)
    if match:
        data['address'] = match.group(1).strip()
    
    # 提取產業類別（尋找「產業類別」關鍵字）
    industry_pattern = r'(?:產業類別|產業|Industry)[:：\s]+([^\n]{5,50})'
    match = re.search(industry_pattern, snapshot_text)
    if match:
        data['industry'] = match.group(1).strip()
    
    # 提取服務項目（尋找「主要商品/服務」關鍵字）
    services_pattern = r'(?:主要商品|服務項目|Products|Services)[:：\s]+([^\n]{10,200})'
    match = re.search(services_pattern, snapshot_text)
    if match:
        data['services'] = match.group(1).strip()
    
    return data

def format_timestamp() -> str:
    """格式化時間戳"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def sanitize_text(text: Optional[str]) -> str:
    """清理文字（移除特殊字元）"""
    if not text:
        return ""
    
    # 移除多餘空白
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text
