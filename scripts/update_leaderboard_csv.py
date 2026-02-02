#!/usr/bin/env python3
"""Update leaderboard.csv with model_card_url column"""

import json
import pandas as pd
from pathlib import Path

# Load updated scores
scores = json.loads(Path("results/scores.json").read_text())

# Build leaderboard data
rows = []
for report in scores:
    rows.append({
        "model": report["model_name"],
        "model_card_url": report.get("model_card_url"),
        "eu_code_of_practice_pct": report["cop_percentage"],
        "stream_pct": report["stream_percentage"],
        "lab_safety_pct": report["lab_safety_percentage"],
        "overall_pct": report["overall_percentage"],
    })

df = pd.DataFrame(rows).sort_values("overall_pct", ascending=False)
df.to_csv("results/leaderboard.csv", index=False)

print(f"✓ Updated leaderboard.csv with {len(df)} models")
print(df[["model", "overall_pct", "model_card_url"]].head().to_string())
