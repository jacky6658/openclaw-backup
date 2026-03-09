# 自動找人選 - 快速啟動指南

**版本**：v1.0  
**適用對象**：新手 AI Bot / 其他團隊  
**預計時間**：10 分鐘上手

---

## ⚡ 3 步驟開始

### Step 1: 準備環境（5 分鐘）

1. **安裝 gog CLI**
```bash
brew install steipete/tap/gogcli
```

2. **授權 Google 帳號**
```bash
gog auth add your-email@gmail.com --services sheets
```

3. **確認 OpenClaw 工具**
- ✅ `web_search`（Brave Search API）
- ✅ `message`（Telegram 通知）

---

### Step 2: 設定資料表（3 分鐘）

**需要 2 個 Google Sheets**：

1. **職缺列表（JD List）**
   - Sheet ID：`1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE`
   - 欄位：職位名稱 | 客戶公司 | 部門 | 需求人數 | 薪資範圍 | 主要技能

2. **履歷池（Resume Pool）**
   - Sheet ID：`1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q`
   - 欄位：姓名 | 聯絡方式 | 應徵職位 | 主要技能 | ... （共 12 欄）

**權限**：確保你的 Google 帳號有編輯權限

---

### Step 3: 執行搜尋（2 分鐘）

**最簡單的方式**：

```python
# 1. 搜尋單一職缺
web_search(
    query="AI Engineer Machine Learning Python Taiwan site:linkedin.com/in",
    count=10
)

# 2. 解析結果
results = [...]  # 從 web_search 回傳
candidates = []
for r in results:
    name = r['title'].split(' - ')[0]
    url = r['url']
    candidates.append({'name': name, 'url': url, 'title': r['title']})

# 3. 匯入履歷池
import json
import subprocess

rows = [[c['name'], c['url'], "AI工程師", c['title'], "", "", c['url'], 
         "待聯繫", "Jacky", "自動搜尋匯入", "2026-02-13", "2026-02-13"] 
        for c in candidates]

cmd = [
    'gog', 'sheets', 'append',
    '1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q',
    '工作表1!A:L',
    '--account', 'your-email@gmail.com',
    '--values-json', json.dumps(rows, ensure_ascii=False),
    '--insert', 'INSERT_ROWS'
]

subprocess.run(cmd)
```

✅ **完成！** 候選人已匯入履歷池

---

## 📚 完整文檔

**如果需要完整流程、故障排除、最佳實踐**：

1. **完整流程指南**：
   - 📄 `AUTO-SOURCING-GUIDE.md`
   - 🔗 https://github.com/jacky6658/step1ne-headhunter-skill/blob/main/AUTO-SOURCING-GUIDE.md

2. **實戰腳本包**：
   - 📄 `AUTO-SOURCING-SCRIPTS.md`
   - 🔗 https://github.com/jacky6658/step1ne-headhunter-skill/blob/main/AUTO-SOURCING-SCRIPTS.md

---

## 💡 關鍵技巧（速記）

### 搜尋關鍵字格式
```
<職位> <技能> <地區> site:linkedin.com/in
```

### 批次大小
- 每批 ≤20 筆（避免 API 限制）

### 去重
```python
existing_urls = set(pool['LinkedIn'])
new = [c for c in candidates if c['url'] not in existing_urls]
```

### Telegram 通知
```python
message(
    action="send",
    channel="telegram",
    target="-1003231629634",  # 群組 ID
    threadId="304",            # Topic ID
    message="✅ 找到 10 位候選人"
)
```

---

## 🎯 成功案例（2026-02-13）

**輸入**：11 個職缺  
**輸出**：84 位候選人  
**耗時**：3 分鐘  
**準確率**：~70%（需人工篩選）

---

## 🆘 快速求助

**遇到問題？**

1. 檢查 `gog auth list`（授權）
2. 檢查 Sheet ID 是否正確
3. 檢查 JSON 格式（用 `jq` 驗證）
4. 查看完整文檔（上方連結）

**聯絡方式**：
- Telegram：@YuQi0923_bot
- GitHub Issues：https://github.com/jacky6658/step1ne-headhunter-skill/issues

---

**最後更新**：2026-02-13 12:17 GMT+8
