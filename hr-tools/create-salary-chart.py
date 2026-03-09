#!/usr/bin/env python3
"""
生成薪資比較圖（用於 LinkedIn 貼文）
需要安裝：pip install matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 設定中文字體（macOS）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang TC', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

def create_salary_comparison():
    """
    生成 .NET 工程師薪資比較圖
    """
    
    # 數據
    positions = ['.NET\nJunior\n(0-2年)', '.NET\nMid-level\n(3-5年)', '.NET\nSenior\n(5-8年)', '.NET\nLead\n(8年+)']
    
    # 薪資範圍（月薪，千元為單位）
    salary_min = [45, 70, 100, 140]
    salary_max = [65, 100, 140, 200]
    salary_avg = [55, 85, 120, 170]
    
    # 建立圖表
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(positions))
    width = 0.6
    
    # 繪製薪資範圍（漸層色）
    colors = ['#4A90E2', '#5BA3F5', '#6CB6FF', '#7DC9FF']
    
    for i in range(len(positions)):
        # 薪資範圍區間
        ax.bar(i, salary_max[i] - salary_min[i], width, 
               bottom=salary_min[i], 
               color=colors[i], 
               alpha=0.3,
               edgecolor=colors[i],
               linewidth=2)
        
        # 平均薪資點
        ax.scatter(i, salary_avg[i], s=200, color=colors[i], 
                  zorder=5, edgecolor='white', linewidth=2)
        
        # 標註平均薪資
        ax.text(i, salary_avg[i] + 8, f'{salary_avg[i]}k', 
               ha='center', fontsize=14, fontweight='bold', color=colors[i])
        
        # 標註薪資範圍
        ax.text(i, salary_min[i] - 8, f'{salary_min[i]}-{salary_max[i]}k', 
               ha='center', fontsize=10, color='gray')
    
    # 設定座標軸
    ax.set_ylabel('月薪（千元 TWD）', fontsize=14, fontweight='bold')
    ax.set_xlabel('資歷等級', fontsize=14, fontweight='bold')
    ax.set_title('.NET 工程師薪資行情（2025 台北）', 
                fontsize=18, fontweight='bold', pad=20)
    
    ax.set_xticks(x)
    ax.set_xticklabels(positions, fontsize=12)
    ax.set_ylim(0, 220)
    
    # 網格線
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # 圖例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4A90E2', alpha=0.3, edgecolor='#4A90E2', label='薪資範圍'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4A90E2', 
                  markersize=10, label='市場平均')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    # 加入資料來源
    fig.text(0.99, 0.01, 'Data Source: Step1ne 獵頭市場調查 | 2025.02', 
            ha='right', fontsize=9, color='gray')
    
    # 加入 Branding
    fig.text(0.01, 0.01, '🦞 Step1ne Headhunting', 
            ha='left', fontsize=10, color='#4A90E2', fontweight='bold')
    
    plt.tight_layout()
    
    # 儲存
    output_path = '/Users/user/clawd/hr-tools/linkedin-salary-chart-dotnet.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 薪資比較圖已儲存：{output_path}")
    
    return output_path

def create_skill_demand_chart():
    """
    生成技能需求趨勢圖
    """
    
    # 數據
    skills = ['Python', '.NET', 'Java', 'JavaScript', 'Go', 'Rust']
    demand_2024 = [85, 70, 75, 90, 45, 25]
    demand_2025 = [95, 80, 72, 88, 60, 35]
    growth = [(d25 - d24) / d24 * 100 for d24, d25 in zip(demand_2024, demand_2025)]
    
    # 建立圖表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左圖：需求量比較
    x = np.arange(len(skills))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, demand_2024, width, label='2024', color='#A0C4E8', alpha=0.8)
    bars2 = ax1.bar(x + width/2, demand_2025, width, label='2025', color='#4A90E2', alpha=0.8)
    
    ax1.set_ylabel('職缺需求指數', fontsize=12, fontweight='bold')
    ax1.set_xlabel('程式語言', fontsize=12, fontweight='bold')
    ax1.set_title('2024 vs 2025 技能需求比較', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(skills)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 右圖：成長率
    colors_growth = ['#27AE60' if g > 0 else '#E74C3C' for g in growth]
    bars = ax2.barh(skills, growth, color=colors_growth, alpha=0.8)
    
    # 標註成長率數字
    for i, (bar, val) in enumerate(zip(bars, growth)):
        ax2.text(val + 1 if val > 0 else val - 1, i, f'{val:+.0f}%', 
                va='center', fontsize=11, fontweight='bold')
    
    ax2.set_xlabel('成長率 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('2024→2025 需求成長率', fontsize=14, fontweight='bold')
    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.grid(axis='x', alpha=0.3)
    
    # 加入資料來源
    fig.text(0.99, 0.01, 'Data Source: Step1ne 市場調查 | 2025.02', 
            ha='right', fontsize=9, color='gray')
    
    fig.text(0.01, 0.01, '🦞 Step1ne Headhunting', 
            ha='left', fontsize=10, color='#4A90E2', fontweight='bold')
    
    plt.tight_layout()
    
    # 儲存
    output_path = '/Users/user/clawd/hr-tools/linkedin-skill-demand-chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 技能需求圖已儲存：{output_path}")
    
    return output_path

if __name__ == "__main__":
    print("📊 生成 LinkedIn 視覺化內容...")
    
    # 生成薪資比較圖
    salary_chart = create_salary_comparison()
    
    # 生成技能需求圖
    skill_chart = create_skill_demand_chart()
    
    print("\n✅ 所有圖表已生成！")
    print(f"薪資圖：{salary_chart}")
    print(f"技能圖：{skill_chart}")
    print("\n💡 使用建議：")
    print("- 薪資圖：搭配職缺發布，吸引候選人")
    print("- 技能圖：發布產業趨勢文章，建立專業形象")
