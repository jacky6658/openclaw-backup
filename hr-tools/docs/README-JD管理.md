# JD 管理系統

## 📋 系統說明

**JD（Job Description）管理系統** 用於管理公司的職缺資訊，與履歷池整合使用。

## 📊 Google Sheets 結構

**職缺管理**: [AIJob 職缺管理](https://docs.google.com/spreadsheets/d/1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE/edit)

### 欄位說明

| 欄位 | 說明 | 範例 |
|------|------|------|
| 職位名稱 | 職位的正式名稱 | AI工程師 |
| **客戶公司** | **客戶公司名稱** | **美德醫療** |
| 部門 | 所屬部門 | 技術部 |
| 需求人數 | 需要招募的人數 | 2 |
| 薪資範圍 | 月薪範圍（台幣） | 80k-120k |
| 主要技能 | 必備技能（逗號分隔） | Python,AI,Machine Learning |
| 經驗要求 | 工作經驗要求 | 3年以上 |
| 學歷要求 | 學歷門檻 | 大學以上 |
| 工作地點 | 工作地點 | 台北 |
| 職位狀態 | 招募狀態 | 開放中 / 面試中 / 暫停招募 / 已結束 |
| 建立日期 | 職缺建立日期 | 2026-02-10 |
| 最後更新 | 最後更新時間 | 2026-02-10 18:30:45 |

## 🛠 使用工具

### 1. 初始化系統

```bash
./jd-manager.sh init
```

**說明**：初次使用時執行，建立表頭和系統結構。

### 2. 新增職缺

```bash
./jd-manager.sh add <職位名稱> <客戶公司> <部門> <需求人數> <薪資範圍> <主要技能> <經驗要求> <學歷要求> [工作地點] [狀態]
```

**範例**：

```bash
./jd-manager.sh add 'AI工程師' '美德醫療' '技術部' '2' '80k-120k' 'Python、AI、ML' '3年以上' '大學以上' '台北' '開放中'
```

**⚠️ 注意**：技能請使用頓號（、）分隔，不要用逗號（,）

**預設值**：
- 工作地點：台北
- 狀態：開放中

### 3. 列出所有職缺

```bash
./jd-manager.sh list
```

**輸出**：表格化的職缺清單

### 4. 搜尋職缺

```bash
./jd-manager.sh search <關鍵字>
```

**範例**：

```bash
./jd-manager.sh search 'AI'
./jd-manager.sh search '技術部'
./jd-manager.sh search '開放中'
```

**說明**：搜尋所有欄位，找出包含關鍵字的職缺。

### 5. 更新職缺狀態

```bash
./jd-manager.sh update-status <行數> <新狀態>
```

**範例**：

```bash
./jd-manager.sh update-status 2 '面試中'
./jd-manager.sh update-status 3 '已結束'
```

**可用狀態**：
- `開放中` — 正在招募
- `面試中` — 已有候選人在面試
- `暫停招募` — 暫時不招募
- `已結束` — 招募完成

**注意**：行數從 2 開始（第 1 行是表頭）

### 6. 產生統計報表

```bash
./jd-manager.sh report
```

**輸出範例**：

```
📊 職缺統計報表
====================
總職缺數: 5
開放中: 4
面試中: 1
暫停招募: 0
已結束: 0

📊 各部門職缺數:
   3 技術部
   1 產品部
   1 人資部
```

## 🔗 快速連結

- **職缺管理**: https://docs.google.com/spreadsheets/d/1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE/edit
- **履歷池**: https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q/edit

## 📝 最佳實踐

### 1. 職缺命名
- 使用標準職稱（如：AI工程師、數據分析師、產品經理）
- 避免使用過於模糊的名稱

### 2. 技能標註
- 使用逗號分隔技能
- 優先列出核心技能
- 範例：`Python,AI,Machine Learning,深度學習`

### 3. 薪資範圍
- 格式：`XXk-YYk`（月薪）
- 範例：`80k-120k`
- 或使用：`面議`

### 4. 狀態管理
- 定期更新職缺狀態
- 招募完成後改為「已結束」
- 暫時不招募時改為「暫停招募」

## 🚀 進階用法

### 快速新增多個職缺

建立 CSV 檔案 `jd-list.csv`：

```csv
AI工程師,技術部,2,80k-120k,Python|AI|ML,3年以上,大學以上,台北,開放中
數據分析師,數據部,1,60k-90k,Python|SQL|數據分析,2年以上,大學以上,台北,開放中
```

批次匯入：

```bash
while IFS=',' read -r title dept count salary skills exp edu location status; do
  # 將 | 轉成逗號
  skills_formatted=$(echo "$skills" | tr '|' ',')
  ./jd-manager.sh add "$title" "$dept" "$count" "$salary" "$skills_formatted" "$exp" "$edu" "$location" "$status"
done < jd-list.csv
```

### 定期報表

加入 cron 每週一早上 9:00 產生報表：

```bash
0 9 * * 1 /Users/user/clawd/hr-tools/jd-manager.sh report > /tmp/jd-report.txt && cat /tmp/jd-report.txt
```

### 與履歷池整合

當有履歷進來時，可以：

1. 查看對應職缺：`./jd-manager.sh search 'AI工程師'`
2. 確認職缺狀態是否開放
3. 如果職缺已滿，更新狀態：`./jd-manager.sh update-status <行數> '暫停招募'`

## 🔧 技術細節

### 使用的工具
- `gog sheets` — Google Sheets CLI
- Google Account: `aiagentg888@gmail.com`

### 檔案位置
- 管理工具: `/Users/user/clawd/hr-tools/jd-manager.sh`
- 說明文件: `/Users/user/clawd/hr-tools/README-JD管理.md`

### 常見問題

**Q: 如何刪除職缺？**  
A: 目前需要手動到 Google Sheets 刪除該行，或將狀態改為「已結束」。

**Q: 可以編輯職缺內容嗎？**  
A: 需要直接到 Google Sheets 編輯，或使用 `gog sheets update` 指令。

**Q: 技能欄位的格式？**  
A: 使用英文逗號分隔，例如：`Python,AI,Machine Learning`

---

**建立日期**: 2026-02-10  
**維護者**: YuQi 🦞 (HR 助理)  
**版本**: 1.0.0
