# 前端集成指南 - 爬蟲系統到 UI 同步

**版本**: v1.0  
**目的**: 讓爬蟲系統的「今日新增」候選人自動顯示在前端 UI

---

## 📊 **現狀**

爬蟲系統上傳的候選人包含以下新欄位：

```json
{
  "status": "AI推薦",
  "recruitment_source": "自動爬蟲",
  "added_date": "2026-02-27",
  "aiMatchResult": {
    "sourced_from": "talent-sourcing-pipeline",
    "auto_sourced_at": "2026-02-27T20:52:23+08:00"
  }
}
```

---

## 🔧 **前端需要實現的功能**

### 1️⃣ 獲取「今日新增」的候選人

```typescript
// candidateService.ts

export async function getTodayNewCandidates() {
  try {
    const today = new Date().toISOString().split('T')[0]; // 2026-02-27
    
    // 方案 A：直接查詢 API 並篩選
    const response = await apiGet('/candidates?limit=2000');
    const candidates = response.data || [];
    
    // 篩選「今日新增」
    const todayNewCandidates = candidates.filter(c => {
      const addedDate = c.added_date || c.aiMatchResult?.auto_sourced_at?.split('T')[0];
      return addedDate === today;
    });
    
    return todayNewCandidates;
    
    // 方案 B：後端新增專用端點（推薦）
    // const response = await apiGet(`/candidates/today-new?date=${today}`);
    // return response.data;
    
  } catch (error) {
    console.error('獲取今日新增失敗:', error);
    return [];
  }
}
```

### 2️⃣ 更新「候選人選進匯表」頁面

在 `CandidateDashboard.tsx` 或相應元件中：

```typescript
import { useEffect, useState } from 'react';

export default function CandidateDashboard() {
  const [todayNewCount, setTodayNewCount] = useState(0);
  const [todayNewCandidates, setTodayNewCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // 頁面載入時自動獲取
    fetchTodayNew();
    
    // 設定定時刷新（每 30 秒）
    const interval = setInterval(fetchTodayNew, 30000);
    
    return () => clearInterval(interval);
  }, []);

  async function fetchTodayNew() {
    setIsLoading(true);
    try {
      const candidates = await getTodayNewCandidates();
      setTodayNewCount(candidates.length);
      setTodayNewCandidates(candidates);
    } catch (error) {
      console.error('更新今日新增失敗:', error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      {/* 已上職區域 */}
      <div className="status-box">
        <h3>已上職</h3>
        <p>0</p>
      </div>

      {/* ⭐ 今日新增區域（需要更新） */}
      <div className="today-new-box">
        <h3>✨ 今日新增（自動）</h3>
        <p>{todayNewCount}</p>
        
        {isLoading && <p>加載中...</p>}
        
        {todayNewCount === 0 ? (
          <p className="no-data">暫無候選人</p>
        ) : (
          <div className="candidate-list">
            {todayNewCandidates.map(candidate => (
              <div key={candidate.id} className="candidate-card">
                <h4>{candidate.name}</h4>
                <p>評分: {candidate.aiMatchResult?.score} 分 / {candidate.aiMatchResult?.grade} 級</p>
                <p>來源: {candidate.recruitment_source}</p>
                <p className="timestamp">
                  新增於: {candidate.added_date}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 其他部分... */}
    </div>
  );
}
```

### 3️⃣ 設定自動刷新

```typescript
// 在頁面初始化時，每次頁面回到焦點時刷新
useEffect(() => {
  function handleVisibilityChange() {
    if (!document.hidden) {
      // 頁面變為可見時，刷新數據
      fetchTodayNew();
    }
  }
  
  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  };
}, []);
```

---

## 📋 **候選人卡片顯示內容**

每個「今日新增」的候選人應該顯示：

```
┌─────────────────────────────────────┐
│ 👤 charkchalk                       │
│    評分: 89 分 / A 級               │
│    來源: 自動爬蟲                   │
│    新增於: 2026-02-27               │
│                                     │
│    技能: C++, CMake, Docker...      │
│    面試問題: 5 個                   │
│                                     │
│    [查看詳細] [聯繫] [保留]        │
└─────────────────────────────────────┘
```

---

## 🔄 **實時更新方案**

### 方案 A：定時輪詢（簡單）
```typescript
// 每 30 秒刷新一次
setInterval(() => {
  fetchTodayNew();
}, 30000);
```

**優點**: 簡單、易實現  
**缺點**: 可能延遲、浪費頻寬

