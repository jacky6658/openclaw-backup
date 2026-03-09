# Level 3 自動找人選實作計畫
**目標**: AI 全自動化（人工只需審核）  
**制定日期**: 2026-02-12  
**預計完成**: 2026-03-31（6-8 週）

---

## 🎯 Level 3 定義

### 自動化範圍
- ✅ AI 自動搜尋候選人（多渠道）
- ✅ AI 自動配對 + 排序
- ✅ AI 自動發送聯絡訊息
- ✅ AI 自動追蹤回覆
- ✅ AI 自動整理候選人資料
- ✅ AI 自動更新 Pipeline 表

### 人工職責（只剩這些）
- ❌ 搜尋候選人 → AI 做
- ❌ 配對評分 → AI 做
- ❌ 發送訊息 → AI 做
- ❌ 追蹤回覆 → AI 做
- ✅ **審核推薦結果** ← 人工決定是否推薦給客戶
- ✅ **電話面試** ← 人工執行
- ✅ **客戶溝通** ← 人工執行
- ✅ **最終錄用協商** ← 人工執行

**節省時間**: 從 100% 人工 → 70-80% 自動化

---

## 📅 分階段實作計畫

### Phase 1: 基礎自動化（Week 1-2，2/17-2/28）

**目標**: 一鍵搜尋 + AI 配對

#### Week 1 (2/17-2/23)
**任務**:
1. **整合多渠道搜尋**
   ```bash
   # 一鍵指令
   ./auto-sourcing.sh <JD_ID>
   
   # 自動執行：
   # 1. 讀取 JD（從 Google Sheets）
   # 2. AI 提取關鍵字（技能、經驗、地點）
   # 3. 平行搜尋：
   #    - GitHub（技術職）
   #    - 履歷池配對
   #    - Google 搜尋目標公司員工
   # 4. AI 統一打分 + 排序
   # 5. 輸出候選人清單（Top 20）
   ```

2. **建立候選人資料結構**
   ```json
   {
     "candidate_id": "uuid",
     "name": "候選人姓名",
     "source": "github|linkedin|resume_pool|google",
     "contact": {
       "email": "...",
       "phone": "...",
       "linkedin": "..."
     },
     "profile": {
       "current_title": "...",
       "company": "...",
       "skills": [...],
       "experience_years": 5
     },
     "matching": {
       "jd_id": "...",
       "score": 85,
       "reasons": ["中文系畢業", "製造業背景", "財會經驗 10+ 年"]
     },
     "status": "found|contacted|replied|interviewed|recommended|rejected",
     "created_at": "2026-02-12T19:45:00Z"
   }
   ```

3. **測試 3 個 JD**
   - 志邦企業財會主管
   - 美德醫療會計協理
   - 某技術職缺（AI 工程師）

**交付**:
- ✅ `auto-sourcing.sh` 可用
- ✅ 每個 JD 可找到 10-20 個候選人
- ✅ AI 配對準確度 ≥70%

---

#### Week 2 (2/24-2/28)
**任務**:
1. **建立候選人資料庫**
   ```bash
   # PostgreSQL 或 SQLite
   candidates/
   ├── database.db
   ├── schema.sql
   └── migrations/
   ```

2. **API 端點設計**
   ```
   GET  /api/candidates              # 列出候選人
   GET  /api/candidates/:id          # 查看候選人
   POST /api/candidates/search       # 搜尋候選人（執行 auto-sourcing.sh）
   PUT  /api/candidates/:id/status   # 更新狀態
   GET  /api/candidates/match/:jd_id # 配對結果
   ```

3. **測試資料積累**
   - 執行 5 個 JD 搜尋
   - 累積 50-100 個候選人資料

**交付**:
- ✅ 候選人資料庫建立
- ✅ API Server 可用
- ✅ 資料持久化（不會遺失）

---

### Phase 2: 自動聯絡（Week 3-4，3/3-3/14）

**目標**: AI 自動發送訊息 + 追蹤回覆

