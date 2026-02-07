# Workspace 結構規劃（大掃除）

## 📂 當前問題

1. **重複目錄**：`docs/` 和 `templates/` 有重複內容
2. **混亂的分類**：技術、文檔、專案、臨時檔案混在一起
3. **未整理的暫存**：`tmp/`, `downloads/`, `output/` 未清理
4. **Skills 分散**：`skills/`, `skills-import/`, `skills_imported/` 三個地方

---

## 🎯 新結構規劃

```
/Users/user/clawd/
├── 📁 projects/              # 專案開發
│   ├── aijobcase-1/          # EduMind AI 教材問答
│   ├── edumind-api/          # EduMind API
│   ├── token-dashboard/      # Token Dashboard
│   └── installers/           # OpenClaw 安裝包
│
├── 📁 docs/                  # 文檔庫（整合）
│   ├── guides/               # 使用指南
│   │   ├── OpenClaw-終端機指令大全.md
│   │   ├── OpenClaw-Mac-安裝教學_Phoebe.md
│   │   ├── Cooldown完全指南.md
│   │   └── 緊急切換模型指南.md
│   ├── courses/              # 課程相關
│   │   ├── PPA-OpenClaw-課程腳本與影片分配.md
│   │   ├── AI學習能力說明.md
│   │   └── 教材/
│   ├── gog/                  # Google Workspace 教學
│   ├── design/               # 設計文件
│   │   ├── LINE-integration-plan.md
│   │   └── solar-weather/
│   └── archives/             # 舊文檔歸檔
│
├── 📁 skills/                # OpenClaw Skills（整合）
│   ├── installed/            # 已安裝的 skills
│   │   ├── agent-browser/
│   │   ├── cellcog/
│   │   ├── oracle/
│   │   └── ...
│   ├── developing/           # 開發中的 skills
│   │   ├── desktop-control-1.0.0/
│   │   └── clawiskill-0.1.0/
│   └── archived/             # 已廢棄的 skills
│
├── 📁 tasks/                 # 任務管理
│   ├── 待辦清單.md
│   ├── 交接_狀態總覽.md
│   └── 每日會報/
│
├── 📁 memory/                # 記憶庫（保持不變）
│   └── 2026-02-*.md
│
├── 📁 media/                 # 媒體資源（新增）
│   ├── videos/               # 短影音
│   ├── images/               # 圖片素材
│   └── audio/                # 音訊檔
│
├── 📁 templates/             # 範本庫（清理後）
│   ├── agent-persona/
│   ├── 每日會報範例/
│   └── 老闆助理/
│
├── 📁 tmp/                   # 暫存（定期清理）
│   └── README.md (標註：可安全刪除)
│
├── 📁 canvas/                # Canvas 資料（保持）
├── 📁 logs/                  # 日誌（保持）
│
└── 📄 核心檔案（保持）
    ├── AGENTS.md
    ├── SOUL.md
    ├── USER.md
    ├── MEMORY.md
    ├── HEARTBEAT.md
    ├── IDENTITY.md
    └── TOOLS.md
```

---

## 🔄 遷移計劃

### Phase 1: 文檔整理
```bash
# 建立新結構
mkdir -p docs/{guides,courses,design,archives}

# 移動指南
mv docs/OpenClaw-*.md docs/guides/
mv docs/Cooldown完全指南.md docs/guides/
mv docs/緊急切換模型指南.md docs/guides/

# 移動課程
mv docs/PPA-*.md docs/courses/
mv docs/AI學習能力說明.md docs/courses/
mv docs/教材 docs/courses/

# 移動設計文件
mv docs/LINE-*.md docs/design/

# 歸檔舊文檔
mv docs/{boss-assistant,browser,meta,security,setup,tasks} docs/archives/
```

### Phase 2: Skills 整合
```bash
# 建立新結構
mkdir -p skills/{installed,developing,archived}

# 移動已安裝
mv skills/* skills/installed/ (排除目錄)

# 移動開發中
mv skills-import/* skills/developing/

# 移動已廢棄
mv skills_imported/* skills/archived/

# 刪除空目錄
rmdir skills-import skills_imported
```

### Phase 3: 專案整理
```bash
# 移動安裝包專案
mv installers projects/

# 整理臨時檔案
rm -rf tmp/* downloads/* output/ig

# 建立媒體目錄
mkdir -p media/{videos,images,audio}
mv 短影音專業能力 media/videos/
```

### Phase 4: 清理
```bash
# 刪除重複的 templates 內容
rm -rf templates/{browser,gog,meta,security,setup,tasks,skills}

# 清理暫存
echo "This directory contains temporary files and can be safely deleted." > tmp/README.md
```

---

## 📊 預期效果

### Before（現況）
```
❌ 70+ 個頂層項目
❌ 文檔分散在 docs/ 和 templates/
❌ Skills 在 3 個不同位置
❌ 大量未清理的暫存檔
```

### After（整理後）
```
✅ 8 個主要分類
✅ 文檔集中在 docs/ (4 個子分類)
✅ Skills 整合在 skills/ (3 個子分類)
✅ 專案集中在 projects/
✅ 暫存檔標註清理
```

---

## ⚠️ 注意事項

1. **備份**：執行前先備份整個 workspace
2. **測試**：移動後測試 OpenClaw 是否正常運作
3. **Git**：如果有 git repo，需要更新 `.gitignore`
4. **路徑**：檢查是否有硬編碼的絕對路徑需要更新

---

## 🚀 執行建議

**選項 A**：我自動執行（快速但風險較高）  
**選項 B**：生成腳本給你審核後執行（安全）  
**選項 C**：分階段執行，每階段確認（最安全）

**你要選哪個？**
