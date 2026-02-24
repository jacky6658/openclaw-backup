# AI 配對推薦功能完整設計方案

**時間**：2026-02-23  
**目的**：回答 Jacky 關於 AI 配對推薦流程的 4 個問題

---

## 📋 Q1：獵頭顧問提供人選履歷的流程是？

### 當前流程（已實作）✅

#### 方式 1：手動上傳（Phase 1 已完成）
```
獵頭顧問在系統中發現候選人
  ↓
點擊「下載履歷」按鈕
  ↓
LinkedIn 自動開啟新分頁
  ↓
手動點擊「...」→「存為 PDF」
  ↓
選擇檔案上傳（系統自動開啟檔案選擇器）
  ↓
後端自動處理：
  1. 上傳到 Google Drive（按狀態分類）
  2. AI 解析履歷（email, phone, skills, work history）
  3. 更新 Google Sheets 資料
  4. 觸發重新評級（S/A+/A/B/C）
  ↓
完成！候選人資料補全
```

#### 方式 2：Bot 自動搜尋（每日 3 次）✅
```
Sourcing Bot（Cron 自動執行）
  ↓
讀取「step1ne 職缺管理」表的「招募中」職缺
  ↓
LinkedIn + GitHub 多管道搜尋
  ↓
AI 自動配對評分（P0/P1/P2）
  ↓
去重處理（避免重複匯入）
  ↓
批量匯入履歷池
  ↓
Telegram 通知（Topic 304）：
  • 找到幾位候選人
  • Top 5 推薦
  • 配對分數
```

#### 方式 3：Gmail 自動進件（每小時）✅
```
候選人投遞履歷到 aijessie88@step1ne.com
  ↓
系統每小時檢查 inbox
  ↓
AI 解析 PDF 履歷
  ↓
自動匯入履歷池
  ↓
Telegram 通知（Topic 4 履歷進件）：
  • 候選人姓名
  • 應徵職位
  • 負責顧問（Jacky/Phoebe）
```

---

## 🤖 Q2：AI Bot 如何分析人選與職缺的匹配度？

### 技術架構

#### 核心模組：AI Matcher v2
**位置**：`/Users/user/clawd/hr-tools/ai_matcher_v2.py`

**4 維度評分系統**：
```python
總分 = (
  技能匹配 × 40% +
  年資匹配 × 30% +
  學歷匹配 × 20% +
  穩定度 × 10%
)
```

#### 維度 1：技能匹配 (40%)
```python
def calculate_skill_match(candidate_skills, required_skills):
    # 必備技能檢查
    matched = len(set(candidate_skills) & set(required_skills))
    total = len(required_skills)
    
    # 基礎分
    score = (matched / total) * 100
    
    # 額外技能加分（深度 vs 廣度）
    extra_skills = len(candidate_skills) - matched
    bonus = min(extra_skills * 2, 10)  # 上限 10 分
    
    return min(score + bonus, 100)

# 範例
candidate = ["Python", "TensorFlow", "PyTorch", "Docker", "AWS"]
required = ["Python", "TensorFlow", "PyTorch"]
# matched: 3/3 = 100 分
# extra: 2 技能 → +4 分
# 總分：100 分（上限）
```

#### 維度 2：年資匹配 (30%)
```python
def calculate_experience_match(candidate_years, required_years):
    if candidate_years >= required_years:
        # 達標
        over_qualified = candidate_years - required_years
        if over_qualified <= 2:
            return 100  # 完美
        else:
            # 過度資深（可能薪資期望過高）
            penalty = min((over_qualified - 2) * 5, 20)
            return 100 - penalty
    else:
        # 不達標
        gap = required_years - candidate_years
        penalty = gap * 20
        return max(100 - penalty, 0)

# 範例
candidate_years = 5
required_years = 3
# 達標，超過 2 年 → 100 分

candidate_years = 2
required_years = 3
# 差 1 年 → 100 - 20 = 80 分
```