#### Week 3 (3/3-3/9)
**任務**:
1. **AI 訊息生成**
   ```python
   # 根據候選人背景 + JD 生成個人化訊息
   def generate_outreach_message(candidate, jd):
       prompt = f"""
       候選人背景：{candidate.profile}
       職位需求：{jd.requirements}
       
       生成一封專業的聯絡訊息（<200 字）：
       1. 提及候選人的獨特背景
       2. 說明職位吸引力
       3. 邀請進一步討論
       """
       return ai_call(prompt)
   ```

2. **多渠道發送機制**
   - LinkedIn InMail（免費版 3/月，付費版 30/月）
   - Email（如果有 Email）
   - WhatsApp（如果有電話號碼）

3. **發送限制與排程**
   ```python
   # 避免被封鎖
   LIMITS = {
       "linkedin_free": 3/month,
       "linkedin_premium": 30/month,
       "email": 50/day,
       "whatsapp": 20/day
   }
   
   # 智能排程
   # 優先用 Email（無限制）
   # LinkedIn 留給高優先候選人
   # WhatsApp 作為最後手段
   ```

**交付**:
- ✅ AI 生成訊息可用
- ✅ 多渠道發送機制建立
- ✅ 測試發送 10 個候選人

---

#### Week 4 (3/10-3/14)
**任務**:
1. **自動追蹤回覆**
   ```python
   # 每天檢查
   def check_replies():
       # LinkedIn: 爬取收件匣
       # Email: Gmail API
       # WhatsApp: wacli
       
       for reply in new_replies:
           candidate = find_candidate(reply.from)
           update_status(candidate, "replied")
           
           # AI 判斷回覆意願
           intent = ai_classify_intent(reply.message)
           # "interested" | "not_interested" | "need_info"
           
           if intent == "interested":
               notify_jacky(candidate, reply)
           elif intent == "need_info":
               auto_reply = ai_generate_reply(reply.message)
               send_message(candidate, auto_reply)
   ```

2. **自動回覆機制**
   - 候選人問薪資 → AI 自動回覆範圍
   - 候選人問公司 → AI 自動提供簡介
   - 候選人表達興趣 → 通知 Jacky

3. **Telegram 通知整合**
   ```
   📬 新回覆（候選人：Soun Mara）
   
   職位：志邦企業財會主管
   回覆內容：「我對這個職位很感興趣，可以了解更多嗎？」
   
   AI 判斷：✅ 高度興趣
   建議行動：安排電話面試
   
   [查看完整對話] [安排面試] [標記為不合適]
   ```

**交付**:
- ✅ 自動追蹤回覆可用
- ✅ AI 自動回覆常見問題
- ✅ Telegram 通知整合

---

### Phase 3: 完整自動化（Week 5-6，3/17-3/28）

**目標**: 端到端自動化流程

#### Week 5 (3/17-3/23)
**任務**:
1. **完整流程整合**
   ```
   新 JD 進來 → AI 自動搜尋 → AI 自動配對 → AI 自動發送
   → AI 自動追蹤 → AI 自動回覆 → 通知 Jacky 審核
   ```

2. **Cron Job 設定**
   ```cron
   # 每天早上 9:00 檢查新 JD
   0 9 * * * /Users/user/clawd/hr-tools/auto-sourcing-cron.sh
   
   # 每天 14:00 檢查回覆
   0 14 * * * /Users/user/clawd/hr-tools/auto-reply-check.sh
   
   # 每天晚上 21:00 發送候選人進度報告
   0 21 * * * /Users/user/clawd/hr-tools/auto-sourcing-report.sh
   ```

3. **自動更新 Pipeline 表**
   ```python
   # 每次狀態變更時自動更新
   def update_pipeline(candidate):
       row = find_or_create_row(candidate)
       sheets.update(row, {
           "候選人": candidate.name,
           "職位": candidate.jd.title,
           "企業": candidate.jd.company,
           "狀態": candidate.status,
           "日期": today(),
           "備註": candidate.notes
       })
   ```

**交付**:
- ✅ 完整自動化流程可運作
- ✅ Cron Jobs 設定完成
- ✅ Pipeline 表自動更新

---