### 方案 B：WebSocket（推薦）
```typescript
// 建立 WebSocket 連接
const ws = new WebSocket('wss://backendstep1ne.zeabur.app/ws/candidates');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'new_candidate') {
    // 新候選人被新增
    setTodayNewCandidates(prev => [...prev, data.candidate]);
    setTodayNewCount(prev => prev + 1);
  }
};
```

**優點**: 實時推送、高效  
**缺點**: 需要後端支援

### 方案 C：輪詢 + 本地快取（平衡）
```typescript
const [lastFetchTime, setLastFetchTime] = useState(null);

async function fetchTodayNew() {
  const now = Date.now();
  
  // 如果距離上次刷新 < 10 秒，使用快取
  if (lastFetchTime && now - lastFetchTime < 10000) {
    return;
  }
  
  // 否則重新獲取
  const candidates = await getTodayNewCandidates();
  setTodayNewCandidates(candidates);
  setLastFetchTime(now);
}
```

---

## 🎯 **數據欄位對應**

| 前端顯示 | 後端欄位 | 數據類型 | 用途 |
|---------|---------|---------|------|
| 新增人數 | `added_date === 今天` 的個數 | int | 計數 |
| 候選人名字 | `name` | string | 顯示 |
| 評分 | `aiMatchResult.score` | int | 顯示 |
| 等級 | `aiMatchResult.grade` | string (A+/A/B/C/D) | 顯示 |
| 來源 | `recruitment_source` | string | 顯示 |
| 新增日期 | `added_date` | YYYY-MM-DD | 篩選 |
| 技能 | `aiMatchResult.matched_skills` | array | 顯示 |
| 面試問題數 | `aiMatchResult.probing_questions.length` | int | 顯示 |

---

## ✅ **實作檢查清單**

- [ ] **步驟 1**: 在 `candidateService.ts` 新增 `getTodayNewCandidates()` 函數
- [ ] **步驟 2**: 更新 Dashboard 頁面的「今日新增」區域
- [ ] **步驟 3**: 設定自動刷新（30 秒或頁面回焦點時）
- [ ] **步驟 4**: 新增候選人卡片元件，顯示評分、來源、新增日期
- [ ] **步驟 5**: 測試：爬蟲上傳後，前端應自動顯示新人選
- [ ] **步驟 6**: （可選）實現 WebSocket 實時推送

---

## 🧪 **測試步驟**

### 1. 運行爬蟲
```bash
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id 51 --execute
```

### 2. 查詢 API 驗證數據
```bash
curl https://backendstep1ne.zeabur.app/api/candidates/540 | jq '.data | {name, added_date, recruitment_source, aiMatchResult: {score, grade, auto_sourced_at}}'
```

**預期輸出**：
```json
{
  "name": "charkchalk",
  "added_date": "2026-02-27",
  "recruitment_source": "自動爬蟲",
  "aiMatchResult": {
    "score": 89,
    "grade": "A",
    "auto_sourced_at": "2026-02-27T20:52:23+08:00"
  }
}
```

### 3. 檢查前端
- 進入 https://step1ne.zeabur.app
- 進入「候選人選進匯表」頁面
- 檢查「✨ 今日新增（自動）」區域
- 應該看到新增的候選人（不再是 0）

---

## 🔗 **相關 API 端點**

| 端點 | 方法 | 說明 |
|------|------|------|
| `/candidates` | GET | 獲取所有候選人 |
| `/candidates/{id}` | GET | 獲取單個候選人（包括 added_date） |
| `/candidates?added_date=2026-02-27` | GET | 獲取特定日期的候選人（需後端實現） |
| `/candidates/today-new` | GET | 獲取今日新增（推薦後端新增此端點） |

---

## 📝 **後端建議新增端點**

如果後端可以新增，會大幅簡化前端：

```javascript
// Express.js 範例
app.get('/api/candidates/today-new', async (req, res) => {
  const today = new Date().toISOString().split('T')[0];
  
  const candidates = await db.candidates.find({
    added_date: today
  });
  
  res.json({
    data: candidates,
    count: candidates.length
  });
});
```

---

## 🎉 **完成後的效果**

- ✅ 爬蟲運行 → 自動上傳候選人
- ✅ 候選人帶上 `added_date` 標記
- ✅ 前端自動刷新
- ✅ 「✨ 今日新增（自動）」區域顯示新候選人
- ✅ 使用者可以實時看到爬蟲成果

---

**下一步**: 將此文件交給前端團隊，他們可以按步驟實現前端集成！
