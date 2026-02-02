#!/usr/bin/env python3
"""Generate charts from leaderboard data - standalone version."""

import sys
import csv
from pathlib import Path

# Try importing matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"Error: {e}")
    print("Installing matplotlib...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "matplotlib", "numpy"])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

# Anthropic color palette
DARK_ORANGE = '#D97757'
GREY = '#6B6B6B'
DARK_BLUE = '#2C5282'
MEDIUM_ORANGE = '#E8A87C'
LIGHT_PURPLE = '#B794C0'
DARK_PURPLE = '#6B4C7A'
SLATE = '#141413'
IVORY = '#FAF9F5'
SKY = '#6A9BCC'
FIG = '#C46686'
OLIVE = '#788C5D'

# Project paths
project_root = Path(__file__).parent.parent
results_dir = project_root / "results"
leaderboard_file = results_dir / "leaderboard.csv"
figures_dir = Path(__file__).parent / "figures"
figures_dir.mkdir(exist_ok=True)

# Load data
print(f"Loading data from {leaderboard_file}...")
models_data = []
with open(leaderboard_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        models_data.append({
            'model': row['model'],
            'eu_cop': float(row['eu_code_of_practice_pct']),
            'stream': float(row['stream_pct']),
            'lab_safety': float(row['lab_safety_pct']),
            'overall': float(row['overall_pct'])
        })

print(f"Loaded {len(models_data)} models\n")

# ============================================================================
# Chart 1: Validation Agreement (3 model cards)
# ============================================================================
print("Generating Chart 1: Validation Agreement...")
fig, ax = plt.subplots(figsize=(10, 6))

frameworks = ['EU CoP', 'STREAM ChemBio', 'Lab Safety']
agreements = [100, 100, 100]

x = np.arange(len(frameworks))
bars = ax.bar(x, agreements, color=DARK_BLUE, alpha=0.85, edgecolor=SLATE, linewidth=1.5)

ax.set_ylabel('Agreement (%)', fontsize=12, fontweight='bold', color=SLATE)
ax.set_xlabel('Framework', fontsize=12, fontweight='bold', color=SLATE)
ax.set_title('User Validation Agreement by Framework\n(n=3 model cards)', fontsize=14, fontweight='bold', color=SLATE)
ax.set_xticks(x)
ax.set_xticklabels(frameworks, fontsize=11, color=SLATE)
ax.set_ylim([90, 105])
ax.set_facecolor(IVORY)
fig.patch.set_facecolor('white')
ax.grid(axis='y', alpha=0.2, linestyle='--', color=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GREY)
ax.spines['bottom'].set_color(GREY)

for bar, val in zip(bars, agreements):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold', color=SLATE)

plt.tight_layout()
plt.savefig(figures_dir / 'chart_1_validation_agreement.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  ✓ chart_1_validation_agreement.png")
plt.close()

# ============================================================================
# Chart 2: Framework Scores by Model (all 7 models)
# ============================================================================
print("Generating Chart 2: Framework Scores...")
fig, ax = plt.subplots(figsize=(14, 7))

model_names = [m['model'].replace('-', '\n') for m in models_data]
eu_cop_scores = [m['eu_cop'] for m in models_data]
stream_scores = [m['stream'] for m in models_data]
lab_safety_scores = [m['lab_safety'] for m in models_data]

x = np.arange(len(model_names))
width = 0.25

bars1 = ax.bar(x - width, eu_cop_scores, width, label='EU CoP', color=OLIVE, alpha=0.85, edgecolor=SLATE, linewidth=1)
bars2 = ax.bar(x, stream_scores, width, label='STREAM ChemBio', color=FIG, alpha=0.85, edgecolor=SLATE, linewidth=1)
bars3 = ax.bar(x + width, lab_safety_scores, width, label='Lab Safety', color=SKY, alpha=0.85, edgecolor=SLATE, linewidth=1)

ax.set_ylabel('Disclosure Quality Score (%)', fontsize=12, fontweight='bold', color=SLATE)
ax.set_xlabel('Model', fontsize=12, fontweight='bold', color=SLATE)
ax.set_title('Framework Scores Across Seven Frontier Models', fontsize=14, fontweight='bold', color=SLATE)
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=9, color=SLATE)
ax.set_ylim([0, 90])
ax.set_facecolor(IVORY)
fig.patch.set_facecolor('white')
ax.legend(fontsize=11, loc='upper right', framealpha=0.95)
ax.grid(axis='y', alpha=0.2, linestyle='--', color=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GREY)
ax.spines['bottom'].set_color(GREY)

for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8, color=SLATE)

plt.tight_layout()
plt.savefig(figures_dir / 'chart_2_framework_scores.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  ✓ chart_2_framework_scores.png")
plt.close()

# ============================================================================
# Chart 3: Overall Rankings (horizontal bar)
# ============================================================================
print("Generating Chart 3: Overall Rankings...")
fig, ax = plt.subplots(figsize=(12, 6))

model_names_short = [m['model'].replace('-', ' ') for m in models_data]
overall_scores = [m['overall'] for m in models_data]

y_pos = np.arange(len(model_names_short))
bars = ax.barh(y_pos, overall_scores, color=DARK_BLUE, alpha=0.85, edgecolor=SLATE, linewidth=1.2)

ax.set_xlabel('Overall Disclosure Score (%)', fontsize=12, fontweight='bold', color=SLATE)
ax.set_ylabel('Model', fontsize=12, fontweight='bold', color=SLATE)
ax.set_title('Overall Disclosure Quality Rankings', fontsize=14, fontweight='bold', color=SLATE)
ax.set_yticks(y_pos)
ax.set_yticklabels(model_names_short, fontsize=10, color=SLATE)
ax.set_xlim([0, 90])
ax.set_facecolor(IVORY)
fig.patch.set_facecolor('white')
ax.grid(axis='x', alpha=0.2, linestyle='--', color=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GREY)
ax.spines['bottom'].set_color(GREY)

for bar, score in zip(bars, overall_scores):
    width = bar.get_width()
    ax.text(width - 3, bar.get_y() + bar.get_height()/2.,
            f'{score:.1f}%', ha='right', va='center', fontsize=11,
            fontweight='bold', color='white')

plt.tight_layout()
plt.savefig(figures_dir / 'chart_3_overall_rankings.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  ✓ chart_3_overall_rankings.png")
plt.close()

# ============================================================================
# Chart 4: STREAM vs EU CoP (gap analysis)
# ============================================================================
print("Generating Chart 4: Framework Gap Analysis...")
fig, ax = plt.subplots(figsize=(12, 6))

model_names_gap = [m['model'].replace('-', '\n') for m in models_data]
gaps = [m['stream'] - m['eu_cop'] for m in models_data]

x = np.arange(len(model_names_gap))
colors_gap = [SKY if gap > 0 else FIG for gap in gaps]

bars = ax.bar(x, gaps, color=colors_gap, alpha=0.85, edgecolor=SLATE, linewidth=1.2)

ax.axhline(y=0, color=SLATE, linestyle='-', linewidth=1)
ax.set_ylabel('Gap: STREAM Score - EU CoP Score (%)', fontsize=12, fontweight='bold', color=SLATE)
ax.set_xlabel('Model', fontsize=12, fontweight='bold', color=SLATE)
ax.set_title('Framework Comparison: STREAM vs EU Code of Practice', fontsize=14, fontweight='bold', color=SLATE)
ax.set_xticks(x)
ax.set_xticklabels(model_names_gap, fontsize=9, color=SLATE)
ax.set_facecolor(IVORY)
fig.patch.set_facecolor('white')
ax.grid(axis='y', alpha=0.2, linestyle='--', color=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GREY)
ax.spines['bottom'].set_color(GREY)

for bar, gap in zip(bars, gaps):
    height = bar.get_height()
    va = 'bottom' if height > 0 else 'top'
    y_pos = height + 0.3 if height > 0 else height - 0.3
    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
            f'{gap:+.1f}', ha='center', va=va, fontsize=9, fontweight='bold', color=SLATE)

avg_gap = np.mean(gaps)
ax.axhline(y=avg_gap, color=DARK_ORANGE, linestyle='--', linewidth=2.5, alpha=0.7,
           label=f'Average: {avg_gap:+.1f}pp')
ax.legend(fontsize=11, loc='upper left', framealpha=0.95)

plt.tight_layout()
plt.savefig(figures_dir / 'chart_4_framework_gap.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  ✓ chart_4_framework_gap.png")
plt.close()

# ============================================================================
# Chart 5: Lab Safety Disclosure Gap
# ============================================================================
print("Generating Chart 5: Lab Safety Gap Analysis...")
fig, ax = plt.subplots(figsize=(12, 6))

model_names_lab = [m['model'].replace('-', '\n') for m in models_data]
avg_eu_stream = [(m['eu_cop'] + m['stream']) / 2 for m in models_data]
lab_gaps = [m['lab_safety'] - avg for m, avg in zip(models_data, avg_eu_stream)]

x = np.arange(len(model_names_lab))
colors_lab = [FIG if gap < 0 else DARK_BLUE for gap in lab_gaps]

bars = ax.bar(x, lab_gaps, color=colors_lab, alpha=0.85, edgecolor=SLATE, linewidth=1.2)

ax.axhline(y=0, color=SLATE, linestyle='-', linewidth=1)
ax.set_ylabel('Lab Safety Gap: Lab Safety - Avg(EU CoP, STREAM) (%)', fontsize=11, fontweight='bold', color=SLATE)
ax.set_xlabel('Model', fontsize=12, fontweight='bold', color=SLATE)
ax.set_title('Lab Safety Disclosure Gap Across Models', fontsize=14, fontweight='bold', color=SLATE)
ax.set_xticks(x)
ax.set_xticklabels(model_names_lab, fontsize=9, color=SLATE)
ax.set_facecolor(IVORY)
fig.patch.set_facecolor('white')
ax.grid(axis='y', alpha=0.2, linestyle='--', color=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(GREY)
ax.spines['bottom'].set_color(GREY)

for bar, gap in zip(bars, lab_gaps):
    height = bar.get_height()
    va = 'bottom' if height > 0 else 'top'
    y_pos = height + 0.3 if height > 0 else height - 0.3
    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
            f'{gap:+.1f}', ha='center', va=va, fontsize=9, fontweight='bold', color=SLATE)

avg_lab_gap = np.mean(lab_gaps)
ax.axhline(y=avg_lab_gap, color=DARK_ORANGE, linestyle='--', linewidth=2.5, alpha=0.7,
           label=f'Average: {avg_lab_gap:.1f}pp')
ax.legend(fontsize=11, loc='upper left', framealpha=0.95)

plt.tight_layout()
plt.savefig(figures_dir / 'chart_5_lab_safety_gap.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  ✓ chart_5_lab_safety_gap.png")
plt.close()

print(f"\n✅ All charts generated successfully!")
print(f"📊 Saved to: {figures_dir}")
print(f"📈 Analyzed {len(models_data)} models from {leaderboard_file}")
print(f"\nColor palette: Anthropic brand colors (SLATE, DARK_BLUE, OLIVE, FIG, SKY, DARK_ORANGE)")