#### Week 6 (3/24-3/28)
**任務**:
1. **效能優化**
   - 搜尋速度優化（平行處理）
   - 資料庫查詢優化
   - API 回應速度優化

2. **錯誤處理**
   - API rate limit 應對
   - 網路錯誤重試
   - 資料品質檢查

3. **監控與告警**
   - 搜尋失敗告警
   - 發送失敗告警
   - 回覆檢查失敗告警

**交付**:
- ✅ 系統穩定運作
- ✅ 錯誤自動恢復
- ✅ 監控儀表板

---

### Phase 4: 優化與擴展（Week 7-8，3/31-4/11）

**目標**: 智能化與規模化

#### Week 7 (3/31-4/6)
**任務**:
1. **AI 學習優化**
   ```python
   # 追蹤成功率
   def track_success(candidate):
       if candidate.status == "hired":
           # 學習：這種背景的候選人容易成功
           update_scoring_model(candidate.profile)
   ```

2. **A/B 測試**
   - 不同訊息模板測試
   - 不同發送時間測試
   - 不同渠道效果比較

3. **自動化報告**
   ```
   📊 本週招募報告
   
   新增 JD：3 個
   搜尋候選人：45 個
   發送訊息：32 個
   收到回覆：18 個（回覆率 56%）
   安排面試：5 個
   推薦給客戶：3 個
   
   效能最佳渠道：Email（回覆率 62%）
   效能最佳時段：週二 10:00（回覆率 71%）
   ```

**交付**:
- ✅ AI 持續學習優化
- ✅ 數據驅動決策
- ✅ 自動化報告生成

---

#### Week 8 (4/7-4/11)
**任務**:
1. **規模化測試**
   - 同時處理 10+ 個 JD
   - 候選人池 >500 人
   - 每天發送 50+ 訊息

2. **多人協作支援**
   - Jacky Pipeline 表
   - Phoebe Pipeline 表
   - 自動分配候選人

3. **文檔化**
   - 完整操作手冊
   - 故障排除指南
   - 最佳實踐文檔

**交付**:
- ✅ 系統可規模化運作
- ✅ 多人協作順暢
- ✅ 完整文檔交付

---

## 💰 成本評估

### 免費方案（Phase 1-2）
- GitHub API: $0
- Gmail API: $0
- Google Sheets API: $0
- 履歷池: $0
- **總成本**: $0/月

### 付費升級（Phase 3-4，建議）
- **LinkedIn Recruiter Lite**: $170 USD/月 (~5,000 TWD)
  - 30 InMails/月
  - 進階搜尋
  - 候選人追蹤
- **104 企業版**: ~2,500 TWD/月
  - 搜尋求職者
  - 查看履歷
  - 主動邀約
- **伺服器 (VPS)**: ~500 TWD/月
  - DigitalOcean Droplet (2GB RAM)
  - 24/7 運行
- **總成本**: ~8,000 TWD/月

### ROI 計算
**假設**:
- 每月成功推薦 2 個候選人
- 平均年薪 100 萬
- 收費 20%

**月收入**: 200,000 × 2 = 400,000 TWD  
**月成本**: 8,000 TWD  
**淨利**: 392,000 TWD  
**ROI**: 4,900%

---

## 📊 關鍵指標（KPI）

### 搜尋效率
- 每個 JD 搜尋時間 <30 分鐘
- 每個 JD 候選人數 ≥20 個
- AI 配對準確度 ≥70%

### 聯絡效率
- 訊息發送成功率 ≥95%
- 回覆率 ≥30%（業界平均 10-20%）
- 回覆時間 <24 小時

### 轉換效率
- 候選人 → 面試轉換率 ≥20%
- 面試 → 推薦轉換率 ≥50%
- 推薦 → 錄用轉換率 ≥30%

### 人工時間節省
- 搜尋時間：100% → 0%（完全自動化）
- 配對時間：100% → 10%（只需審核）
- 聯絡時間：100% → 20%（只需處理複雜問題）
- 追蹤時間：100% → 0%（完全自動化）
- **總節省**: ~70-80%

---

## 🚨 風險與應對

