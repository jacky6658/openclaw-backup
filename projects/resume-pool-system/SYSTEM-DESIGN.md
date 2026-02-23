# 履歷池管理系統 - 系統設計文檔

基於 AIJobcase CaseFlow 架構，打造專業的獵頭履歷池管理系統

---

## 🎯 專案目標

將現有的 Google Sheets 履歷池（228 筆候選人）升級為：
- ✅ 視覺化、互動式的 Web 應用
- ✅ 整合 AI 配對、穩定度預測、文化匹配功能
- ✅ 多顧問協作（Jacky + Phoebe）
- ✅ 即時同步 Google Sheets（雙向）

---

## 📊 資料架構

### 核心資料表

#### 1. **candidates** - 候選人主表
```sql
CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,                    -- A: 姓名
  email VARCHAR(255),                            -- B: Email
  phone VARCHAR(50),                             -- C: Phone
  location VARCHAR(100),                         -- D: Location
  position VARCHAR(200),                         -- E: Position
  years_experience DECIMAL(4,1),                 -- F: Years
  job_changes INT,                               -- G: Job Changes
  avg_tenure DECIMAL(4,1),                       -- H: Avg Tenure
  last_gap_months INT,                           -- I: Gap
  skills TEXT,                                   -- J: Skills
  education TEXT,                                -- K: Education
  source VARCHAR(100),                           -- L: Source
  work_history JSONB,                            -- M: Work JSON
  quit_reasons TEXT,                             -- N: Quit Reasons
  stability_score INT,                           -- O: Stability Score
  education_json JSONB,                          -- P: Edu JSON
  disc_profile VARCHAR(20),                      -- Q: DISC
  status VARCHAR(50) DEFAULT '待聯繫',           -- R: Status
  consultant VARCHAR(50),                        -- S: Consultant
  notes TEXT,                                    -- T: Notes
  
  -- 額外欄位
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_contact_at TIMESTAMP,
  
  -- 索引
  created_by VARCHAR(50),
  updated_by VARCHAR(50)
);

CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_consultant ON candidates(consultant);
CREATE INDEX idx_candidates_source ON candidates(source);
CREATE INDEX idx_candidates_stability ON candidates(stability_score);
```

#### 2. **candidate_progress** - 候選人進度記錄
```sql
CREATE TABLE candidate_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id),               -- 關聯職缺
  old_status VARCHAR(50),
  new_status VARCHAR(50) NOT NULL,
  contact_type VARCHAR(50),                      -- 電話/Email/面試/Offer
  content TEXT,                                  -- 進度內容
  next_action VARCHAR(255),                      -- 下次行動
  next_action_date DATE,                         -- 下次聯繫日期
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(50)
);

CREATE INDEX idx_progress_candidate ON candidate_progress(candidate_id);
CREATE INDEX idx_progress_job ON candidate_progress(job_id);
```

#### 3. **jobs** - 職缺表
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_code VARCHAR(50) UNIQUE NOT NULL,          -- JD-001
  title VARCHAR(200) NOT NULL,
  company VARCHAR(200),
  department VARCHAR(100),
  location VARCHAR(100),
  salary_min INT,
  salary_max INT,
  required_skills TEXT[],
  required_years INT,
  required_education VARCHAR(50),
  status VARCHAR(50) DEFAULT '招募中',           -- 招募中/已關閉/已成交
  
  -- JD 詳細資訊
  jd_description TEXT,
  jd_requirements JSONB,
  culture_profile JSONB,                         -- 文化特徵（用於 culture_matcher）
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(50)
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_code ON jobs(job_code);
```

#### 4. **candidate_job_matches** - AI 配對結果
```sql
CREATE TABLE candidate_job_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id),
  job_id UUID REFERENCES jobs(id),
  
  -- AI 配對分數
  total_score DECIMAL(5,2),                      -- 總分 0-100
  skill_score DECIMAL(5,2),                      -- 技能匹配 30%
  stability_score DECIMAL(5,2),                  -- 穩定度 30%
  culture_score DECIMAL(5,2),                    -- 文化匹配 20%
  experience_score DECIMAL(5,2),                 -- 經驗匹配 20%
  
  grade VARCHAR(5),                              -- P0/P1/P2/REJECT
  match_reason TEXT,                             -- AI 推薦理由
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(candidate_id, job_id)
);

