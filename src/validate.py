import json
from pathlib import Path
from typing import Dict

import pandas as pd
from sklearn.metrics import cohen_kappa_score


def load_automated_scores(scores_path: Path) -> pd.DataFrame:
    data = json.loads(scores_path.read_text())
    rows = []
    for report in data:
        model = report["model_name"]
        for score in report["scores"]:
            rows.append(
                {
                    "model": model,
                    "requirement_id": score["requirement_id"],
                    "auto_score": int(score["score"]),
                    "auto_justification": score.get("justification"),
                }
            )
    return pd.DataFrame(rows)


def compute_agreement(human_csv: Path, automated_json: Path) -> Dict[str, float]:
    human = pd.read_csv(human_csv)
    auto = load_automated_scores(automated_json)
    merged = human.merge(auto, on=["model", "requirement_id"], how="inner")

    human_scores = merged["score"].dropna().astype(int)
    auto_scores = merged.loc[human_scores.index, "auto_score"].astype(int)

    if human_scores.empty:
        return {
            "n_comparisons": 0,
            "exact_agreement_pct": 0.0,
            "within_one_agreement_pct": 0.0,
            "cohens_kappa": 0.0,
            "mean_human": 0.0,
            "mean_auto": 0.0,
            "auto_overscores_n": 0,
            "auto_underscores_n": 0,
        }

    exact = (human_scores == auto_scores).mean() * 100
    within_one = (abs(human_scores - auto_scores) <= 1).mean() * 100
    kappa = cohen_kappa_score(human_scores, auto_scores, weights="linear")

    return {
        "n_comparisons": int(len(human_scores)),
        "exact_agreement_pct": round(float(exact), 2),
        "within_one_agreement_pct": round(float(within_one), 2),
        "cohens_kappa": round(float(kappa), 3),
        "mean_human": round(float(human_scores.mean()), 2),
        "mean_auto": round(float(auto_scores.mean()), 2),
        "auto_overscores_n": int((auto_scores > human_scores).sum()),
        "auto_underscores_n": int((auto_scores < human_scores).sum()),
    }