#### 維度 3：學歷匹配 (20%)
```python
EDUCATION_LEVELS = {
    "博士": 4,
    "碩士": 3,
    "學士": 2,
    "專科": 1,
    "高中": 0
}

def calculate_education_match(candidate_edu, required_edu):
    candidate_level = EDUCATION_LEVELS.get(candidate_edu, 0)
    required_level = EDUCATION_LEVELS.get(required_edu, 0)
    
    if candidate_level >= required_level:
        return 100  # 達標
    else:
        gap = required_level - candidate_level
        return max(100 - gap * 25, 0)

# 範例
candidate_edu = "碩士" (3)
required_edu = "學士" (2)
# 達標 → 100 分

candidate_edu = "學士" (2)
required_edu = "碩士" (3)
# 差 1 級 → 100 - 25 = 75 分
```

#### 維度 4：穩定度 (10%)
```python
def calculate_stability_match(stability_score):
    # 穩定度評分已經是 0-100 的範圍
    # 直接採用（不做轉換）
    return stability_score

# 範例
stability_score = 85  # A 級穩定度
# 直接使用 85 分
```

### 配對分級標準

```python
def get_priority_level(total_score):
    if total_score >= 80:
        return "P0"  # 完美匹配（強力推薦）
    elif total_score >= 60:
        return "P1"  # 高度匹配（推薦）
    elif total_score >= 40:
        return "P2"  # 中度匹配（可考慮）
    else:
        return "P3"  # 不匹配（不推薦）
```

### 實際應用範例

**職缺**：AI 工程師
- 必備技能：Python, TensorFlow, PyTorch
- 年資要求：3 年
- 學歷要求：學士
- 薪資：80k-120k

**候選人 A**：張大明
```json
{
  "name": "張大明",
  "skills": ["Python", "TensorFlow", "PyTorch", "Docker", "Kubernetes"],
  "experience": 5,
  "education": "碩士",
  "stability": 85
}
```

**配對計算**：
```
技能匹配：100 分（3/3 必備技能 + 2 額外技能）× 40% = 40
年資匹配：100 分（5年 ≥ 3年，超過 2 年）× 30% = 30
學歷匹配：100 分（碩士 ≥ 學士）× 20% = 20
穩定度：85 分 × 10% = 8.5
────────────────────────────
總分：98.5 分 → P0（完美匹配）✅
```

**候選人 B**：李小華
```json
{
  "name": "李小華",
  "skills": ["Python", "scikit-learn", "pandas"],
  "experience": 2,
  "education": "學士",
  "stability": 70
}
```

**配對計算**：
```
技能匹配：33 分（1/3 必備技能，缺 TensorFlow + PyTorch）× 40% = 13.2
年資匹配：80 分（差 1 年 → -20）× 30% = 24
學歷匹配：100 分（學士 = 學士）× 20% = 20
穩定度：70 分 × 10% = 7
────────────────────────────
總分：64.2 分 → P1（高度匹配）⚠️
```

---

## 📄 Q3：交付物會有匹配度報告嗎？

### ✅ 目前已有的報告（Telegram 通知）

**每次搜尋完成後自動產生**：
```
🔍 職缺：AI工程師
📊 搜尋完成

管道：LinkedIn (20位) + GitHub (10位)
找到：30 位候選人

=== 🏆 Top 5 推薦 ===

1. 張大明 - P0 (98.5分) ⭐⭐⭐⭐⭐
   • 技能：Python, TensorFlow, PyTorch, Docker, K8s
   • 年資：5 年（超標）
   • 學歷：碩士
   • 穩定度：85 分（A級）
   • LinkedIn: https://...
   📌 匹配原因：技能完全符合，年資充足，穩定度高

2. 李小華 - P1 (72分) ⭐⭐⭐⭐
   • 技能：Python, TensorFlow, AI
   • 年資：3 年（剛好）
   • 學歷：學士
   • 穩定度：70 分（B級）
   • GitHub: https://...
   📌 匹配原因：核心技能符合，年資達標

（... 其他 3 位）

=== 📈 配對統計 ===
• P0（完美匹配）: 5 位 ← 強力推薦
• P1（高度匹配）: 10 位 ← 推薦
• P2（中度匹配）: 12 位 ← 可考慮
• P3（不匹配）: 3 位 ← 不推薦
────────────────
✅ 已匯入 27 位到履歷池（P3 已過濾）
📍 位置：履歷池v2 第 250-277 行
```