CREATE INDEX idx_matches_job ON candidate_job_matches(job_id);
CREATE INDEX idx_matches_grade ON candidate_job_matches(grade);
```

#### 5. **placements** - 成功推薦記錄
```sql
CREATE TABLE placements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id),
  job_id UUID REFERENCES jobs(id),
  
  -- 推薦資訊
  placement_date DATE NOT NULL,                  -- 上職日期
  salary INT,                                    -- 確認薪資
  fee DECIMAL(10,2),                             -- 推薦費用
  fee_percentage DECIMAL(5,2),                   -- 費率 %
  
  -- 保證期追蹤
  guarantee_days INT DEFAULT 90,                 -- 保證期天數
  guarantee_end_date DATE,                       -- 保證期結束日
  status VARCHAR(50) DEFAULT '保證期內',         -- 保證期內/已通過/已退費
  
  -- 離職記錄
  left_date DATE,                                -- 離職日期
  left_reason TEXT,                              -- 離職原因
  refund_amount DECIMAL(10,2),                   -- 退費金額
  
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(50)
);

CREATE INDEX idx_placements_status ON placements(status);
CREATE INDEX idx_placements_guarantee_end ON placements(guarantee_end_date);
```

---

## 🎨 前端架構

### 技術棧
- **框架**: React 19 + TypeScript + Vite
- **樣式**: Tailwind CSS
- **圖表**: Recharts
- **狀態管理**: React Context + Hooks
- **後端通訊**: Fetch API (雙模式：PostgreSQL API + Google Sheets)

### 頁面結構

```
/pages
  ├── DashboardPage.tsx          # 📊 儀表板（總覽）
  ├── CandidatesPage.tsx         # 📋 候選人總表
  ├── CandidateDetailPage.tsx    # 👤 候選人詳情
  ├── KanbanPage.tsx             # 📊 招募看板（候選人流程）
  ├── JobsPage.tsx               # 💼 職缺管理
  ├── JobDetailPage.tsx          # 📄 職缺詳情 + AI 推薦
  ├── MatchingPage.tsx           # 🤖 AI 智慧配對
  ├── PlacementsPage.tsx         # 💰 成功推薦 + 保證期追蹤
  ├── AnalyticsPage.tsx          # 📈 數據分析
  └── SettingsPage.tsx           # ⚙️ 系統設定
```

### 組件結構

```
/components
  ├── candidates/
  │   ├── CandidateCard.tsx      # 候選人卡片
  │   ├── CandidateModal.tsx     # 新增/編輯候選人
  │   ├── CandidateTimeline.tsx  # 工作經歷時間軸
  │   ├── StabilityGauge.tsx     # 穩定度儀表盤
  │   └── CultureRadar.tsx       # 文化匹配雷達圖
  ├── jobs/
  │   ├── JobCard.tsx            # 職缺卡片
  │   ├── JobModal.tsx           # 新增/編輯職缺
  │   └── MatchList.tsx          # AI 推薦候選人列表
  ├── kanban/
  │   ├── KanbanBoard.tsx        # 看板主體
  │   ├── KanbanColumn.tsx       # 看板欄位
  │   └── KanbanCard.tsx         # 候選人卡片（可拖曳）
  ├── analytics/
  │   ├── SourceChart.tsx        # 來源分布圖
  │   ├── StatusChart.tsx        # 狀態分布圖
  │   ├── PlacementChart.tsx     # 成功推薦趨勢
  │   └── GuaranteeTable.tsx     # 保證期追蹤表
  └── shared/
      ├── Badge.tsx              # 狀態標籤
      ├── Sidebar.tsx            # 側邊欄
      └── FileUpload.tsx         # 履歷上傳（支援 PDF 解析）
```

---

## 🔧 核心功能模組

### 1. 履歷自動解析
```typescript
// services/resumeParser.ts
import { parseResume } from '../ai/resume-parser-v2';

export async function uploadResume(file: File): Promise<Candidate> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/candidates/parse', {
    method: 'POST',
    body: formData
  });
  
  const parsed = await response.json();
  
  // 返回結構化候選人資料（包含工作經歷 JSON、穩定度評分）
  return {
    name: parsed.name,
    email: parsed.email,
    phone: parsed.phone,
    work_history: parsed.work_history,  // JSON
    stability_score: parsed.stability_score,
    ...
  };
}
```

### 2. AI 智慧配對
```typescript
// services/matchingService.ts
import { aiMatcher } from '../ai/ai-matcher-v3';

export async function matchCandidatesToJob(jobId: string): Promise<Match[]> {
  const job = await getJob(jobId);
  const candidates = await getCandidates({ status: '待聯繫' });
  
  const matches = await Promise.all(
    candidates.map(candidate => 
      aiMatcher.match(job, candidate)
    )
  );
  
  // 返回排序後的配對結果（P0 → P1 → P2）
  return matches
    .filter(m => m.grade !== 'REJECT')
    .sort((a, b) => b.total_score - a.total_score);
}
```

### 3. 穩定度視覺化
```typescript
// components/candidates/StabilityGauge.tsx
export function StabilityGauge({ score, breakdown }: Props) {
  return (
    <div className="stability-gauge">
      <CircularProgress value={score} max={100} />
      <div className="breakdown">
        <div>基礎分: {breakdown.base}</div>
        <div>年資加分: +{breakdown.years_bonus}</div>
        <div>離職扣分: -{breakdown.changes_penalty}</div>
        <div>空窗扣分: -{breakdown.gap_penalty}</div>
      </div>
    </div>
  );
}
```

### 4. 文化匹配雷達圖
```typescript
// components/candidates/CultureRadar.tsx
import { Radar } from 'recharts';

