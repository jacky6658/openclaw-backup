# 🛡️ 反爬蟲 & 人類行為模擬策略

**版本**: v1.0  
**更新**: 2026-02-27  
**應用範圍**: GitHub API + Google Web Search

---

## 📊 反爬蟲分層策略

### Level 1：隨機延遲 ⭐⭐⭐⭐⭐
**最重要的防禦機制**

```python
import random
import time

class HumanBehavior:
    """模擬人類操作的隨機延遲"""
    
    @staticmethod
    def think_pause():
        """思考延遲（1-3秒）"""
        time.sleep(random.uniform(1, 3))
    
    @staticmethod
    def read_pause():
        """閱讀延遲（0.5-2秒）"""
        time.sleep(random.uniform(0.5, 2))
    
    @staticmethod
    def action_pause():
        """操作延遲（0.2-1秒）"""
        time.sleep(random.uniform(0.2, 1))
    
    @staticmethod
    def request_pause():
        """API 請求間隔（2-5秒）"""
        time.sleep(random.uniform(2, 5))
    
    @staticmethod
    def batch_pause():
        """批次間隔（10-15秒）"""
        time.sleep(random.uniform(10, 15))
```

**應用場景**：
```
GitHub 搜尋：
  搜尋查詢 → think_pause() → 等待 2 秒 → 解析結果 → read_pause() → 2 秒
  
  每個候選人詳情：
    訪問 profile → request_pause() → 5 秒 → 提取信息 → read_pause() → 2 秒
  
  每批 5 人：
    完成 5 人 → batch_pause() → 12 秒 → 開始下一批
```

---

### Level 2：User-Agent 輪換
**欺騙伺服器，看起來是不同使用者**

```python
class UserAgentRotator:
    """User-Agent 輪換"""
    
    DESKTOP_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    @staticmethod
    def get_random_agent():
        """隨機選擇 User-Agent"""
        return random.choice(UserAgentRotator.DESKTOP_AGENTS)
```

**應用**：
```python
headers = {
    'User-Agent': UserAgentRotator.get_random_agent(),
    'Accept': 'application/json',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
}
```

---

### Level 3：請求頻率控制
**避免在短時間內發送過多請求**

```python
class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_minute=30):
        self.rpm = requests_per_minute
        self.request_times = []
    
    def wait_if_needed(self):
        """如果超過速率，等待"""
        now = time.time()
        # 移除 1 分鐘外的舊請求
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rpm:
            # 計算要等待的時間
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                print(f"⏳ 速率限制：等待 {wait_time:.1f} 秒")
                time.sleep(wait_time)
        
        self.request_times.append(time.time())
```

**配置**：
```
GitHub API：60 requests/hour 免認證（推薦用 token 提升到 5000）
Google Web Search：每分鐘 30 次（安全上限）
```

---

### Level 4：批次分散
**不要在短時間內爬完所有人選**

```python
class BatchDispatcher:
    """批次分散爬蟲"""
    
    def process_candidates(self, candidates, batch_size=5):
        """
        按批次處理，每批間隔較長
        
        例：40 人 → 8 批 × 5 人
        批 1 (5人) → 等待 12 秒 → 批 2 (5人) → 等待 12 秒 → ...
        """
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i+batch_size]
            
            print(f"[批次 {i//batch_size + 1}] 正在處理 {len(batch)} 人...")
            
            for candidate in batch:
                self.process_single(candidate)
                HumanBehavior.request_pause()  # 每人間隔 2-5 秒
            
            # 批次間隔
            if i + batch_size < len(candidates):
                print(f"⏸️ 批次休息，12 秒後繼續...")
                HumanBehavior.batch_pause()
```

---

### Level 5：錯誤重試 + 退避策略
**遇到 429/403 時自動退退**

```python
class SmartRetry:
    """智慧重試機制"""
    
    @staticmethod
    def exponential_backoff(attempt, base_delay=5):
        """指數退避：5s → 10s → 20s → 40s"""
        delay = base_delay * (2 ** attempt)
        return min(delay, 300)  # 最多等 5 分鐘
    
    @staticmethod
    def retry_with_backoff(func, max_attempts=3):
        """帶退避的重試"""
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt < max_attempts - 1:
                    wait = SmartRetry.exponential_backoff(attempt)
                    print(f"❌ 失敗：{e}")
                    print(f"⏳ {wait} 秒後重試... (嘗試 {attempt+2}/{max_attempts})")
                    time.sleep(wait)
                else:
                    raise
```

---

### Level 6：Session 管理
**保持連接活躍，避免被強制中斷**

```python
class SessionManager:
    """Session 管理"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': UserAgentRotator.get_random_agent(),
            'Accept-Encoding': 'gzip, deflate',
        })
    
    def get(self, url, timeout=10):
        """帶超時的 GET 請求"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            print("⚠️ 請求超時，可能被限流")
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("🚫 429 Too Many Requests，降速...")
                raise
            raise
```