### 🆕 建議新增：完整 PDF 匹配度報告

**應該包含的內容**：

#### 1. 封面
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Step1ne 人才配對分析報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

職缺：AI工程師
客戶：遊戲橘子股份有限公司
配對日期：2026-02-23
配對顧問：Jacky Chen

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 2. 職缺需求總覽
```
📋 職缺資訊

職位：AI工程師
部門：技術部
人數：2 人
薪資範圍：80k-120k

必備技能：
  • Python（熟練）
  • TensorFlow / PyTorch（至少一種）
  • 機器學習基礎
  • 資料處理（pandas, numpy）

年資要求：3 年以上 AI/ML 相關經驗
學歷要求：資訊相關學士以上
```

#### 3. 候選人推薦清單（分級）

```
🏆 P0 級候選人（5 位）- 強力推薦

────────────────────────────
1. 張大明 | P0 (98.5分) ⭐⭐⭐⭐⭐
────────────────────────────

【基本資料】
  • 年資：5 年
  • 學歷：台大資工碩士
  • 目前職位：資深 AI 工程師 @ Google
  • 期望薪資：100k-130k

【技能匹配】100/100 ✅
  必備技能：✓ Python, ✓ TensorFlow, ✓ PyTorch
  額外技能：Docker, Kubernetes, AWS, CI/CD
  
【年資匹配】100/100 ✅
  要求 3 年，實際 5 年（超標 2 年）
  
【學歷匹配】100/100 ✅
  要求學士，實際碩士（台大資工）
  
【穩定度】85/100 (A級) ✅
  工作經歷：3 份工作，平均任期 2.5 年
  
【工作經歷】
  1. Google - 資深 AI 工程師 (2021-2026, 5年)
  2. Microsoft - AI 工程師 (2018-2021, 3年)
  3. Startup - ML 工程師 (2016-2018, 2年)

【推薦原因】
  ✓ 技能完全符合，且有大廠（Google）經驗
  ✓ 年資充足，穩定度高
  ✓ 台大碩士背景，技術實力強
  ⚠️ 薪資期望略高（可能需要 120k+）

【聯繫方式】
  • Email: zhang@example.com
  • Phone: 0912-345-678
  • LinkedIn: https://linkedin.com/in/...
  • GitHub: https://github.com/...

────────────────────────────

（... 其他 4 位 P0 候選人）
```

#### 4. 配對分析圖表

```
📊 候選人分布

配對等級分布：
P0 ████████████ 5 位 (16.7%)
P1 ████████████████████ 10 位 (33.3%)
P2 ████████████████████████ 12 位 (40%)
P3 ██████ 3 位 (10%)

技能符合度分布：
100% ████████ 8 位
80-99% ████████████ 12 位
60-79% ██████ 6 位
<60% ████ 4 位

年資分布：
10年+ ████ 2 位
7-10年 ██████ 3 位
5-7年 ████████ 4 位
3-5年 ██████████████ 7 位
1-3年 ████████████ 6 位
<1年 ████ 2 位
```

#### 5. 推薦策略與後續步驟

```
💡 推薦策略

優先聯繫（P0 級，5 位）：
  1. 張大明（98.5分）- 技術實力最強
  2. 王小明（95分）- 薪資期望合理
  3. 陳大華（92分）- 穩定度最高
  4. 李建國（88分）- 即戰力
  5. 林志玲（85分）- 潛力股

備選名單（P1 級，10 位）：
  • 適合第二輪面試
  • 如果 P0 候選人不合適時啟用

📅 建議時程：
  • Week 1: 聯繫 P0 候選人（5 位）
  • Week 2: 安排初步面試
  • Week 3: 技術測試 + 二面
  • Week 4: Offer 協商

⚠️ 風險提示：
  • 市場競爭激烈，AI 工程師薪資持續上漲
  • 建議提高薪資上限至 130k 以吸引頂尖人才
  • P0 候選人可能同時面試多家公司
```

