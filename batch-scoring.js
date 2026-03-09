#!/usr/bin/env node
// Step1ne 批量評分腳本 - Jacky-aibot
// 處理 recruiter == "Crawler-WebUI" AND status == "未開始" 的候選人

const BASE_URL = 'https://backendstep1ne.zeabur.app';
const ACTOR = 'Jacky-aibot';

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${url}`);
  return res.json();
}

async function patchCandidate(id, data) {
  const res = await fetch(`${BASE_URL}/api/candidates/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`PATCH ${id} failed: ${res.status} ${txt}`);
  }
  return res.json();
}

function calcStabilityScore(years, jobChanges) {
  const raw = 40 + (years * 2) - (jobChanges * 3);
  return Math.min(100, Math.max(20, raw));
}

function scoreToGrade(score) {
  if (score >= 85) return { talent_level: 'S', status: 'AI推薦', recommendation: '強力推薦' };
  if (score >= 70) return { talent_level: 'A', status: 'AI推薦', recommendation: '推薦' };
  if (score >= 55) return { talent_level: 'B', status: '備選人才', recommendation: '觀望' };
  return { talent_level: 'C', status: '備選人才', recommendation: '不推薦' };
}

function aiScore(candidate, job) {
  // 評分維度：技能匹配40%、年資25%、產業職能20%、學歷10%、資料完整度5%
  const years = parseFloat(candidate.years) || 0;
  const jobChanges = parseInt(candidate.jobChanges) || 0;
  const stability = calcStabilityScore(years, jobChanges);

  // 技能匹配 (40%)
  const candidateSkills = (candidate.skills || '').toLowerCase();
  const jobReq = job ? (job.requirements || job.skills || job.description || '').toLowerCase() : '';
  const jobTitle = job ? (job.title || job.position || '').toLowerCase() : '';
  
  let skillScore = 40; // base
  if (jobReq && candidateSkills) {
    const reqWords = jobReq.split(/[,\s、，]+/).filter(w => w.length > 1);
    const matched = reqWords.filter(w => candidateSkills.includes(w));
    skillScore = reqWords.length > 0 ? Math.round((matched.length / reqWords.length) * 40) : 20;
  }

  // 年資 (25%)
  const yearScore = Math.min(25, years * 2.5);

  // 產業職能 (20%) - 職位匹配
  const positionMatch = jobTitle && candidate.position 
    ? (candidate.position.toLowerCase().includes(jobTitle.split(' ')[0]) ? 15 : 8)
    : 10;

  // 學歷 (10%)
  const edu = (candidate.education || '').toLowerCase();
  let eduScore = 5;
  if (edu.includes('博士') || edu.includes('phd')) eduScore = 10;
  else if (edu.includes('碩士') || edu.includes('master')) eduScore = 8;
  else if (edu.includes('學士') || edu.includes('大學') || edu.includes('university') || edu.includes('bachelor')) eduScore = 7;
  else if (edu.includes('高中') || edu.includes('high school')) eduScore = 4;

  // 資料完整度 (5%)
  const fields = [candidate.name, candidate.position, candidate.skills, candidate.education, candidate.years];
  const completeness = fields.filter(f => f && String(f).trim()).length;
  const completenessScore = Math.round((completeness / fields.length) * 5);

  const totalScore = skillScore + yearScore + positionMatch + eduScore + completenessScore;
  const finalScore = Math.min(100, Math.max(20, Math.round(totalScore)));

  return { score: finalScore, stability };
}

