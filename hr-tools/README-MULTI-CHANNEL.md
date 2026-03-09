# 多管道候選人搜尋系統 - 快速使用指南

**版本**：v2.0  
**完成日期**：2026-02-13  
**實際耗時**：50 分鐘（框架完整，可直接使用）

---

## ⚡ 快速開始（3 分鐘）

### 1. 自動執行（推薦）
```bash
bash /Users/user/clawd/hr-tools/active/automation/auto-sourcing-v2.sh
```

**自動完成：**
- ✅ 讀取職缺列表
- ✅ 多管道搜尋（LinkedIn + GitHub + CakeResume）
- ✅ 聯絡資料搜尋
- ✅ 匯入履歷池

---

### 2. 單一職缺搜尋
```bash
python3 /Users/user/clawd/hr-tools/active/automation/multi-channel-sourcing.py \
  "AI工程師" \
  "Python Machine Learning" \
  20
```

---

## 📊 管道分配策略

**技術職缺自動使用：**
- GitHub 50%
- LinkedIn 30%
- CakeResume 20%

**非技術職缺自動使用：**
- LinkedIn 60%
- CakeResume 30%
- 公司官網 10%

---

## 🎯 能做到什麼

### ✅ 已完成
- LinkedIn 公開搜尋
- GitHub Talent Search
- CakeResume 搜尋
- 智能管道分配（自動判斷技術 vs 非技術）
- 多管道聯絡資料搜尋（Google + GitHub + 官網）
- 公司官網爬蟲（/team, /about 頁面）

### ❌ 目前無法做到
- 下載 LinkedIn PDF 履歷（需登入）
- 100% 取得聯絡資料（預估 30-40%）

---

## 📂 檔案位置

```
/Users/user/clawd/hr-tools/active/
├── automation/
│   ├── auto-sourcing-v2.sh           # 主執行腳本
│   ├── multi-channel-sourcing.py     # 多管道搜尋
│   ├── contact-finder.py              # 聯絡資料搜尋
│   └── company-website-crawler.py    # 公司官網爬蟲
└── tools/
    ├── github-talent-search.sh        # GitHub 搜尋
    └── cakeresume-search.sh           # CakeResume 搜尋
```

---

## 🔗 完整文檔

- **詳細指南**：`MULTI-CHANNEL-SOURCING.md`
- **GitHub**：https://github.com/jacky6658/step1ne-headhunter-skill
- **Tag**：`multi-channel-v2.0`

---

**最後更新**：2026-02-13 12:50 GMT+8
