# 獵頭顧問 Prompt 模板庫

## 1. 人才畫像 (Persona Generator)

```
作為世界級招募行銷專家，分析以下職缺 JD，建立「人才畫像」(Candidate Persona)。

[JD 內容]:
"{jd}"

---

輸出 JSON 格式，包含 7 個維度：

{
  "archetype": "人才類型名稱（如：技術魔法師）",
  "quote": "代表這類人才心態的一句話",
  "bio": "2-3句人物描述",
  
  "workType": ["工作類型1", "工作類型2"],
  "traits": ["人才特質1", "人才特質2"],
  "skills": ["專業技能1", "專業技能2"],
  "values": ["價值觀1", "價值觀2"],
  "background": {
    "education": "學歷要求",
    "experience": "經驗要求",
    "industries": ["目標產業1", "目標產業2"]
  },
  "channels": ["招募管道1", "招募管道2"],
  "keywords": ["搜尋關鍵字1", "搜尋關鍵字2"]
}

使用繁體中文輸出。
```

---

## 2. 人才搜尋策略 (Talent Search)

```
作為資深獵頭顧問和招募策略師，為以下職缺制定搜尋策略：

職稱：{title}
技能需求：{skills}
地點：{location}

請提供：

1. **招募管道策略**：最適合找這類人才的 3-5 個平台/社群
2. **目標公司名單**：在 {location} 有這類人才的 8-10 間公司，說明為何適合
3. **Boolean Search Strings**：提供 3 種 LinkedIn 搜尋字串
   - 廣泛搜尋
   - 精準搜尋
   - 利基搜尋

輸出 JSON 格式：
{
  "channelStrategy": ["管道1", "管道2"],
  "companyHuntingList": [
    { "name": "公司名稱", "reason": "適合原因" }
  ],
  "booleanStrings": [
    { "label": "廣泛搜尋", "query": "boolean string" },
    { "label": "精準搜尋", "query": "boolean string" },
    { "label": "利基搜尋", "query": "boolean string" }
  ]
}

使用繁體中文輸出。
```

---

## 3. 履歷-JD 匹配分析 (Match Analysis)

```
作為嚴格的招募經理，比較以下 [JD] 與 [履歷] 的匹配程度：

[JD]:
"{jd}"

[履歷]:
"{resume}"

---

輸出 JSON 格式：
{
  "score": 85,
  "summary": "整體評估摘要（2-3句）",
  "recommendation": "Strong Hire / Hire / Hold / No Hire",
  "reasoning": "推薦/不推薦的核心理由",
  "strengths": ["優點1", "優點2", "優點3"],
  "weaknesses": ["缺點/缺口1", "缺點/缺口2"],
  "interviewQuestions": ["建議面試問題1", "建議面試問題2", "建議面試問題3"]
}

使用繁體中文輸出。
```

---

## 4. 開發信撰寫 (Outreach Writer)

```
作為資深獵頭，撰寫 3 種風格的開發信（LinkedIn InMail 或 Email）：

[基本資訊]
候選人姓名：{candidateName}
目標職位：{position}
客戶公司：{company}
語氣：{tone}

[參考文件]
候選人履歷：
"{resume}"

職缺 JD：
"{jd}"

---

撰寫要求：
1. 分析履歷與 JD 的關聯
2. 在信中具體提到候選人的經驗如何符合職缺
3. 提供 3 種版本

輸出 JSON 陣列：
[
  {
    "type": "簡短直接",
    "subject": "Email 主旨",
    "content": "Email 內容"
  },
  {
    "type": "詳細價值導向",
    "subject": "Email 主旨",
    "content": "Email 內容（強調職涯發展、技能匹配）"
  },
  {
    "type": "提問式開場",
    "subject": "Email 主旨",
    "content": "Email 內容（以問題開場，引起興趣）"
  }
]

使用繁體中文輸出。
```

---

## 5. 面試問題生成 (Interview Questions)

```
作為面試官，根據以下資料生成結構化面試問題：

[JD]:
"{jd}"

[候選人履歷]（如有）:
"{resume}"

---

輸出 JSON 格式：
{
  "resumeDeepDive": [
    "履歷深挖問題1（針對特定經歷詢問）",
    "履歷深挖問題2",
    "履歷深挖問題3"
  ],
  "technicalQuestions": [
    "技術問題1",
    "技術問題2",
    "技術問題3"
  ],
  "behavioralQuestions": [
    "行為問題1（STAR 格式）",
    "行為問題2",
    "行為問題3"
  ],
  "redFlags": [
    "需特別注意/追問的點1",
    "需特別注意/追問的點2"
  ]
}

使用繁體中文輸出。
```

---

## 6. JD 生成 (Job Description Generator)

```
作為專業 HR 顧問和招募行銷專家，根據以下資訊生成 JD：

[輸入資訊]
職稱：{title}
資歷：{seniority}
技能需求：{skills}
公司文化：{culture}
主管筆記（如有）：{notes}

---

生成兩個版本：

版本 1：正式招募平台版（104、LinkedIn、CakeResume）
- 結構：職務摘要、主要職責、必備條件、加分條件、福利
- 語氣：專業、結構化、清楚

版本 2：社群媒體版（FB、IG、LinkedIn Post）
- 結構：吸睛標題、Emoji、亮點、CTA
- 語氣：活潑、吸引人、易分享

輸出 JSON 格式：
{
  "platform": "正式版 JD 內容（Markdown）",
  "social": "社群版內容（帶 emoji）"
}

使用繁體中文輸出。
```

---

## 7. 候選人摘要 (Candidate Summary)

```
作為獵頭顧問，根據履歷撰寫候選人推薦摘要：

[履歷]:
"{resume}"

[職缺 JD]（如有）:
"{jd}"

[顧問備註]（如有）:
"{notes}"

---

輸出 JSON 格式：
{
  "name": "候選人姓名",
  "currentRole": "現職公司 / 職稱",
  "experience": "N 年相關經驗",
  "education": "最高學歷",
  "highlights": [
    "核心優勢1",
    "核心優勢2",
    "核心優勢3"
  ],
  "motivation": "轉職動機（如履歷/備註中有提到）",
  "expectedSalary": "期望薪資（如有）",
  "availability": "可到職日（如有）",
  "summary": "一段 3-5 句的推薦摘要，可直接用於 Email"
}

使用繁體中文輸出。
```

---

## 8. 推薦信生成 (Recommendation Email)

```
作為獵頭顧問，撰寫一封給客戶的候選人推薦 Email：

[候選人資訊]:
{candidateSummary}

[職缺 JD]（如有）:
"{jd}"

[客戶資訊]:
客戶名稱/稱呼：{clientName}

---

輸出 JSON 格式：
{
  "subject": "Email 主旨（格式：【Step1ne】推薦 {職位} 人選 - {姓名}）",
  "greeting": "開頭問候",
  "body": "正文內容（包含候選人摘要、推薦理由、亮點）",
  "closing": "結尾（詢問是否安排面試、聯絡方式）",
  "fullEmail": "完整 Email 內容（可直接複製使用）"
}

使用繁體中文，語氣專業但親切。
```

---

## 使用方式

當用戶提供 JD/履歷等資料時：
1. 判斷要使用哪個模板
2. 將用戶資料填入 `{變數}` 位置
3. 執行 prompt
4. 解析 JSON 輸出並回覆用戶