### 風險 1: LinkedIn 封鎖
**機率**: 中  
**影響**: 高  
**應對**:
- 使用 LinkedIn Recruiter API（合規）
- 控制發送頻率（<30/天）
- 多渠道備份（Email, WhatsApp）

### 風險 2: 訊息被視為垃圾郵件
**機率**: 中  
**影響**: 中  
**應對**:
- AI 生成個人化訊息
- 避免群發相同內容
- 提供取消訂閱選項

### 風險 3: AI 配對不準確
**機率**: 中  
**影響**: 中  
**應對**:
- 人工審核機制（Level 3 定義）
- A/B 測試優化 Prompt
- 持續學習與調整

### 風險 4: 候選人資料品質差
**機率**: 高  
**影響**: 中  
**應對**:
- 多渠道交叉驗證
- AI 資料清理
- 人工抽查

### 風險 5: 系統穩定性問題
**機率**: 低  
**影響**: 高  
**應對**:
- Checkpoint/Resume 機制
- 錯誤自動恢復
- 監控與告警

---

## 🎯 成功標準

### Phase 1-2 (2 週後)
- ✅ 一鍵搜尋可用
- ✅ 每個 JD 可找到 10-20 個候選人
- ✅ AI 配對準確度 ≥70%
- ✅ 候選人資料庫建立

### Phase 3-4 (4 週後)
- ✅ 自動發送訊息可用
- ✅ 自動追蹤回覆可用
- ✅ 回覆率 ≥30%
- ✅ Pipeline 表自動更新

### Phase 5-6 (6 週後)
- ✅ 完整自動化流程運作
- ✅ Cron Jobs 穩定執行
- ✅ 人工時間節省 ≥70%
- ✅ 系統可規模化

### Phase 7-8 (8 週後)
- ✅ AI 持續學習優化
- ✅ 數據驅動決策
- ✅ 可同時處理 10+ JD
- ✅ 候選人池 >500 人

---

## 📅 里程碑時間表

| 週次 | 日期 | 里程碑 | 交付 |
|------|------|--------|------|
| Week 1 | 2/17-2/23 | 多渠道搜尋整合 | `auto-sourcing.sh` |
| Week 2 | 2/24-2/28 | 候選人資料庫 | API Server |
| Week 3 | 3/3-3/9 | AI 訊息生成 | 多渠道發送 |
| Week 4 | 3/10-3/14 | 自動追蹤回覆 | Telegram 通知 |
| Week 5 | 3/17-3/23 | 完整流程整合 | Cron Jobs |
| Week 6 | 3/24-3/28 | 優化與穩定 | 監控儀表板 |
| Week 7 | 3/31-4/6 | AI 學習優化 | 自動化報告 |
| Week 8 | 4/7-4/11 | 規模化測試 | 完整文檔 |

---

## 🔄 下一步行動

### 本週（2/13-2/14）
1. ⏳ 完成獵頭流程上線（Day 3-4）
2. ⏳ Cambodia 候選人回覆追蹤

### 下週（2/17-2/23）
1. 🆕 開始 Phase 1: 多渠道搜尋整合
2. 🆕 建立候選人資料結構
3. 🆕 測試 3 個 JD

### 本月底（2/24-2/28）
1. 🆕 建立候選人資料庫
2. 🆕 API Server 開發
3. 🆕 累積 50-100 個候選人

---

## ❓ 決策點

**問題 1**: 付費升級時機？
- [ ] 立刻訂閱（Phase 1 開始）
- [ ] Phase 3 再訂閱（確認效果後）← 建議
- [ ] Phase 5 再訂閱（規模化時）

**問題 2**: 優先渠道？
- [ ] LinkedIn 優先（海外/高階人才）
- [ ] 104 優先（台灣本地人才）← 建議
- [ ] 兩者並行（成本較高）

**問題 3**: 伺服器部署？
- [ ] 本地運行（Mac mini）← Phase 1-2
- [ ] VPS 部署（DigitalOcean）← Phase 3+ 建議
- [ ] 兩者並行（備援）

---

**制定日期**: 2026-02-12 19:45  
**制定者**: YuQi (YQ1)  
**狀態**: 等待 Jacky 確認開始執行
