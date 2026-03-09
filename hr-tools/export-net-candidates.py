#!/usr/bin/env python3
"""
export-net-candidates.py
重新搜尋 .NET 後端 (Job ID 19) 候選人，
結果存成 CSV + JSON（供 API 上傳用）
"""

import sys
import json
import csv
import os
import datetime

# 把 hr-tools 加進 path 讓 pipeline 可以 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from talent_sourcing_pipeline import TalentSourcingPipeline

OUTPUT_DIR = "/tmp"
TIMESTAMP  = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
CSV_FILE   = f"{OUTPUT_DIR}/dotnet-candidates-{TIMESTAMP}.csv"
JSON_FILE  = f"{OUTPUT_DIR}/dotnet-candidates-{TIMESTAMP}.json"

# ── CSV 欄位 ────────────────────────────────────────────────────
CSV_HEADERS = [
    "name", "email", "github_url", "linkedin_url",
    "skills", "score", "grade",
    "position", "company",
    "matched_skills", "missing_skills",
    "strengths", "conclusion",
    "contact_method", "open_to_work", "has_photo",
    "notes", "status", "recruiter"
]

def run():
    print("🚀 開始重新搜尋 .NET 後端開發工程師（Job ID 19）...")
    print(f"📁 輸出目錄: {OUTPUT_DIR}")
    print()

    # 建立 pipeline 實例（Job ID 19 = .NET 後端）
    pipeline = TalentSourcingPipeline(job_id=19)

    # ── 執行 JD 分析 ──
    print("📋 【第一階段】JD 深度分析...")
    pipeline._stage_jd_analysis()
    job_title   = pipeline.jd_analysis['job_profile']['title']
    company_name = pipeline.jd_analysis['company_profile']['name']
    print(f"   職位：{job_title}  公司：{company_name}")
    print()

    # ── 執行搜尋 ──
    print("🔍 【第二階段】雙管道搜尋（GitHub + LinkedIn）...")
    pipeline._stage_search()
    print(f"   GitHub: {len(pipeline.github_candidates)} 位 / LinkedIn: {len(pipeline.linkedin_candidates)} 位")
    print()

    # ── 去重 ──
    print("🧹 【第二點五階段】智慧去重...")
    pipeline._stage_deduplication()
    print(f"   去重後：{len(pipeline.final_candidates)} 位")
    print()

    if not pipeline.final_candidates:
        print("⚠️ 沒有找到候選人，結束。")
        return

    # ── 執行評分 ──
    print(f"🤖 【第三階段】AI 評分（{len(pipeline.final_candidates)} 位）...")
    from candidate_scorer import CandidateScorer
    scorer = CandidateScorer(pipeline.jd_analysis)
    for idx, candidate in enumerate(pipeline.final_candidates, 1):
        try:
            result = scorer.score(candidate)
            pipeline.scored_candidates.append(result)
            grade = result.get('grade', '?')
            score = result.get('score', 0)
            print(f"   [{idx:02d}] {candidate.get('name','?'):25s} → {score}分 / {grade}級")
        except Exception as e:
            print(f"   [{idx:02d}] {candidate.get('name','?'):25s} → 評分失敗: {e}")

    print(f"\n   ✅ 評分完成：{len(pipeline.scored_candidates)} 位")
    print()

    # ── 輸出 CSV ──
    print(f"📊 【第四階段】輸出 CSV...")
    rows = []
    for sc in pipeline.scored_candidates:
        row = {
            "name":           sc.get("name", ""),
            "email":          sc.get("email", ""),
            "github_url":     sc.get("github_url", ""),
            "linkedin_url":   sc.get("linkedin_url", ""),
            "skills":         ", ".join(sc.get("skills", [])) if isinstance(sc.get("skills"), list) else sc.get("skills", ""),
            "score":          sc.get("score", 0),
            "grade":          sc.get("grade", ""),
            "position":       sc.get("position", job_title),
            "company":        sc.get("company", company_name),
            "matched_skills": ", ".join(sc.get("matched_skills", [])) if isinstance(sc.get("matched_skills"), list) else sc.get("matched_skills", ""),
            "missing_skills": ", ".join(sc.get("missing_skills", [])) if isinstance(sc.get("missing_skills"), list) else sc.get("missing_skills", ""),
            "strengths":      " | ".join(sc.get("strengths", [])) if isinstance(sc.get("strengths"), list) else sc.get("strengths", ""),
            "conclusion":     sc.get("conclusion", ""),
            "contact_method": sc.get("contact_method", ""),
            "open_to_work":   "是" if sc.get("open_to_work") else "否",
            "has_photo":      "是" if sc.get("has_photo") else "否",
            "notes":          f"AI爬蟲 | {job_title} ({company_name}) | {TIMESTAMP}",
            "status":         "AI推薦",
            "recruiter":      "Jacky",
        }
        rows.append(row)

    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"   ✅ CSV 已儲存：{CSV_FILE}")

    # ── 輸出 JSON（供後續直接 API 上傳用）──
    print(f"📦 【第五階段】輸出 API JSON...")
    api_payload = {
        "job_id": 19,
        "job_title": job_title,
        "company": company_name,
        "exported_at": TIMESTAMP,
        "total": len(pipeline.scored_candidates),
        "candidates": []
    }
    for sc in pipeline.scored_candidates:
        api_payload["candidates"].append({
            "name":              sc.get("name", ""),
            "email":             sc.get("email", "unknown@github.com"),
            "github_url":        sc.get("github_url", ""),
            "linkedin_url":      sc.get("linkedin_url", ""),
            "status":            "AI推薦",
            "stability_score":   sc.get("score", 0),
            "talent_level":      sc.get("grade", ""),
            "recruitment_source": "自動爬蟲",
            "notes": (
                f"Bot 自動匯入 | 目標職缺：{sc.get('position', job_title)} ({sc.get('company', company_name)}) | "
                f"負責顧問：Jacky | "
                + ("🟢 Open to Work | " if sc.get("open_to_work") else "")
                + TIMESTAMP
            ),
            "ai_match_result": {
                "score":             sc.get("score", 0),
                "grade":             sc.get("grade", ""),
                "date":              sc.get("date", TIMESTAMP[:10]),
                "position":          sc.get("position", job_title),
                "company":           sc.get("company", company_name),
                "matched_skills":    sc.get("matched_skills", []),
                "missing_skills":    sc.get("missing_skills", []),
                "strengths":         sc.get("strengths", []),
                "probing_questions": sc.get("probing_questions", []),
                "salary_fit":        sc.get("salary_fit", ""),
                "conclusion":        sc.get("conclusion", ""),
                "contact_method":    sc.get("contact_method", ""),
                "open_to_work":      sc.get("open_to_work", False),
                "has_photo":         sc.get("has_photo", False),
                "evaluated_by":      sc.get("evaluated_by", "pipeline-v1"),
                "evaluated_at":      sc.get("evaluated_at", TIMESTAMP),
                "sourced_from":      "talent-sourcing-pipeline",
            }
        })

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)

    print(f"   ✅ JSON 已儲存：{JSON_FILE}")

    # ── 摘要 ──
    grade_count = {}
    for sc in pipeline.scored_candidates:
        g = sc.get("grade", "?")
        grade_count[g] = grade_count.get(g, 0) + 1

    print(f"""
════════════════════════════════════════
✅ 導出完成！

職位：{job_title}（{company_name}）
總計：{len(rows)} 位候選人

等級分布：""")
    for g, c in sorted(grade_count.items()):
        print(f"   {g} 級：{c} 位")

    print(f"""
📁 輸出檔案：
   CSV  → {CSV_FILE}
   JSON → {JSON_FILE}

📌 後續操作（Zeabur 恢復後）：
   curl -X POST https://backendstep1ne.zeabur.app/api/candidates/bulk \\
     -H 'Content-Type: application/json' \\
     -d @{JSON_FILE}
════════════════════════════════════════""")

if __name__ == "__main__":
    run()