async function main() {
  console.log('=== Step1ne 批量評分開始 ===');
  console.log(`時間: ${new Date().toLocaleString('zh-TW')}`);
  
  // Step 1: 取得所有候選人
  console.log('\n[Step 1] 取得候選人清單...');
  let allCandidates = [];
  
  try {
    const data = await fetchJSON(`${BASE_URL}/api/candidates?limit=1000`);
    allCandidates = data.data || data || [];
    console.log(`總候選人數: ${allCandidates.length}`);
  } catch (e) {
    console.error('取得候選人失敗:', e.message);
    process.exit(1);
  }

  // 過濾: recruiter == "Crawler-WebUI" AND status == "未開始"
  const targets = allCandidates.filter(c => 
    c.recruiter === 'Crawler-WebUI' && c.status === '未開始'
  );
  
  console.log(`符合條件 (Crawler-WebUI + 未開始): ${targets.length} 位`);
  
  if (targets.length === 0) {
    console.log('沒有符合條件的候選人，任務結束');
    console.log(JSON.stringify({ total: 0, ai_recommended: 0, backup: 0, skipped: 0 }));
    return;
  }

  // 分類: 有/無 target_job_id
  const withJob = targets.filter(c => c.targetJobId);
  const withoutJob = targets.filter(c => !c.targetJobId);
  
  console.log(`有指定職缺: ${withJob.length} 位`);
  console.log(`無指定職缺: ${withoutJob.length} 位`);

  let completed = 0;
  let aiRecommended = 0;
  let backupCount = 0;
  let skipped = 0;

  // 快取 job 資訊
  const jobCache = {};

  // Step 2+3: 有 target_job_id 的候選人
  console.log('\n[Step 2+3] 開始處理有職缺的候選人...');
  
  for (const candidate of withJob) {
    try {
      // Step 2: 職缺排名重算
      try {
        await fetchJSON(`${BASE_URL}/api/candidates/${candidate.id}/job-rankings?force=1`);
      } catch (e) {
        // 忽略排名錯誤，繼續
      }

      // 取得 job 詳情 (快取)
      let job = null;
      if (candidate.targetJobId) {
        if (!jobCache[candidate.targetJobId]) {
          try {
            const jobData = await fetchJSON(`${BASE_URL}/api/jobs/${candidate.targetJobId}`);
            jobCache[candidate.targetJobId] = jobData.data || jobData;
          } catch (e) {
            // job 取得失敗，用 null
          }
        }
        job = jobCache[candidate.targetJobId];
      }

      // AI 評分
      const { score, stability } = aiScore(candidate, job);
      const grade = scoreToGrade(score);
      const jobTitle = job ? (job.title || job.position || candidate.targetJobLabel || '') : candidate.targetJobLabel || '';

      const matchedSkills = [];
      const missingSkills = [];
      if (job) {
        const req = (job.requirements || job.skills || '').toLowerCase();
        const candidateSkills = (candidate.skills || '').toLowerCase();
        const reqWords = req.split(/[,\s、，]+/).filter(w => w.length > 1);
        reqWords.forEach(w => {
          if (candidateSkills.includes(w)) matchedSkills.push(w);
          else missingSkills.push(w);
        });
      }

      const aiMatchResult = {
        score,
        grade: grade.talent_level,
        recommendation: grade.recommendation,
        job_title: jobTitle,
        company: job ? (job.company || '') : '',
        matched_skills: matchedSkills.slice(0, 8),
        missing_skills: missingSkills.slice(0, 8),
        strengths: [`年資 ${candidate.years || 0} 年`, `職位: ${candidate.position || '未知'}`],
        probing_questions: [
          `請描述您在 ${candidate.position || '此領域'} 的具體專案經驗？`,
          `您的期望薪資與可到職時間？`
        ],
        salary_fit: score >= 70 ? '符合預算' : '待確認',
        conclusion: `${candidate.name} 評分 ${score} 分，${grade.recommendation}。穩定性分數: ${stability}。`,
        evaluated_by: ACTOR,
        evaluated_at: new Date().toISOString()
      };

      // 寫回系統
      await patchCandidate(candidate.id, {
        stability_score: stability,
        stabilityScore: stability,
        talent_level: grade.talent_level,
        status: grade.status,
        actor: ACTOR,
        ai_match_result: aiMatchResult,
        aiMatchResult
      });

      if (grade.status === 'AI推薦') aiRecommended++;
      else backupCount++;
      completed++;

      if (completed % 10 === 0) {
        console.log(`[進度] 已完成 ${completed}/${withJob.length + withoutJob.length} 位 | AI推薦: ${aiRecommended} | 備選: ${backupCount}`);
      }
    } catch (e) {
      console.error(`候選人 ${candidate.id} (${candidate.name}) 處理失敗: ${e.message}`);
      skipped++;
    }
  }

  // Step 4: 無 target_job_id 的候選人
  console.log(`\n[Step 4] 處理無職缺候選人 (${withoutJob.length} 位)...`);
  
  for (const candidate of withoutJob) {
    try {
      // Step 2: 職缺排名重算 (force)
      try {
        await fetchJSON(`${BASE_URL}/api/candidates/${candidate.id}/job-rankings?force=1`);
      } catch (e) {
        // 忽略
      }

      // 基礎評分（無職缺對標）
      const years = parseFloat(candidate.years) || 0;
      const jobChanges = parseInt(candidate.jobChanges) || 0;
      const stability = calcStabilityScore(years, jobChanges);
      const score = stability; // 無職缺時直接用穩定性分數
      const grade = scoreToGrade(score);

      const aiMatchResult = {
        score,
        grade: grade.talent_level,
        recommendation: grade.recommendation,
        job_title: '待指派',
        company: '',
        matched_skills: (candidate.skills || '').split(/[,，、]+/).filter(s => s.trim()).slice(0, 5),
        missing_skills: [],
        strengths: [`年資 ${years} 年`, `專長: ${candidate.position || '未知'}`],
        probing_questions: ['請描述您目前的求職方向？', '期望薪資與可到職時間？'],
        salary_fit: '待確認',
        conclusion: `${candidate.name} 穩定性評分 ${stability} 分，${grade.recommendation}。尚未指派職缺。`,
        evaluated_by: ACTOR,
        evaluated_at: new Date().toISOString()
      };

      await patchCandidate(candidate.id, {
        stability_score: stability,
        stabilityScore: stability,
        talent_level: grade.talent_level,
        status: grade.status,
        actor: ACTOR,
        ai_match_result: aiMatchResult,
        aiMatchResult
      });

      if (grade.status === 'AI推薦') aiRecommended++;
      else backupCount++;
      completed++;

      if (completed % 10 === 0) {
        console.log(`[進度] 已完成 ${completed}/${withJob.length + withoutJob.length} 位 | AI推薦: ${aiRecommended} | 備選: ${backupCount}`);
      }
    } catch (e) {
      console.error(`候選人 ${candidate.id} (${candidate.name}) 處理失敗: ${e.message}`);
      skipped++;
    }
  }

  console.log('\n=== 批量評分完成 ===');
  console.log(`總共處理: ${completed} 位`);
  console.log(`AI推薦: ${aiRecommended} 位`);
  console.log(`備選人才: ${backupCount} 位`);
  console.log(`跳過/失敗: ${skipped} 位`);

  // 輸出 JSON 結果給主流程使用
  const result = { total: completed, ai_recommended: aiRecommended, backup: backupCount, skipped };
  console.log('RESULT_JSON:' + JSON.stringify(result));
}

main().catch(e => {
  console.error('Fatal:', e);
  process.exit(1);
});
