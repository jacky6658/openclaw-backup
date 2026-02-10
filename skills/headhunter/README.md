# 🦞 獵頭顧問 AI 技能包

為獵頭顧問設計的 AI 自動化工具，讓 Bot 能執行完整的招募工作流程。

## 快速安裝

```bash
# 方法 1：執行安裝腳本
./install.sh ~/clawd

# 方法 2：手動複製
cp -r headhunter/ ~/clawd/skills/
mkdir -p ~/clawd/data/headhunter
```

## 安裝後設定

### 1. Telegram 群組資訊（已預設）
群組資訊已寫在 `config/telegram-groups.json`：
```json
{
  "group_id": "-1003231629634",
  "topics": {
    "#履歷進件": "4",
    "#履歷池": "304",
    "#JD列表": "319",
    "#總覽看板": "326"
  }
}
```
**新 Bot 安裝後自動讀取，無需手動設定！**

### 2. 設定 Email（gog）
```bash
gog auth add your@email.com --services gmail
```

### 3. 測試
```bash
python3 ~/clawd/skills/headhunter/scripts/dashboard.py
python3 ~/clawd/skills/headhunter/scripts/auto-followup.py demo
```

## 功能列表

| 功能 | 說明 | 觸發詞 |
|------|------|--------|
| 人才畫像 | 分析 JD 產出人選特徵 | 「人才畫像」「分析 JD」 |
| 搜尋策略 | Boolean String + 管道建議 | 「搜尋策略」「找人」 |
| 履歷匹配 | 履歷 vs JD 匹配分析 | 「匹配度」「分析履歷」 |
| 開發信 | 撰寫候選人開發信 | 「開發信」「InMail」 |
| 面試問題 | 生成面試問題 | 「面試問題」 |
| JD 生成 | 撰寫職位說明 | 「寫 JD」 |
| 候選人摘要 | 整理候選人報告 | 「候選人摘要」 |
| 推薦信 | 撰寫推薦 Email | 「推薦信」「推人選」 |

## 自動化工具

| 工具 | 檔案 | 用途 |
|------|------|------|
| GitHub 搜尋 | `github-talent-search.py` | 搜尋開發者 |
| 批量匹配 | `batch-match.py` | 多履歷 vs JD |
| 總覽看板 | `dashboard.py` | Pipeline 追蹤 |
| 自動跟進 | `auto-followup.py` | 排程提醒 |

## 工作流程

```
履歷進來 → #履歷進件
    ↓
YQ1 自動匹配 vs 所有 JD
    ↓
┌─────────┬─────────┬─────────┐
│ ≥90%    │ 70-89%  │ <70%    │
│ 建議推   │ 待確認   │ 放池子   │
└────┬────┴────┬────┴────┬────┘
     ↓         ↓         ↓
  通知顧問   通知顧問   存 #履歷池
     ↓         ↓
  回「推」   回「推」
     ↓         ↓
  YQ2 發信 + 設提醒
```

## 匹配度門檻

| 分數 | 狀態 | 動作 |
|------|------|------|
| ≥90% | 🟢 高匹配 | 通知 + 建議直接推 |
| 70-89% | 🟡 中匹配 | 通知 + 等顧問確認 |
| <70% | ⚪ 低匹配 | 不通知，放履歷池 |

## 自動跟進規則

| 狀態 | 跟進時間 |
|------|----------|
| 推薦後 | 3天、7天、14天 |
| 面試後 | 1天、3天 |
| Offer | 每天 |
| 報到後 | Day1、Week1、Month1、90天 |

## 目錄結構

```
headhunter/
├── SKILL.md              # 技能說明
├── README.md             # 本文件
├── install.sh            # 安裝腳本
├── references/
│   └── prompts.md        # Prompt 模板
├── scripts/
│   ├── github-talent-search.py
│   ├── batch-match.py
│   ├── dashboard.py
│   └── auto-followup.py
└── templates/
    └── resume-format.md
```

## 支援

有問題請聯繫 Jacky 或 YuQi 🦞
