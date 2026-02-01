"""Export results to CSV for reporting."""
import json
from pathlib import Path

import pandas as pd

from bootstrap import add_project_root


if __name__ == "__main__":
    add_project_root()

    from src.config import RESULTS_DIR, RUBRIC_PATH
    from src.rubric import load_requirements

    scores_path = RESULTS_DIR / "scores.json"
    if not scores_path.exists():
        raise FileNotFoundError(f"Missing {scores_path}")

    data = json.loads(scores_path.read_text())
    requirements = load_requirements(RUBRIC_PATH)
    req_map = {req.id: req for req in requirements}

    rows = []
    for report in data:
        model = report["model_name"]
        for score in report["scores"]:
            req = req_map.get(score["requirement_id"])
            rows.append(
                {
                    "model": model,
                    "requirement_id": score["requirement_id"],
                    "framework": req.framework if req else "",
                    "category": req.category if req else "",
                    "short_name": req.short_name if req else "",
                    "score": int(score["score"]),
                    "justification": score.get("justification", ""),
                    "evidence": " | ".join(score.get("evidence", [])),
                }
            )

    df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / "scores_flat.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
