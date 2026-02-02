#!/usr/bin/env python3
"""Patch existing scores.json to add model_card_url field from sources.json"""

import json
from pathlib import Path

# Load sources (model card URLs)
sources_path = Path("data/model_cards/sources.json")
sources = json.loads(sources_path.read_text()) if sources_path.exists() else {}

# Load existing scores
scores_path = Path("results/scores.json")
scores = json.loads(scores_path.read_text())

# Add model_card_url to each report
for report in scores:
    model_name = report["model_name"]
    report["model_card_url"] = sources.get(model_name)

# Write back
scores_path.write_text(json.dumps(scores, indent=2, ensure_ascii=True))

# Verify
first_model = scores[0]
print(f"✓ Added model_card_url to {len(scores)} models")
print(f"  First model: {first_model['model_name']}")
print(f"  URL: {first_model.get('model_card_url')}")
