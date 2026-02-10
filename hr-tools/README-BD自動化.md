# BD 客戶開發信自動化

## 🎯 功能
自動寄送合作邀請信給潛在客戶，使用 Step1ne 官方信箱 `aijessie88@step1ne.com`

## 📧 信件類型：合作邀請信

**主旨**：【Step1ne】獵頭合作邀請 - 協助您快速找到優秀人才

**內容架構**：
1. 開場問候
2. Step1ne 優勢介紹（AI 匹配、人才庫、快速交付、保證期）
3. 成功案例展示
4. 行動呼籲（CTA）
5. 聯絡方式

## 🚀 快速開始

### 1. 確認 gog 帳號
```bash
gog auth list | grep aijessie88@step1ne.com
```

如果沒有，請執行：
```bash
gog auth add aijessie88@step1ne.com --services gmail
```

### 2. 預覽信件
```bash
cd ~/clawd/hr-tools
./bd-outreach.sh preview "ABC科技" "王經理"
```

### 3. 寄送單一客戶
```bash
# 知道聯絡人名字
./bd-outreach.sh send "ABC科技" "hr@abc.com" "王經理"

# 不知道聯絡人名字
./bd-outreach.sh send "ABC科技" "hr@abc.com"
```

### 4. 批量寄送（從客戶資料庫）
```bash
# 開發中...
./bd-outreach.sh batch 1 10
```

## 📊 客戶資料庫

### 格式：`clients.json`
```json
[
  {
    "name": "公司名稱",
    "email": "hr@company.com",
    "contactPerson": "聯絡人",
    "source": "來源（104/LinkedIn/手動）",
    "status": "待開發/已寄送/已回覆/合作中",
    "notes": "備註",
    "addedAt": "2026-02-10"
  }
]
```

### 管理客戶
```bash
# 列出所有客戶
./bd-outreach.sh list
```

## 📝 寄信記錄

所有寄信記錄會自動存入 `bd-sent.log`：
```
2026-02-10 19:10:00 | ABC科技 | hr@abc.com | 【Step1ne】獵頭合作邀請...
```

查看記錄：
```bash
tail -20 ~/clawd/hr-tools/bd-sent.log
```

## 🔗 整合流程

### 與 104 爬蟲整合
```bash
# 1. 爬取 104 職缺，找到招聘公司
cd ~/clawd/skills/headhunter/scripts
python3 scraper-104.py "backend engineer" 20

# 2. 提取公司資訊加到 clients.json
# （手動或自動化）

# 3. 批量寄送開發信
cd ~/clawd/hr-tools
./bd-outreach.sh batch 1 10
```

### Telegram 觸發
在 Telegram 群組輸入：
```
「寄BD信給 ABC科技」
```

YuQi 會自動：
1. 從 clients.json 找到客戶資料
2. 生成合作邀請信
3. 使用 aijessie88@step1ne.com 寄出
4. 記錄到 bd-sent.log

## ⚙️ 進階設定

### 自訂信件模板
編輯 `bd-outreach.sh` 中的 `generate_email` 函數

### 寄信頻率控制
建議：
- 每位客戶只寄一次
- 批量寄送時間間隔 30 秒（避免被標記為垃圾信）
- 每天最多 50 封

### 追蹤與跟進
- 第 3 天：檢查是否回信
- 第 7 天：發送跟進信（開發中）
- 第 14 天：標記為「無回應」

## 📈 效果追蹤

### 統計報表（開發中）
```bash
./bd-outreach.sh stats

# 輸出：
# 📊 BD 開發信統計
# 總寄送：50 封
# 已回覆：5 封（10%）
# 合作中：2 封（4%）
# 待跟進：10 封
```

## 🐛 除錯

### 錯誤：找不到 gog
```bash
brew install steipete/tap/gogcli
```

### 錯誤：找不到帳號
```bash
gog auth add aijessie88@step1ne.com --services gmail
```

### 錯誤：寄信失敗
檢查：
1. 帳號是否有 Gmail 權限
2. Email 格式是否正確
3. 信箱是否被標記為垃圾信

---

## 📞 支援
有問題請在 Telegram 群組詢問 YuQi