---

## 🎭 人類行為模擬細節

### 1. 滾動頁面（模擬閱讀）
```python
def human_scroll_pattern(pages=3):
    """
    模擬人類滾動頁面的行為
    - 不是一次性滾到底
    - 隨機停留閱讀
    """
    for page in range(pages):
        # 向下滾動
        scroll_distance = random.randint(300, 800)
        time.sleep(random.uniform(0.5, 1.5))  # 滾動時間
        
        # 停留閱讀
        pause_duration = random.uniform(1, 3)
        print(f"  📖 閱讀 {pause_duration:.1f} 秒...")
        time.sleep(pause_duration)
```

### 2. 選擇性點擊（不是一直點）
```python
def human_click_pattern(total_items=20, click_ratio=0.7):
    """
    人類不會點所有項目
    只會點擊其中 70% 的結果來檢查
    """
    to_click = random.sample(range(total_items), int(total_items * click_ratio))
    
    for idx in to_click:
        print(f"  👆 點擊項目 {idx+1}...")
        time.sleep(random.uniform(0.5, 1))  # 點擊動作
        # 檢查內容
        time.sleep(random.uniform(2, 4))  # 閱讀時間
```

### 3. 隨機搜尋詞組合
```python
def generate_search_variations(base_keywords):
    """
    不同搜尋請求用不同詞序
    避免每次搜尋都完全相同
    """
    variations = [
        " ".join(base_keywords),
        " ".join(reversed(base_keywords)),
        " OR ".join(base_keywords),
        f'"{" ".join(base_keywords)}"',  # 精確搜尋
    ]
    return random.choice(variations)
```

---

## 📊 監控 & 日誌

### 每次爬蟲的詳細日誌
```python
class CrawlLogger:
    """爬蟲日誌記錄"""
    
    def __init__(self, job_title):
        self.job_title = job_title
        self.start_time = time.time()
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'rate_limited': 0,
            'total_duration': 0,
        }
    
    def log_event(self, event_type, message):
        """記錄事件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{event_type}] {message}")
    
    def generate_report(self):
        """生成報告"""
        self.stats['total_duration'] = time.time() - self.start_time
        
        report = f"""
        📊 爬蟲報告 - {self.job_title}
        ────────────────────
        總耗時：{self.stats['total_duration']:.1f} 秒
        總請求：{self.stats['total_requests']}
        成功：{self.stats['successful']}
        失敗：{self.stats['failed']}
        限流：{self.stats['rate_limited']}
        成功率：{self.stats['successful']/max(1, self.stats['total_requests'])*100:.1f}%
        """
        return report
```

---

## 🚨 被限流時的應對方案

| 情況 | 反應 | 應對 |
|------|------|------|
| **429 Too Many Requests** | 短期限流 | 等待 5-10 分鐘後重試 |
| **403 Forbidden** | IP 被封 | 更換 IP 或隔天重試 |
| **Timeout（10+ 秒）** | 可能被限流 | 增加延遲，降低批次大小 |
| **異常 HTTP Headers** | 可能被檢測 | 隨機 User-Agent，更新 headers |
| **持續失敗** | 高風險 | 暫停 24 小時，或改用 Proxy |

---

## 📋 速度 vs 安全權衡

### 保守方案（優先穩定）⭐⭐⭐⭐⭐
```
單人間隔：5 秒
批次間隔：15 秒
每小時最多：30 人
風險：很低
```

### 平衡方案（推薦） ⭐⭐⭐⭐
```
單人間隔：2-3 秒
批次間隔：10-12 秒
每小時最多：60 人
風險：低
耗時：快
```

### 激進方案（高風險）⭐⭐
```
單人間隔：0.5-1 秒
批次間隔：5 秒
每小時最多：150+ 人
風險：高（容易被限流）
適用：只做一次性爬蟲
```

**建議使用：平衡方案**

---

## ✅ 檢查清單

爬蟲執行前確認：

- [ ] User-Agent 已隨機化
- [ ] 延遲參數已設置（2-5 秒）
- [ ] 批次大小設為 5-10 人
- [ ] 重試機制已啟用
- [ ] 日誌記錄已開啟
- [ ] 速率限制器已啟動
- [ ] Timeout 設為 10-15 秒
- [ ] Session 已初始化

爬蟲執行中監控：

- [ ] 無 429 錯誤
- [ ] 無 403 錯誤
- [ ] 平均響應時間 < 5 秒
- [ ] 成功率 > 95%

爬蟲完成後檢查：

- [ ] 所有日誌已記錄
- [ ] 成功率報告已生成
- [ ] 候選人資料完整
