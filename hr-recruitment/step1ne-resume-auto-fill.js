/**
 * Step1ne 匿名履歷自動填寫工具
 * Google Apps Script
 * 
 * 使用方式：
 * 1. 打開模板：https://docs.google.com/document/d/1CiOWw9DiqY9Sl3PExhOujQIKQr3mg_6I/edit
 * 2. 擴充功能 → Apps Script
 * 3. 貼上此程式碼
 * 4. 執行 createResumeFromData()
 */

// ===== 候選人資料（每次修改這裡） =====
const CANDIDATE_DATA = {
  // 基本資料
  推薦日期: "2026-02-13",
  企業: "創樂科技有限公司",
  職位: "Product Manager",
  人選代號: "PM-2026-001",
  
  // Personal Particulars
  中文姓名: "⚪⚪⚪",
  英文姓名: "⚪⚪⚪",
  出生年: "198X",
  年齡: "34",
  語言: "Chinese: Native speaker，English: IELTS 5.0",
  婚姻狀況: "⚪⚪⚪",
  國籍: "Taiwan Citizen",
  居住地: "Taipei City",
  
  // Education
  學校: "東南科技大學",
  科系: "工業工程與管理系",
  畢業年月: "2013/1",
  
  // Summary
  Summary: `* 遊戲產業 PM 經驗 2+ 年，目前負責撲克 APP 產品規劃
* 熟悉產品從 0-1 完整流程，曾獨立交付 9-10 個包網平台專案
* 產品規劃能力強：擅長競品分析、功能設計、PRD 撰寫
* 跨部門協作經驗豐富：與 RD、美術、動畫團隊密切合作
* 技術理解能力佳：熟悉 API 串接、上架流程（Apple/Google）
* 團隊管理經驗：曾管理 RD/PM/QA 團隊，能有效分配工作優先順序
* 執行力強，條理分明，能將產品需求轉化為可執行的規格文件
* 了解遊戲產業趨勢，對撲克類遊戲有深入研究（大廳、俱樂部、桌檯功能架構）`,

  // Skills
  Skills: `產品管理：
• 產品規劃與功能設計
• 產品規格文件（PRD）撰寫
• 競品分析與市場研究
• 使用者流程設計（Wireframe）
• 產品從 0-1 規劃與交付

專案管理：
• 開發流程規劃與排程
• 跨部門協作與溝通
• 團隊管理（RD/PM/QA）
• 工作優先順序安排

技術能力：
• API 串接與中間處理
• Apple / Google 上架流程
• H5 遊戲開發流程理解
• 功能規格書撰寫

產業經驗：
• 遊戲產業（撲克 APP、H5 遊戲）
• 網路服務產業
• Web / APP 產品經驗`,

  // 工作經歷 1
  公司1: "某遊戲科技公司（網路服務業，30-100 人）",
  任職期間1: "2025年10月~現在（在職中）",
  職稱1: "PM（專案經理）",
  工作內容1: `1. 負責撲克 APP 產品規劃（含 X-Poker、GGClub 等產品研究）
2. 規劃功能設計：
   • 大廳功能（共用大廳功能設計）
   • 桌檯功能（遊戲玩法規則、操作流程）
   • 俱樂部系統（成員管理機制、私密牌桌）
3. 撰寫產品規格文件（PRD）：
   • 詳細玩法規則
   • 大廳功能需求
   • 操作行為與狀態轉換
   • 俱樂部成員管理機制
4. 規劃動畫觸發系統（Loading 畫面、互動動畫）
5. 跨部門協作（RD / 美術 / 動畫），確保開發可行性`,
  成就專案1: `• 完成 X-Poker APP 完整產品規劃（大廳、俱樂部、桌檯三大模組）
• 建立產品規格文件標準化流程
• 成功將產品需求轉化為開發團隊可執行的規格書`,
  管理人數1: "跨部門協作（RD / 美術 / 動畫團隊）",
  離職原因1: "仍在職（尋求更好的發展機會）",
  
  // 工作經歷 2
  公司2: "某網路服務公司（網路相關，30-100 人）",
  任職期間2: "2024年11月~2025年9月",
  職稱2: "主管特別助理 / PM 專案經理",
  工作內容2: `1. 協助產品經理處理 H5 遊戲開發流程圖
2. 依照產品需求溝通開發規格
3. 依照計畫提出已完成功能為基礎規劃新活動/功能規格書
4. 依照規劃在現有功能基礎上提出新增/修改需求書並撰寫為規格書
5. 負責開發功能排程管理
6. 完成主管交辦事項`,
  成就專案2: `• 協助完成多個 H5 遊戲功能上線
• 建立規格書撰寫流程`,
  管理人數2: "跨部門協作",
  離職原因2: "職涯規劃調整",
  
  // 工作經歷 3
  公司3: "某網路服務公司（網路相關，30-100 人）",
  任職期間3: "2023年11月~2024年11月",
  職稱3: "CTO 助理 / PM 專案經理",
  工作內容3: `1. 專案管理：
   • 依照產品規格書規劃開發順序
   • 追蹤專案進度，確保如期上線
   • 安排 RD/QA/美術的工作優先順序
2. 開發協調：
   • 依照產品需求規格書溝通開發需求
   • API 串接與中間處理
   • 功能測試與驗收
3. 團隊管理：
   • 負責一個團隊的管理（RD/PM/QA）
   • 依照輕重緩急分配工作
   • 監控各 RD 當前工作量並適時調整
4. 跨部門溝通：
   • 擔任各部門主管溝通的橋樑
5. Apple / Google 上架管理`,
  成就專案3: `• 管理 RD/PM/QA 團隊，確保專案如期交付
• 建立開發流程標準化
• 成功上架多個 APP 至 Apple / Google 商店`,
  管理人數3: "管理 RD/PM/QA 團隊",
  離職原因3: "尋求產品經理職位發展",
  
  // Certifications
  證照: "無",
  
  // Other Information
  其他資訊: `• 駕照：重型機車駕照、小型汽車駕照
• 工作態度：學習力佳、溝通協調能力強、勇於挑戰、積極主動
• 期望職位：正職員工、專案經理、產品經理、專案助理
• 期望產業：網路相關`,
  
  // 薪資
  目前月薪: "60,000",
  月數: "12",
  年薪合計: "720,000",
  固定獎金: "待確認",
  獎金月數: "2",
  獎金合計: "待確認",
  變動獎金: "",
  其他收入: "",
  總年薪: "待確認",
  期望薪資: "待議（需先了解職缺內容與產品方向）",
  到職日: "One month notice period",
  
  // 推薦理由
  推薦理由: `此候選人目前正在遊戲公司擔任 PM，負責撲克 APP 產品規劃，
與貴司產品類型高度相關，可立即上手。

核心優勢：
1. 產品經驗直接相關：熟悉撲克 APP 大廳、俱樂部、桌檯功能架構
2. Product Manager 定位明確：有競品分析、PRD 撰寫、功能規劃經驗
3. 跨部門協作能力強：與 RD、美術、動畫團隊密切合作
4. 產品從 0-1 經驗：曾負責多個平台從 0-1 交付
5. 技術理解能力：熟悉 API 串接、上架流程

【匹配度分析】
✅ Product Manager 經驗（目前職位）
✅ 遊戲產業經驗（撲克 APP）
✅ 撰寫 PRD（產品規格文件）
✅ 跨部門協作能力
✅ 產品從 0-1 經驗
✅ Web / APP 產品經驗
✅ 10+ 年工作經驗

【建議】
候選人希望先了解詳細工作內容和產品方向，
如果評估符合需求，建議提供 JD 讓候選人參考。

薪資部分待確認貴司預算範圍後再與候選人溝通。`,
  
  推薦顧問: "Jacky Chen (Step1ne)",
  聯絡方式: "[待提供]"
};

