# LinkedIn PDF 履歷自動下載腳本 — 使用說明

> 腳本位置：`/Users/user/clawd/headhunter-crawler/scripts/linkedin_pdf_download.py`

---

## 運作原理

透過 **Playwright** 連接本機已登入的 Chrome（CDP 協議），模擬人類操作 LinkedIn，自動下載候選人履歷 PDF。

### 兩種下載方式（自動判斷）

| 方式 | 條件 | 說明 |
|------|------|------|
| **方式A** — LinkedIn 原生 Save to PDF | 任何人（含非一度） | JS 點 More → 存為 PDF，攔截下載，取得標準履歷 |
| **方式B** — page.pdf() 列印備援 | 方式A失敗時 | 把 LinkedIn Profile 頁面列印成 PDF（排版較差） |

### 關鍵實作細節（2026-03-23 修正）

原本的問題：More 按鈕會被 LinkedIn 其他元素（商務功能按鈕）遮擋，`locator.click()` 會 Timeout。

**解法：改用 JavaScript 點擊 + expect_download() 攔截**

```python
# 1. JS 點擊 More 按鈕（繞過元素遮擋）
await page.evaluate("""
    () => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const moreBtn = buttons.find(b =>
            b.textContent.trim() === 'More' ||
            b.textContent.trim() === '更多'
        );
        if (moreBtn) moreBtn.click();
    }
""")

# 2. 用 expect_download() 攔截下載事件
async with page.expect_download(timeout=15000) as dl_info:
    await page.evaluate("""
        () => {
            const saveItem = Array.from(document.querySelectorAll('li, div, span'))
                .find(el => el.textContent.trim() === '存為 PDF');
            if (saveItem) saveItem.click();
        }
    """)
download = await dl_info.value
await download.save_as(str(save_path))
```

> **重要**：必須用 `expect_download()` 攔截，否則 Chrome 下載了但腳本拿不到檔案路徑。

---

## 前置條件

### 1. 啟動 Chrome CDP 模式
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp
```

### 2. 在新開的 Chrome 登入 LinkedIn
用你自己的 LinkedIn 帳號登入。

### 3. 確認 CDP 連線
```bash
curl http://localhost:9222/json/version
```
看到 Chrome 版本資訊就代表成功。

---

## 使用步驟

### Step 1：編輯候選人清單

打開腳本，找到 `candidates` 清單，填入要下載的人：

```python
candidates = [
    # (候選人ID, "姓名", "LinkedIn URL", "評級"),
    (3003, "Kun Yen", "https://www.linkedin.com/in/yenkun/", "B+"),
    (3005, "William Wu", "https://www.linkedin.com/in/william-wu-xxx/", "A"),
]
```

### Step 2：執行腳本

```bash
cd /Users/user/clawd/headhunter-crawler

API_SECRET_KEY=PotfZ42-qPyY4uqSwqstpxllQB1alxVfjJsm3Mgp3HQ \
python scripts/linkedin_pdf_download.py
```

### Step 3：查看結果

PDF 會存到兩個地方：
- 主目錄：`resumes/linkedin_pdfs/`
- 備份：`resumes/pending_upload/`

---

## 反偵測機制

腳本內建多種模擬人類的行為：

| 機制 | 設定 | 說明 |
|------|------|------|
| 隨機間隔 | 45~90 秒 | 每個候選人之間隨機等待 |
| 批次休息 | 每 5 人休息 10 分鐘 | 避免頻繁操作被偵測 |
| 閱讀模擬 | 5~12 秒 | 進入頁面後隨機滾動 |
| Feed 瀏覽 | 隨機觸發 30% | 偶爾去 LinkedIn Feed 瀏覽 |
| Hover 延遲 | 0.5~1.5 秒 | 點擊前先 hover |

---

## 上傳到 HR 系統

如果設定了 `API_SECRET_KEY`，下載完會自動呼叫：

```
POST /api/candidates/:id/resume-parse
```

自動解析 PDF 並更新人選卡片的所有欄位（工作經歷、技能、學歷等）。

---

## 今天的實際測試（2026-03-23）

測試對象：Hank Chiang
- LinkedIn: https://www.linkedin.com/in/hank-chiang-14b309113/
- 最終結果：✅ 成功，60KB 原生 LinkedIn PDF
- 方式：JS 點擊 More + expect_download() 攔截（方式A）
- 問題排除：原本 More 按鈕被「商務功能」按鈕遮擋 → 改用 JS 直接 click() 解決

---

## 注意事項

1. **不能用 Jacky 的個人 LinkedIn 帳號做自動化**（MEMORY.md 硬性規定）
2. 腳本連接的 Chrome 要用**專用帳號**
3. LinkedIn 每月有 PDF 下載上限，超過自動改用 page.pdf()
4. 每天建議不超過 50 人，避免帳號被限制
