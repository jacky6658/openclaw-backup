#!/usr/bin/env python3
"""
Industry Analytics Dashboard - 產業分析儀表板 (Fixed)

可視化：
1. 候選人產業分布（餅圖）
2. 職缺 vs 候選人產業匹配熱力圖
3. 遷移能力分布（直方圖）
4. 評分分布（漏斗圖）
5. 數據表格摘要
"""

import json
from typing import Dict, List, Optional
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

# ==================== 數據類 ====================

@dataclass
class DashboardMetrics:
    """儀表板指標"""
    total_candidates: int
    total_jobs: int
    industry_distribution: Dict[str, int]
    skill_distribution: Dict[str, int]
    talent_level_distribution: Dict[str, int]
    migration_potential_avg: float
    top_industries: List[str]
    top_skills: List[str]

# ==================== 儀表板生成器 ====================

class AnalyticsDashboard:
    """產業分析儀表板生成器"""
    
    def __init__(self):
        pass
    
    def generate_dashboard(self, candidates_data: Dict, jobs_data: Dict, output_dir: str = '/tmp'):
        """生成完整儀表板"""
        
        # 收集指標
        metrics = self._collect_metrics(candidates_data, jobs_data)
        
        # 生成 JSON 報告
        json_report = self._generate_json_report(metrics, candidates_data)
        
        # 生成 HTML 儀表板
        html_dashboard = self._generate_html_dashboard(metrics, candidates_data, jobs_data)
        
        # 保存檔案
        self._save_reports(json_report, html_dashboard, output_dir)
        
        return metrics
    
    def _collect_metrics(self, candidates_data: Dict, jobs_data: Dict) -> DashboardMetrics:
        """收集儀表板指標"""
        
        # 產業分布
        industries = [c.get('source_industry') for c in candidates_data.get('candidates', []) if c.get('source_industry')]
        industry_dist = dict(Counter(industries))
        
        # 技能分布
        all_skills = []
        for c in candidates_data.get('candidates', []):
            all_skills.extend(c.get('skills', []))
        skill_dist = dict(Counter(all_skills))
        
        # 評級分布
        levels = [c.get('talent_level') for c in candidates_data.get('candidates', []) if c.get('talent_level')]
        level_dist = dict(Counter(levels))
        
        # 遷移潛力平均分
        migration_scores = [c.get('migration_potential', 50) for c in candidates_data.get('candidates', [])]
        avg_migration = sum(migration_scores) / len(migration_scores) if migration_scores else 0
        
        return DashboardMetrics(
            total_candidates=len(candidates_data.get('candidates', [])),
            total_jobs=len(jobs_data.get('jobs', [])),
            industry_distribution=industry_dist,
            skill_distribution=skill_dist,
            talent_level_distribution=level_dist,
            migration_potential_avg=avg_migration,
            top_industries=sorted(industry_dist.items(), key=lambda x: x[1], reverse=True)[:3],
            top_skills=sorted(skill_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        )
    
    def _generate_json_report(self, metrics: DashboardMetrics, candidates_data: Dict) -> Dict:
        """生成 JSON 報告"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_candidates': metrics.total_candidates,
                'total_jobs': metrics.total_jobs,
                'avg_migration_potential': round(metrics.migration_potential_avg, 2),
            },
            'distribution': {
                'industries': metrics.industry_distribution,
                'top_industries': [{'name': ind, 'count': count} 
                                 for ind, count in metrics.top_industries],
                'talent_levels': metrics.talent_level_distribution,
                'top_skills': [{'skill': skill, 'count': count} 
                             for skill, count in metrics.top_skills],
            },
            'candidates_sample': candidates_data.get('candidates', [])[:10],
        }
    
    def _generate_html_dashboard(self, metrics: DashboardMetrics, 
                                candidates_data: Dict, jobs_data: Dict) -> str:
        """生成 HTML 儀表板"""
        
        # 產業分布圖數據
        industry_labels = [ind[0] for ind in metrics.top_industries]
        industry_values = [ind[1] for ind in metrics.top_industries]
        industry_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'][:len(industry_labels)]
        
        # 評級分布
        level_labels = list(metrics.talent_level_distribution.keys())
        level_values = list(metrics.talent_level_distribution.values())
        
        # 時間戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 構建 HTML 片段 (分開以避免 f-string 問題)
        html_parts = []
        
        # DOCTYPE + Head
        html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>產業分析儀表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            color: #7f8c8d;
            font-size: 14px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }
        .metric-card.alt1 { border-left-color: #e74c3c; }
        .metric-card.alt2 { border-left-color: #2ecc71; }
        .metric-card.alt3 { border-left-color: #f39c12; }
        .metric-label {
            color: #95a5a6;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #2c3e50;
            font-size: 28px;
            font-weight: bold;
        }
        .metric-unit {
            color: #95a5a6;
            font-size: 12px;
            margin-left: 5px;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-container h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 16px;
        }
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        .table-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow-x: auto;
        }
        .table-container h3 {
            margin-bottom: 15px;
            color: #2c3e50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #ecf0f1;
            padding: 12px;
            text-align: left;
            color: #2c3e50;
            font-weight: 600;
            border-bottom: 2px solid #bdc3c7;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge.s { background: #f39c12; color: white; }
        .badge.a-plus { background: #3498db; color: white; }
        .badge.a { background: #2ecc71; color: white; }
        .badge.b { background: #e74c3c; color: white; }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">""")
        
        # Header
        html_parts.append(f"""        <div class="header">
            <h1>🎯 產業分析儀表板</h1>
            <p>生成時間：{timestamp}</p>
        </div>""")
        
        # Metrics
        top_industry = metrics.top_industries[0][0] if metrics.top_industries else 'N/A'
        html_parts.append(f"""        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">總候選人</div>
                <div class="metric-value">{metrics.total_candidates}</div>
            </div>
            <div class="metric-card alt1">
                <div class="metric-label">招募職缺</div>
                <div class="metric-value">{metrics.total_jobs}</div>
            </div>
            <div class="metric-card alt2">
                <div class="metric-label">遷移潛力</div>
                <div class="metric-value">{metrics.migration_potential_avg:.0f}<span class="metric-unit">/100</span></div>
            </div>
            <div class="metric-card alt3">
                <div class="metric-label">主要產業</div>
                <div class="metric-value">{top_industry}</div>
            </div>
        </div>""")
        
        # Charts
        html_parts.append("""        <div class="charts-grid">
            <div class="chart-container">
                <h3>📊 候選人產業分布</h3>
                <div class="chart-wrapper">
                    <canvas id="industryChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>⭐ 人才評級分布</h3>
                <div class="chart-wrapper">
                    <canvas id="levelChart"></canvas>
                </div>
            </div>
        </div>""")
        
        # Top Skills Table
        html_parts.append("""        <div class="table-container">
            <h3>🛠️ 最受歡迎的技能</h3>
            <table>
                <thead>
                    <tr>
                        <th>技能</th>
                        <th>候選人數</th>
                        <th>占比</th>
                    </tr>
                </thead>
                <tbody>""")
        
        for skill, count in metrics.top_skills:
            percentage = (count / metrics.total_candidates * 100) if metrics.total_candidates > 0 else 0
            html_parts.append(f"""                    <tr>
                        <td>{skill}</td>
                        <td><strong>{count}</strong></td>
                        <td>{percentage:.1f}%</td>
                    </tr>""")
        
        html_parts.append("""                </tbody>
            </table>
        </div>""")
        
        # Candidate Sample Table
        html_parts.append("""        <div class="table-container">
            <h3>👥 候選人樣本（前 10 位）</h3>
            <table>
                <thead>
                    <tr>
                        <th>姓名</th>
                        <th>產業</th>
                        <th>評級</th>
                        <th>遷移潛力</th>
                        <th>核心技能</th>
                    </tr>
                </thead>
                <tbody>""")
        
        for candidate in candidates_data.get('candidates', [])[:10]:
            level = candidate.get('talent_level', 'N/A').lower()
            migration = candidate.get('migration_potential', 0)
            skills = ', '.join(candidate.get('skills', [])[:2])
            name = candidate.get('name', 'N/A')
            industry = candidate.get('source_industry', 'N/A').upper()
            
            html_parts.append(f"""                    <tr>
                        <td>{name}</td>
                        <td>{industry}</td>
                        <td><span class="badge {level}">{level.upper()}</span></td>
                        <td>{migration:.0f}%</td>
                        <td>{skills}</td>
                    </tr>""")
        
        html_parts.append("""                </tbody>
            </table>
        </div>""")
        
        # Footer
        html_parts.append("""        <div class="footer">
            <p>Step1ne 獵頭系統 - 產業智能招聘平台</p>
        </div>
    </div>""")
        
        # JavaScript - Industry Chart
        industry_labels_str = json.dumps(industry_labels)
        industry_values_str = json.dumps(industry_values)
        industry_colors_str = json.dumps(industry_colors)
        
        # JavaScript - Level Chart
        level_labels_str = json.dumps(level_labels)
        level_values_str = json.dumps(level_values)
        
        chart_script = f"""    <script>
        // 產業分布圖
        const industryCtx = document.getElementById('industryChart').getContext('2d');
        new Chart(industryCtx, {{
            type: 'doughnut',
            data: {{
                labels: {industry_labels_str},
                datasets: [{{
                    data: {industry_values_str},
                    backgroundColor: {industry_colors_str},
                    borderColor: '#fff',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 評級分布圖
        const levelCtx = document.getElementById('levelChart').getContext('2d');
        new Chart(levelCtx, {{
            type: 'bar',
            data: {{
                labels: {level_labels_str},
                datasets: [{{
                    label: '人數',
                    data: {level_values_str},
                    backgroundColor: ['#f39c12', '#3498db', '#2ecc71', '#e74c3c'],
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>"""
        
        html_parts.append(chart_script)
        html_parts.append("""</body>
</html>""")
        
        return '\n'.join(html_parts)
    
    def _save_reports(self, json_report: Dict, html_dashboard: str, output_dir: str):
        """保存報告檔案"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON
        json_path = os.path.join(output_dir, 'analytics-report.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 報告：{json_path}")
        
        # HTML
        html_path = os.path.join(output_dir, 'analytics-dashboard.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_dashboard)
        print(f"✅ HTML 儀表板：{html_path}")

# ==================== 主程序 ====================

def main():
    """示例：生成儀表板"""
    
    # 示例數據
    candidates_data = {
        'candidates': [
            {
                'name': '陳宥樺',
                'source_industry': 'internet',
                'talent_level': 'A+',
                'migration_potential': 85,
                'skills': ['Python', 'Go', 'Kubernetes']
            },
            {
                'name': '李明哲',
                'source_industry': 'gaming',
                'talent_level': 'A',
                'migration_potential': 72,
                'skills': ['C#', 'Unity', 'Networking']
            },
        ] * 5  # 重複以有更多數據
    }
    
    jobs_data = {
        'jobs': [
            {'job_title': '資安工程師', 'industry': 'gaming'},
            {'job_title': 'AI工程師', 'industry': 'internet'},
        ] * 3
    }
    
    dashboard = AnalyticsDashboard()
    metrics = dashboard.generate_dashboard(candidates_data, jobs_data, '/tmp/recruiting-pipeline/reports')
    
    print("\n" + "="*80)
    print("📊 儀表板生成完成")
    print("="*80)

if __name__ == '__main__':
    main()