export function CultureRadar({ candidateProfile, jobProfile }: Props) {
  const dimensions = [
    '創新導向', '流程導向', '團隊合作', 
    '獨立作業', '快節奏', '穩定環境',
    '彈性工時', '固定上班', '績效獎金', '穩定薪資'
  ];
  
  const data = dimensions.map((dim, i) => ({
    dimension: dim,
    candidate: candidateProfile[i],
    job: jobProfile[i]
  }));
  
  return (
    <Radar data={data}>
      <PolarGrid />
      <PolarAngleAxis dataKey="dimension" />
      <Radar name="候選人" dataKey="candidate" stroke="#8884d8" fill="#8884d8" />
      <Radar name="職缺" dataKey="job" stroke="#82ca9d" fill="#82ca9d" />
    </Radar>
  );
}
```

---

## 🔄 Google Sheets 雙向同步

### 同步策略
1. **前端操作** → PostgreSQL → Google Sheets（自動同步）
2. **Google Sheets 手動編輯** → Webhook 通知 → PostgreSQL 更新
3. **衝突處理**: PostgreSQL 為主，Sheets 為備份

### 同步腳本
```typescript
// services/sheetsSync.ts
export async function syncToSheets(candidate: Candidate) {
  const values = [
    candidate.name,           // A
    candidate.email,          // B
    candidate.phone,          // C
    // ... (20 個欄位)
  ];
  
  await gog.sheets.append(SHEET_ID, '履歷池v2!A:T', {
    values: [values]
  });
}

export async function syncFromSheets() {
  const rows = await gog.sheets.get(SHEET_ID, '履歷池v2!A:T');
  
  for (const row of rows) {
    await upsertCandidate({
      name: row[0],
      email: row[1],
      // ...
    });
  }
}
```

---

## 🚀 開發計畫

### Phase 1: 基礎架構（Week 1-2）
- [ ] 建立 PostgreSQL 資料庫（5 張表）
- [ ] 建立 Node.js 後端 API
- [ ] 建立 React 前端框架
- [ ] 實作候選人 CRUD
- [ ] Google Sheets 雙向同步

### Phase 2: AI 功能整合（Week 3-4）
- [ ] 整合 Resume Parser v2
- [ ] 整合 Stability Predictor
- [ ] 整合 Culture Matcher
- [ ] 整合 AI Matcher v3
- [ ] 視覺化組件開發

### Phase 3: 核心功能（Week 5-6）
- [ ] Kanban 看板
- [ ] 職缺管理
- [ ] AI 智慧配對頁面
- [ ] 候選人詳情頁（含時間軸）
- [ ] 進度追蹤功能

### Phase 4: 協作與分析（Week 7-8）
- [ ] 多顧問協作（Jacky/Phoebe Pipeline 分離）
- [ ] 儀表板（數據總覽）
- [ ] 成功推薦 + 保證期追蹤
- [ ] 財務分析（推薦費用、退費率）

### Phase 5: 優化與部署（Week 9-10）
- [ ] 效能優化
- [ ] 行動裝置適配
- [ ] 部署到 Zeabur
- [ ] 使用者培訓

---

## 📦 部署架構

### 技術棧
- **前端**: Vite + React 19 → Zeabur
- **後端**: Node.js + Express → Zeabur
- **資料庫**: PostgreSQL → Zeabur (或 Supabase)
- **同步**: Google Sheets API
- **檔案儲存**: Google Drive (履歷 PDF)

### 環境變數
```env
# PostgreSQL
DATABASE_URL=postgresql://...

# Google Sheets
GOOGLE_SHEETS_ID=1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q

# AI API Keys
ANTHROPIC_API_KEY=...
GOOGLE_AI_KEY=...

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS
```

---

## 🎯 成功指標

1. **效率提升**
   - 候選人搜尋時間：從 5 分鐘 → 30 秒
   - AI 配對準確率：≥ 80%
   - 履歷處理時間：從 10 分鐘 → 2 分鐘（自動解析）

2. **數據品質**
   - 穩定度評分覆蓋率：100%
   - 文化匹配完成率：≥ 60%
   - 進度記錄完整性：100%

3. **業務成效**
   - 推薦成功率：提升 25%
   - 保證期內離職率：降低 30%
   - 顧問協作效率：提升 40%

---

*Last updated: 2026-02-23 by YuQi AI 助理 🦞*
