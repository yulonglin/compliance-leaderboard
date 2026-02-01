"""Run full extraction + scoring pipeline."""
import asyncio
import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from bootstrap import add_project_root


def _build_leaderboard(reports: list[dict]) -> pd.DataFrame:
    rows = []
    for report in reports:
        rows.append(
            {
                "model": report["model_name"],
                "model_card_url": report.get("model_card_url"),
                "eu_code_of_practice_pct": report["cop_percentage"],
                "stream_pct": report["stream_percentage"],
                "lab_safety_pct": report["lab_safety_percentage"],
                "overall_pct": report["overall_percentage"],
            }
        )
    df = pd.DataFrame(rows)
    return df.sort_values("overall_pct", ascending=False)


async def _run_all(model_card_dir: Path, rubric_path: Path) -> list[dict]:
    from src.config import load_env
    from src.ingest import list_model_cards
    from src.pipeline import run_pipeline
    from src.rubric import load_requirements

    load_env()
    requirements = load_requirements(rubric_path)
    model_cards = list_model_cards(model_card_dir)
    sources_path = model_card_dir / "sources.json"
    sources = {}
    if sources_path.exists():
        sources = json.loads(sources_path.read_text())

    print(f"Processing {len(model_cards)} models × {len(requirements)} requirements")

    reports: list[dict] = []
    for card_path in tqdm(model_cards, desc="Models"):
        model_name = card_path.stem
        model_card_url = sources.get(model_name)
        report = await run_pipeline(model_name, card_path, requirements, model_card_url=model_card_url)
        reports.append(report.model_dump())
    return reports


if __name__ == "__main__":
    add_project_root()

    from src.config import MODEL_CARD_DIR, RESULTS_DIR, RUBRIC_PATH

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    reports = asyncio.run(_run_all(MODEL_CARD_DIR, RUBRIC_PATH))
    scores_path = RESULTS_DIR / "scores.json"
    scores_path.write_text(json.dumps(reports, ensure_ascii=True, indent=2))

    leaderboard = _build_leaderboard(reports)
    leaderboard.to_csv(RESULTS_DIR / "leaderboard.csv", index=False)

    print(f"Saved {scores_path}")
