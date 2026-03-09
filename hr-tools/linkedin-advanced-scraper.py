#!/usr/bin/env python3
"""
LinkedIn 進階爬蟲 v1 - 對抗反爬蟲機制
整合：User-Agent 輪換 + 隨機延遲 + Session 管理 + Selenium 動態渲染

⚠️ 僅供學習使用，使用者承擔違反 ToS 的風險
請遵守當地法律 & LinkedIn 服務條款
"""

import time
import random
import json
import os
import sys
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import urllib.parse

# 第三方庫
try:
    import requests
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    print("❌ 缺少依賴，請安裝：pip install requests selenium")
    sys.exit(1)

# ==================== 日誌設定 ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 反爬蟲配置 ====================

# 1️⃣ User-Agent 池（模擬不同瀏覽器）
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# 2️⃣ 延遲設定
DELAY_MIN = 3  # 最小延遲（秒）
DELAY_MAX = 8  # 最大延遲（秒）

# 3️⃣ Selenium 選項
CHROME_OPTIONS = [
    '--disable-blink-features=AutomationControlled',  # 反指紋識別
    '--disable-extensions',
    '--disable-plugins',
    '--no-default-browser-check',
    '--no-first-run',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--headless=new',  # 無頭模式（新版 Chrome）
]

# ==================== 爬蟲核心類 ====================