#### 6. 附錄

```
📎 附錄

A. 配對評分演算法說明
B. 技能匹配度計算細節
C. 穩定度評分標準
D. 候選人完整履歷（PDF 附件）
E. 聯繫記錄表（空白模板）
```

---

## 🖥️ Q4：左側 Sidebar「AI 配對推薦」功能如何實現？

### 目前狀態

**檢查結果**：
```javascript
// components/Sidebar.tsx
{ 
  id: 'ai-matching', 
  label: '🤖 AI 配對推薦', 
  icon: CheckSquare, 
  roles: [Role.ADMIN, Role.REVIEWER],
  disabled: true,  ← 目前停用
  badge: '即將推出' 
}
```

### 完整實作方案

#### 方案 A：統一配對池（推薦）✅

**設計邏輯**：
- **所有顧問**都能看到「AI 配對推薦」頁面
- **但只顯示該顧問負責的職缺**的配對結果
- 使用 `userProfile.consultant` 欄位過濾

**實作步驟**：

##### Step 1: 建立 AI 配對推薦頁面
```typescript
// pages/AIMatchingPage.tsx

import React, { useState, useEffect } from 'react';
import { UserProfile } from '../types';

interface AIMatchingPageProps {
  userProfile: UserProfile;
}

export const AIMatchingPage: React.FC<AIMatchingPageProps> = ({ userProfile }) => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  // 載入該顧問負責的職缺
  useEffect(() => {
    fetchJobsByConsultant(userProfile.consultant);
  }, [userProfile]);

  const fetchJobsByConsultant = async (consultant: string) => {
    // 從 Google Sheets 讀取
    const response = await fetch(`/api/jobs?consultant=${consultant}`);
    const data = await response.json();
    setJobs(data.jobs);
  };

  const runMatching = async (jobId: string) => {
    setLoading(true);
    
    // 呼叫後端 API 執行配對
    const response = await fetch('/api/ai-matching/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        jobId,
        consultant: userProfile.consultant  // 只配對該顧問的候選人
      })
    });
    
    const data = await response.json();
    setMatches(data.matches);
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">🤖 AI 配對推薦</h1>
      
      {/* 職缺選擇 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <label className="block text-sm font-medium mb-2">
          選擇職缺（您負責的職缺）
        </label>
        <select 
          className="w-full border rounded px-3 py-2"
          onChange={(e) => setSelectedJob(e.target.value)}
        >
          <option value="">請選擇...</option>
          {jobs.map(job => (
            <option key={job.id} value={job.id}>
              {job.title} - {job.company}
            </option>
          ))}
        </select>
        
        <button
          onClick={() => runMatching(selectedJob)}
          disabled={!selectedJob || loading}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          {loading ? '配對中...' : '開始配對'}
        </button>
      </div>
      
      {/* 配對結果 */}
      {matches.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">配對結果（共 {matches.length} 位）</h2>
          
          {['P0', 'P1', 'P2'].map(priority => {
            const filtered = matches.filter(m => m.priority === priority);
            if (filtered.length === 0) return null;
            
            return (
              <div key={priority} className="bg-white rounded-lg shadow p-4">
                <h3 className="font-medium mb-3">
                  {priority} 級候選人（{filtered.length} 位）
                </h3>
                
                <div className="space-y-2">
                  {filtered.map(match => (
                    <MatchCard key={match.candidateId} match={match} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// 配對卡片組件
const MatchCard: React.FC<{ match: any }> = ({ match }) => {
  return (
    <div className="border rounded p-4 hover:bg-gray-50">
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium">{match.name}</h4>
          <p className="text-sm text-gray-600">{match.position}</p>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-blue-600">
            {match.score} 分
          </div>
          <div className="text-xs text-gray-500">
            {match.priority}
          </div>
        </div>
      </div>
      
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-500">技能：</span>
          <span className="font-medium">{match.skillMatch}%</span>
        </div>
        <div>
          <span className="text-gray-500">年資：</span>
          <span className="font-medium">{match.experienceMatch}%</span>
        </div>
        <div>
          <span className="text-gray-500">學歷：</span>
          <span className="font-medium">{match.educationMatch}%</span>
        </div>
        <div>
          <span className="text-gray-500">穩定度：</span>
          <span className="font-medium">{match.stabilityScore}</span>
        </div>
      </div>
      
      <div className="mt-3 flex gap-2">
        <button className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded">
          查看履歷
        </button>
        <button className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded">
          聯繫候選人
        </button>
        <button className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded">
          產生報告
        </button>
      </div>
    </div>
  );
};
```