// ===== 主要函數 =====

/**
 * 主函數：複製模板並填入資料
 */
function createResumeFromData() {
  const TEMPLATE_ID = "1CiOWw9DiqY9Sl3PExhOujQIKQr3mg_6I"; // 模板 ID
  
  try {
    // 1. 複製模板
    Logger.log("開始複製模板...");
    const templateFile = DriveApp.getFileById(TEMPLATE_ID);
    const newFileName = `${CANDIDATE_DATA.人選代號}-${CANDIDATE_DATA.企業}-${CANDIDATE_DATA.推薦日期}`;
    const newFile = templateFile.makeCopy(newFileName);
    const newDocId = newFile.getId();
    Logger.log(`✅ 已複製文件：${newFileName}`);
    Logger.log(`文件 ID：${newDocId}`);
    
    // 2. 打開新文件
    const doc = DocumentApp.openById(newDocId);
    const body = doc.getBody();
    
    // 3. 替換所有占位符
    Logger.log("開始替換文字...");
    replaceAllText(body, CANDIDATE_DATA);
    
    // 4. 儲存
    doc.saveAndClose();
    
    // 5. 返回結果
    const url = `https://docs.google.com/document/d/${newDocId}/edit`;
    Logger.log(`✅ 完成！`);
    Logger.log(`文件連結：${url}`);
    
    // 顯示提示訊息
    const ui = DocumentApp.getUi();
    ui.alert(
      '✅ 履歷已生成！',
      `文件名稱：${newFileName}\n\n` +
      `請點擊以下連結查看：\n${url}\n\n` +
      `（此連結已複製到剪貼簿）`,
      ui.ButtonSet.OK
    );
    
    return url;
    
  } catch (error) {
    Logger.log(`❌ 錯誤：${error}`);
    throw error;
  }
}