class LinkedInAdvancedScraper:
    """LinkedIn 進階爬蟲"""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        初始化爬蟲
        
        Args:
            email: LinkedIn 登錄郵箱（可選）
            password: LinkedIn 登錄密碼（可選）
        """
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.session = requests.Session()
        self.driver = None
        self.cookies = {}
        
        self._setup_session()
    
    def _setup_session(self):
        """設定 requests Session（User-Agent + Headers）"""
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.linkedin.com/',
            'DNT': '1',  # 不追蹤請求
        })
        logger.info(f"✓ Session 已設定（UA: {self.session.headers['User-Agent'][:50]}...）")
    
    def _random_delay(self):
        """隨機延遲（對抗速率限制）"""
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        logger.debug(f"⏳ 延遲 {delay:.2f} 秒...")
        time.sleep(delay)
    
    def _setup_driver(self) -> webdriver.Chrome:
        """建立 Selenium WebDriver（對抗 JavaScript 動態渲染）"""
        logger.info("🌐 啟動 Chrome 瀏覽器...")
        
        options = ChromeOptions()
        for opt in CHROME_OPTIONS:
            options.add_argument(opt)
        
        # 執行前隱藏 webdriver 跡象
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        # 關閉影像和 JS（加速）
        # prefs = {'profile.managed_default_content_settings.images': 2}
        # options.add_experimental_option('prefs', prefs)
        
        driver = webdriver.Chrome(options=options)
        
        # 執行 JS 隱藏 webdriver 標記
        driver.execute_cdp_command('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            '''
        })
        
        logger.info("✓ Chrome 已啟動（隱身模式）")
        return driver
    
    def login(self) -> bool:
        """登錄 LinkedIn（如果提供認證）"""
        if not self.email or not self.password:
            logger.warning("⚠️ 未提供郵箱/密碼，使用公開搜尋模式")
            return False
        
        logger.info(f"🔑 嘗試登錄 LinkedIn（{self.email}）...")
        
        try:
            self.driver = self._setup_driver()
            self.driver.get('https://www.linkedin.com/login')
            
            # 等待登錄表單加載
            wait = WebDriverWait(self.driver, 10)
            email_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            
            # 輸入郵箱
            email_field.send_keys(self.email)
            time.sleep(random.uniform(1, 2))
            
            # 輸入密碼
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(self.password)
            time.sleep(random.uniform(1, 2))
            
            # 提交
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            
            # 等待登錄完成
            time.sleep(5)
            
            # 儲存 Cookie
            self.cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            logger.info("✓ 登錄成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 登錄失敗：{e}")
            return False
    
    def search_profiles(self, keywords: str, location: str = "Taiwan", limit: int = 20) -> List[Dict]:
        """
        搜尋 LinkedIn 個人資料
        
        Args:
            keywords: 搜尋關鍵字（如 "Python Engineer"）
            location: 地點
            limit: 最大結果數
            
        Returns:
            候選人列表
        """
        logger.info(f"🔍 搜尋 LinkedIn：{keywords} @ {location}（限制 {limit} 筆）...")
        
        candidates = []
        
        # 方法 1：Google 搜尋（不登錄）
        candidates.extend(self._search_via_google(keywords, location, limit))
        
        # 方法 2：Selenium 動態搜尋（登錄後使用）
        if self.driver and self.email:
            candidates.extend(self._search_via_selenium(keywords, location, limit - len(candidates)))
        
        logger.info(f"✓ 找到 {len(candidates)} 位候選人")
        return candidates[:limit]
    
    def _search_via_google(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """使用 Google 搜尋 LinkedIn 公開資料（無需登錄）"""
        logger.info(f"  📱 方法 1：Google 搜尋...")
        
        candidates = []
        query = f'"{keywords}" {location} site:linkedin.com/in'
        
        try:
            # 模擬 Google 搜尋
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={limit}"
            
            response = self.session.get(
                search_url,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                # 提取 LinkedIn URLs
                linkedin_urls = re.findall(
                    r'href="(https://(?:www\.)?linkedin\.com/in/[^"]+)"',
                    response.text
                )
                
                for url in linkedin_urls[:limit]:
                    # 清理 URL
                    clean_url = url.split('?')[0].split('#')[0].rstrip('/')
                    
                    candidates.append({
                        'url': clean_url,
                        'name': clean_url.split('/')[-1],
                        'method': 'Google Search',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self._random_delay()
                
                logger.info(f"    ✓ 找到 {len(candidates)} 位候選人")
            else:
                logger.warning(f"    ⚠️ Google 搜尋失敗（HTTP {response.status_code}）")
                
        except Exception as e:
            logger.error(f"    ❌ Google 搜尋錯誤：{e}")
        
        return candidates
    
    def _search_via_selenium(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """使用 Selenium 動態搜尋（登錄後，抗 JavaScript）"""
        logger.info(f"  🤖 方法 2：Selenium 動態搜尋...")
        
        candidates = []
        
        try:
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(keywords)}&location={urllib.parse.quote(location)}'
            
            self.driver.get(search_url)
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 10)
            
            # 等待搜尋結果加載
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'reusable-search__result-container')))
            
            # 滾動加載更多結果
            for _ in range(min(limit // 10, 5)):
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(random.uniform(2, 3))
            
            # 提取候選人
            results = self.driver.find_elements(By.CLASS_NAME, 'reusable-search__result-container')
            
            for result in results[:limit]:
                try:
                    name_elem = result.find_element(By.CLASS_NAME, 'entity-result-title-text')
                    name = name_elem.text.strip()
                    
                    link_elem = result.find_element(By.TAG_NAME, 'a')
                    url = link_elem.get_attribute('href')
                    
                    candidates.append({
                        'url': url,
                        'name': name,
                        'method': 'Selenium',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.debug(f"    ⚠️ 提取結果失敗：{e}")
                    continue
            
            logger.info(f"    ✓ 找到 {len(candidates)} 位候選人")
            
        except Exception as e:
            logger.error(f"    ❌ Selenium 搜尋錯誤：{e}")
        
        return candidates
    
    def scrape_profile(self, profile_url: str) -> Dict:
        """
        爬取個人資料詳情
        
        Args:
            profile_url: LinkedIn 個人頁面 URL
            
        Returns:
            個人資料數據
        """
        logger.info(f"📄 爬取個人資料：{profile_url}...")
        
        profile_data = {
            'url': profile_url,
            'name': '',
            'title': '',
            'location': '',
            'about': '',
            'experience': [],
            'education': [],
            'skills': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if not self.driver:
                self.driver = self._setup_driver()
            
            self.driver.get(profile_url)
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 10)
            
            # 爬取基本信息
            try:
                name_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'text-heading-xlarge')))
                profile_data['name'] = name_elem.text.strip()
            except:
                pass
            
            try:
                title_elem = self.driver.find_element(By.CLASS_NAME, 'text-body-medium')
                profile_data['title'] = title_elem.text.strip()
            except:
                pass
            
            try:
                location_elem = self.driver.find_element(By.CLASS_NAME, 'text-body-small')
                profile_data['location'] = location_elem.text.strip()
            except:
                pass
            
            # 爬取關於部分
            try:
                about_elem = self.driver.find_element(By.XPATH, '//section[@aria-label="About"]')
                profile_data['about'] = about_elem.text.strip()
            except:
                pass
            
            logger.info(f"✓ 爬取成功：{profile_data['name']}")
            
        except Exception as e:
            logger.error(f"❌ 爬取失敗：{e}")
        
        self._random_delay()
        return profile_data
    
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ 瀏覽器已關閉")

# ==================== 主程式 ====================

def main():
    """主函數"""
    
    # 從環境變數讀取認證（可選）
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    # 初始化爬蟲
    scraper = LinkedInAdvancedScraper(email, password)
    
    try:
        # 嘗試登錄（如果提供認證）
        if email and password:
            scraper.login()
        
        # 搜尋候選人
        results = scraper.search_profiles(
            keywords="Python Engineer",
            location="Taiwan",
            limit=10
        )
        
        # 輸出結果
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # 爬取前 3 個候選人的詳情
        for result in results[:3]:
            profile = scraper.scrape_profile(result['url'])
            print(json.dumps(profile, indent=2, ensure_ascii=False))
        
    finally:
        scraper.close()

if __name__ == '__main__':
    main()
