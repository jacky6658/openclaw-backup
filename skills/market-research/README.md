# 市場調查報告製作技能

## 快速開始

### 1. 手動版（20 分鐘）

```bash
# Step 1：收集市場數據（Google 搜尋）
# 整理成 Markdown 檔案

# Step 2：讀取內部數據
gog sheets get "[BD Sheet ID]" "A1:Z100" --json

# Step 3：生成報告
./scripts/generate-report.sh --market-data data.md --output report.html

# Step 4：上傳
cd /tmp/aijob-presentations
git add report.html && git commit -m "報告" && git push
```

### 2. 自動版（每週一 09:00）

```bash
# 設定 Cron Job
cron add \
  --schedule "0 9 * * 1" \
  --command "~/clawd/skills/market-research/scripts/weekly-report.sh" \
  --name "每週市場調查報告"
```

## 檔案結構

```
market-research/
├── SKILL.md                 # 技能說明書（完整教學）
├── README.md                # 快速開始
├── scripts/                 # 執行腳本
│   ├── weekly-report.sh     # 每週自動報告
│   ├── collect-market-data.sh   # 收集市場數據
│   ├── analyze-internal-data.sh # 整理內部數據
│   └── generate-report.sh   # 生成 HTML 報告
├── templates/               # 報告範本
│   └── report-template.html # HTML 範本
├── references/              # 參考資料
│   └── data-sources.md      # 數據來源清單
└── data/                    # 數據儲存（自動生成）
    ├── market-data-YYYY-MM-DD.md
    └── internal-stats-YYYY-MM-DD.json
```

## 詳細說明

請閱讀 [SKILL.md](./SKILL.md) 了解完整流程。

## 支援

- 製作者：YuQi (YQ1)
- 版本：1.0.0
- 更新：2026-02-11
