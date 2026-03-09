#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
人類行為模擬 & 反爬蟲工具
版本：v1.0
"""

import time
import random
import requests
from datetime import datetime
from typing import Callable


class HumanBehavior:
    """模擬人類操作的延遲"""
    
    @staticmethod
    def think_pause(min_sec=1, max_sec=3):
        """思考延遲（1-3 秒）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def read_pause(min_sec=0.5, max_sec=2):
        """閱讀延遲（0.5-2 秒）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def action_pause(min_sec=0.2, max_sec=1):
        """操作延遲（0.2-1 秒）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def request_pause(min_sec=2, max_sec=5):
        """API 請求間隔（2-5 秒）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def batch_pause(min_sec=10, max_sec=15):
        """批次間隔（10-15 秒）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def custom_pause(min_sec=1, max_sec=3):
        """自訂延遲"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay


class UserAgentRotator:
    """User-Agent 輪換"""
    
    DESKTOP_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    @staticmethod
    def get_random_agent():
        """隨機選擇 User-Agent"""
        return random.choice(UserAgentRotator.DESKTOP_AGENTS)
    
    @staticmethod
    def get_headers():
        """獲取隨機 headers"""
        return {
            'User-Agent': UserAgentRotator.get_random_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_minute=30):
        """
        初始化
        
        Args:
            requests_per_minute: 每分鐘最多請求數
        """
        self.rpm = requests_per_minute
        self.request_times = []
    
    def wait_if_needed(self):
        """如果超過速率，等待"""
        now = time.time()
        
        # 移除 1 分鐘外的舊請求
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rpm:
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request)
            
            if wait_time > 0:
                print(f"⏳ 速率限制：等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
            
            self.request_times.pop(0)
        
        self.request_times.append(time.time())
    
    def get_requests_this_minute(self):
        """獲取本分鐘已請求數"""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        return len(self.request_times)


class SessionManager:
    """Session 管理"""
    
    def __init__(self, timeout=10, max_retries=3):
        """
        初始化
        
        Args:
            timeout: 請求超時（秒）
            max_retries: 最大重試次數
        """
        self.session = requests.Session()
        self.session.headers.update(UserAgentRotator.get_headers())
        self.timeout = timeout
        self.max_retries = max_retries
    
    def get(self, url, **kwargs):
        """帶超時的 GET 請求"""
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            print("⚠️ 請求超時")
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("🚫 429 Too Many Requests，速率限制已啟用")
            raise
    
    def close(self):
        """關閉 session"""
        self.session.close()


class SmartRetry:
    """智慧重試機制"""
    
    @staticmethod
    def exponential_backoff(attempt, base_delay=5, max_delay=300):
        """指數退避：5s → 10s → 20s → 40s"""
        delay = base_delay * (2 ** attempt)
        return min(delay, max_delay)
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_attempts=3, description=""):
        """帶退避的重試"""
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt < max_attempts - 1:
                    wait = SmartRetry.exponential_backoff(attempt)
                    print(f"❌ {description} 失敗：{str(e)[:50]}")
                    print(f"⏳ {wait:.0f} 秒後重試... (嘗試 {attempt+2}/{max_attempts})")
                    time.sleep(wait)
                else:
                    print(f"🚨 {description} 最終失敗")
                    raise


class BatchDispatcher:
    """批次分散爬蟲"""
    
    def __init__(self, batch_size=5, batch_delay_min=10, batch_delay_max=15):
        """
        初始化
        
        Args:
            batch_size: 每批大小
            batch_delay_min: 批次最小延遲（秒）
            batch_delay_max: 批次最大延遲（秒）
        """
        self.batch_size = batch_size
        self.batch_delay_min = batch_delay_min
        self.batch_delay_max = batch_delay_max
    
    def process_with_batches(self, items, process_func, item_delay_min=2, item_delay_max=5):
        """
        按批次處理項目
        
        Args:
            items: 項目列表
            process_func: 處理函數 (item) -> result
            item_delay_min: 項目間延遲最小值
            item_delay_max: 項目間延遲最大值
        
        Returns:
            結果列表
        """
        results = []
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min((batch_idx + 1) * self.batch_size, len(items))
            batch = items[start_idx:end_idx]
            
            print(f"\n📦 [批次 {batch_idx+1}/{total_batches}] 正在處理 {len(batch)} 項...")
            
            for item_idx, item in enumerate(batch):
                try:
                    result = process_func(item)
                    results.append(result)
                    print(f"  ✅ [{batch_idx+1}.{item_idx+1}] 完成")
                    
                    # 項目間延遲
                    if item_idx < len(batch) - 1:
                        delay = HumanBehavior.custom_pause(item_delay_min, item_delay_max)
                except Exception as e:
                    print(f"  ❌ [{batch_idx+1}.{item_idx+1}] 失敗：{str(e)[:50]}")
                    results.append(None)
            
            # 批次間延遲
            if batch_idx < total_batches - 1:
                delay = HumanBehavior.batch_pause(self.batch_delay_min, self.batch_delay_max)
                print(f"⏸️ 批次休息 {delay:.0f} 秒...")
        
        return results


class CrawlLogger:
    """爬蟲日誌記錄"""
    
    def __init__(self, job_title):
        """初始化"""
        self.job_title = job_title
        self.start_time = time.time()
        self.events = []
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'rate_limited': 0,
            'total_duration': 0,
        }
    
    def log_event(self, event_type, message):
        """記錄事件"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message,
        }
        self.events.append(log_entry)
        
        # 即時輸出
        if event_type == "error":
            icon = "❌"
        elif event_type == "warning":
            icon = "⚠️"
        elif event_type == "success":
            icon = "✅"
        else:
            icon = "📌"
        
        print(f"[{timestamp}] {icon} {message}")
    
    def log_request(self, success=True, rate_limited=False):
        """記錄請求"""
        self.stats['total_requests'] += 1
        if success:
            self.stats['successful'] += 1
        else:
            self.stats['failed'] += 1
        if rate_limited:
            self.stats['rate_limited'] += 1
    
    def generate_report(self):
        """生成報告"""
        self.stats['total_duration'] = time.time() - self.start_time
        
        success_rate = (
            self.stats['successful'] / max(1, self.stats['total_requests']) * 100
        ) if self.stats['total_requests'] > 0 else 0
        
        report = {
            'job_title': self.job_title,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_duration_sec': self.stats['total_duration'],
            'stats': self.stats,
            'success_rate': f"{success_rate:.1f}%",
            'events': self.events,
        }
        
        return report


# 使用範例
if __name__ == "__main__":
    print("🧪 人類行為模擬測試")
    
    # 測試延遲
    print("\n1. 測試延遲...")
    print(f"  思考延遲: {HumanBehavior.think_pause():.2f}s")
    print(f"  閱讀延遲: {HumanBehavior.read_pause():.2f}s")
    print(f"  請求延遲: {HumanBehavior.request_pause():.2f}s")
    
    # 測試 User-Agent
    print("\n2. 測試 User-Agent...")
    print(f"  隨機 UA: {UserAgentRotator.get_random_agent()[:50]}...")
    
    # 測試速率限制
    print("\n3. 測試速率限制...")
    limiter = RateLimiter(requests_per_minute=5)
    for i in range(7):
        limiter.wait_if_needed()
        print(f"  請求 {i+1}/{7}")
    
    print("\n✅ 測試完成")