##### Step 2: 後端 API 實作

```javascript
// server/server.js

// AI 配對 API
app.post('/api/ai-matching/run', async (req, res) => {
  try {
    const { jobId, consultant } = req.body;
    
    // 1. 讀取職缺資訊
    const job = await getJobById(jobId);
    
    // 2. 讀取該顧問的候選人池
    const candidates = await getCandidatesByConsultant(consultant);
    
    // 3. 執行 AI 配對
    const matcherScript = path.join(__dirname, '../../hr-tools/ai_matcher_v2.py');
    const tempJobFile = `/tmp/job-${jobId}.json`;
    const tempCandidatesFile = `/tmp/candidates-${consultant}.json`;
    const outputFile = `/tmp/matches-${jobId}-${Date.now()}.json`;
    
    // 寫入臨時檔案
    fs.writeFileSync(tempJobFile, JSON.stringify(job));
    fs.writeFileSync(tempCandidatesFile, JSON.stringify(candidates));
    
    // 執行 Python 腳本
    execSync(`python3 "${matcherScript}" \
      --job "${tempJobFile}" \
      --candidates "${tempCandidatesFile}" \
      --output "${outputFile}"`, 
      { encoding: 'utf-8' }
    );
    
    // 讀取結果
    const matches = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
    
    // 清理臨時檔案
    fs.unlinkSync(tempJobFile);
    fs.unlinkSync(tempCandidatesFile);
    fs.unlinkSync(outputFile);
    
    res.json({
      success: true,
      matches,
      count: matches.length,
      jobId,
      consultant
    });
  } catch (error) {
    console.error('AI 配對失敗:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// 產生 PDF 報告
app.post('/api/ai-matching/report', async (req, res) => {
  try {
    const { jobId, matches } = req.body;
    
    // 使用 ai-pdf-builder skill 產生報告
    const reportScript = path.join(__dirname, '../../clawd/skills/installed/ai-pdf-builder/generate.sh');
    
    const reportData = {
      title: `人才配對分析報告 - ${job.title}`,
      job,
      matches,
      generatedAt: new Date().toISOString()
    };
    
    const tempDataFile = `/tmp/report-data-${Date.now()}.json`;
    const outputPdf = `/tmp/report-${jobId}-${Date.now()}.pdf`;
    
    fs.writeFileSync(tempDataFile, JSON.stringify(reportData));
    
    execSync(`bash "${reportScript}" "${tempDataFile}" "${outputPdf}"`,
      { encoding: 'utf-8' }
    );
    
    // 返回 PDF 檔案
    res.download(outputPdf, `配對報告-${job.title}-${Date.now()}.pdf`, () => {
      fs.unlinkSync(tempDataFile);
      fs.unlinkSync(outputPdf);
    });
  } catch (error) {
    console.error('產生報告失敗:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});
```

##### Step 3: 啟用 Sidebar 選項

```typescript
// components/Sidebar.tsx

{ 
  id: 'ai-matching', 
  label: '🤖 AI 配對推薦', 
  icon: CheckSquare, 
  roles: [Role.ADMIN, Role.REVIEWER],
  disabled: false,  // ← 改為 false
  badge: null       // ← 移除「即將推出」
}
```

##### Step 4: App.tsx 路由

