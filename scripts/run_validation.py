"""Compute agreement metrics between human and automated scores."""
import json
from pathlib import Path

import pandas as pd

from bootstrap import add_project_root


def _write_report(report_path: Path, metrics: dict) -> None:
    lines = [
        "# Agreement Report",
        "",
        f"- Comparisons: {metrics['n_comparisons']}",
        f"- Exact agreement: {metrics['exact_agreement_pct']}%",
        f"- Within-one agreement: {metrics['within_one_agreement_pct']}%",
        f"- Cohen's kappa (linear): {metrics['cohens_kappa']}",
        f"- Mean human score: {metrics['mean_human']}",
        f"- Mean auto score: {metrics['mean_auto']}",
        f"- Auto overscores: {metrics['auto_overscores_n']}",
        f"- Auto underscores: {metrics['auto_underscores_n']}",
    ]
    report_path.write_text("\n".join(lines))


if __name__ == "__main__":
    add_project_root()

    from src.config import RESULTS_DIR, VALIDATION_DIR
    from src.validate import compute_agreement, load_automated_scores

    human_csv = VALIDATION_DIR / "human_scores_rater1.csv"
    scores_json = RESULTS_DIR / "scores.json"

    if not human_csv.exists():
        raise FileNotFoundError(f"Missing {human_csv}")
    if not scores_json.exists():
        raise FileNotFoundError(f"Missing {scores_json}")

    metrics = compute_agreement(human_csv, scores_json)

    auto = load_automated_scores(scores_json)
    human = pd.read_csv(human_csv)
    merged = human.merge(auto, on=["model", "requirement_id"], how="inner")
    scored = merged[merged["score"].notna()].copy()
    disagreements = scored[scored["score"].astype(int) != scored["auto_score"]]

    disagreements_payload = disagreements[
        [
            "model",
            "requirement_id",
            "score",
            "auto_score",
            "justification",
            "auto_justification",
            "evidence_quote",
        ]
    ].to_dict(orient="records")

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "disagreements.json").write_text(
        json.dumps(disagreements_payload, ensure_ascii=True, indent=2)
    )
    _write_report(VALIDATION_DIR / "agreement_report.md", metrics)

    print("Validation complete")