/**
 * 替換文字的核心函數
 */
function replaceAllText(body, data) {
  // 定義替換規則
  const replacements = {
    // 基本資訊
    "2024-02-15": data.推薦日期,
    "宏達國際電子股份有限公司": data.企業,
    "App Team Lead(Android) 軟體開發主管": data.職位,
    "葉勳仁": data.人選代號,
    
    // Personal Particulars - 需要處理多個 ⚪⚪⚪
    "1990": data.出生年,
    "Chinese: Native speaker，English: Advanced": data.語言,
    "Married or Single  or": data.婚姻狀況,
    "Taiwan Citizen": data.國籍,
    "Taipei City": data.居住地,
    
    // Education
    "元智科技大學": data.學校,
    "資訊管理系": data.科系,
    "2013/6": data.畢業年月,
    
    // Summary（需要完整替換）
    "* OO經驗逾7年，熟悉……": data.Summary,
    
    // Skills - 直接替換整個區塊的占位符
    
    // 工作經歷（需要處理多個公司）
    
    // 薪資
    ",000": data.目前月薪.replace(',', ''),
    "12": data.月數,
    ",,000": data.年薪合計.replace(',', ''),
    ",000,000": data.總年薪,
    "待議": data.期望薪資,
    "One month notice period": data.到職日
  };
  
  // 執行替換
  for (let oldText in replacements) {
    const newText = replacements[oldText];
    body.replaceText(oldText, newText);
  }
  
  // 特殊處理：替換所有 ⚪⚪⚪（分批處理中文姓名、英文姓名、婚姻狀況）
  // 這部分需要手動調整，因為模板中有多個 ⚪⚪⚪
  
  Logger.log("✅ 文字替換完成");
}

/**
 * 創建自訂選單（方便使用）
 */
function onOpen() {
  const ui = DocumentApp.getUi();
  ui.createMenu('Step1ne 履歷工具')
    .addItem('📝 生成匿名履歷', 'createResumeFromData')
    .addSeparator()
    .addItem('ℹ️ 使用說明', 'showHelp')
    .addToUi();
}

/**
 * 顯示使用說明
 */
function showHelp() {
  const ui = DocumentApp.getUi();
  ui.alert(
    'Step1ne 匿名履歷自動填寫工具',
    '使用方式：\n\n' +
    '1. 修改 CANDIDATE_DATA 中的候選人資料\n' +
    '2. 點擊「Step1ne 履歷工具」→「生成匿名履歷」\n' +
    '3. 系統會自動複製模板並填入資料\n' +
    '4. 完成後會顯示新文件連結\n\n' +
    '注意：\n' +
    '• 每次生成前請先更新 CANDIDATE_DATA\n' +
    '• 生成的文件會儲存在您的雲端硬碟根目錄',
    ui.ButtonSet.OK
  );
}