```typescript
// App.tsx

case 'ai-matching': 
  return <AIMatchingPage userProfile={profile} />;
```

---

### 多顧問區分邏輯

#### 資料隔離策略

```javascript
// 1. 職缺過濾（只顯示該顧問負責的職缺）
const getJobsByConsultant = (consultant: string) => {
  return jobs.filter(job => job.consultant === consultant);
};

// 2. 候選人過濾（只配對該顧問的候選人池）
const getCandidatesByConsultant = (consultant: string) => {
  return candidates.filter(c => c.consultant === consultant);
};

// 3. 配對結果過濾（只顯示該顧問的配對）
const getMatchesByConsultant = (consultant: string) => {
  return matches.filter(m => m.consultant === consultant);
};
```

#### 權限矩陣

| 角色 | 可看到的職缺 | 可看到的候選人 | 可看到的配對結果 |
|------|------------|--------------|----------------|
| **Admin** | 全部職缺 | 全部候選人 | 全部配對結果 |
| **Jacky** | Jacky 負責的職缺 | Jacky 負責的候選人 | Jacky 的配對結果 |
| **Phoebe** | Phoebe 負責的職缺 | Phoebe 負責的候選人 | Phoebe 的配對結果 |

#### 實作範例

```typescript
// 根據用戶角色動態過濾
const fetchData = async (userProfile: UserProfile) => {
  const isAdmin = userProfile.role === Role.ADMIN;
  
  if (isAdmin) {
    // 管理員：看到全部
    const allJobs = await fetchAllJobs();
    const allCandidates = await fetchAllCandidates();
    return { jobs: allJobs, candidates: allCandidates };
  } else {
    // 顧問：只看到自己的
    const myJobs = await fetchJobsByConsultant(userProfile.consultant);
    const myCandidates = await fetchCandidatesByConsultant(userProfile.consultant);
    return { jobs: myJobs, candidates: myCandidates };
  }
};
```

---

## 🎯 總結與建議

### 當前狀態（已完成）✅

1. ✅ **履歷上傳流程**（Phase 1）
2. ✅ **AI 配對核心模組**（ai_matcher_v2.py）
3. ✅ **Telegram 通知報告**（基礎版）
4. ✅ **多顧問資料隔離**（Google Sheets 欄位）

### 待實作項目（優先級排序）

#### P0（高優先級）- 本週完成
1. **AI 配對推薦頁面**（前端）
   - 職缺選擇
   - 一鍵配對
   - 結果展示
   - 預計時間：4 小時

2. **配對 API 端點**（後端）
   - POST /api/ai-matching/run
   - 呼叫 Python 腳本
   - 回傳結果
   - 預計時間：2 小時

#### P1（中優先級）- 下週完成
3. **PDF 報告產生**
   - 使用 ai-pdf-builder skill
   - 完整的配對分析報告
   - 預計時間：3 小時

4. **配對歷史記錄**
   - 儲存每次配對結果
   - 可查詢歷史報告
   - 預計時間：2 小時

#### P2（低優先級）- 未來優化
5. **自動配對提醒**
   - 新職缺自動觸發配對
   - Telegram 通知
   - 預計時間：1 小時

6. **配對結果優化**
   - 加入文化匹配度
   - 加入薪資匹配度
   - 預計時間：3 小時

---

## 🚀 下一步行動

建議執行順序：

**本週（2/24-2/28）**：
1. ✅ 確認 AI 配對推薦頁面設計（UI/UX）
2. ✅ 實作前端頁面（AIMatchingPage.tsx）
3. ✅ 實作後端 API（/api/ai-matching/run）
4. ✅ 測試單一顧問配對流程
5. ✅ 測試多顧問資料隔離

**下週（3/3-3/7）**：
6. ✅ 實作 PDF 報告產生
7. ✅ 整合配對歷史記錄
8. ✅ 完整測試（Jacky + Phoebe 雙顧問）

---

**要開始實作嗎？建議從 P0-1（AI 配對推薦頁面）開始！** 🦞
