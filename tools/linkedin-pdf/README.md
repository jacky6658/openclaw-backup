# LinkedIn PDF 批量下載工具

## 使用步驟

### 1. 準備候選人列表
建立 `/tmp/li_candidates.json`：
```json
[
  {"id": "1234", "name": "姓名", "linkedin_url": "https://www.linkedin.com/in/xxx/"}
]
```

### 2. 確認 Chrome 已登入 LinkedIn 且視窗在前景

### 3. 執行批量下載
```bash
./linkedin_batch_pdf.sh
```
- 每位候選人約 12 秒
- PDF 存到 ~/Downloads/Profile*.pdf
- 完成後看 log 確認哪些成功/失敗

### 4. 解析 PDF + 上傳 Step1ne

根據 log 建立 `/tmp/pdf_mapping.json`：
```json
[
  {"id": "1234", "name": "姓名", "pdf": "/Users/user/Downloads/Profile (4).pdf"}
]
```

然後執行：
```bash
python3 parse_and_upload.py
```

### 5. 失敗的候選人用 Web Search 補
搜尋 `{name} LinkedIn {url_slug}`，提取職位/技能/學歷，手動或用腳本 PATCH API。

---

## 關鍵座標（MacBook 螢幕固定）
- More 按鈕：`cliclick c:339,719`
- 存為 PDF：`cliclick c:446,508`

如果座標跑掉（螢幕解析度改變），用這段 JS 重新校正：
```javascript
// 在 Chrome DevTools Console 執行（先點 More 開選單）
(function(){
  var all = document.querySelectorAll("*");
  for(var el of all){
    if((el.textContent||"").trim() === "存為 PDF"){
      var r = el.getBoundingClientRect();
      if(r.width > 0) return Math.round(r.x+r.width/2+window.screenX)+","+Math.round(r.y+r.height/2+window.screenY+100);
    }
  }
})()
```

## API
- Base: `https://backendstep1ne.zeabur.app`
- PATCH `/api/candidates/{id}` 更新資料
- actor 帶 `"Jacky-aibot"`
