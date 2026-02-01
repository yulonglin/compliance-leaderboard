from pathlib import Path
import json
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
RUBRIC_PATH = PROJECT_ROOT / "data" / "rubrics" / "requirements.json"

COLORS = {
    "absent": "#DC2626",
    "mentioned": "#F97316",
    "partial": "#EAB308",
    "thorough": "#16A34A",
    "bg_light": "#F8FAFC",
    "text": "#1E293B",
}


def score_color(pct: float) -> str:
    """Return a color on a smooth gradient from red (0%) -> yellow (50%) -> green (100%)."""
    pct = max(0, min(100, pct))  # Clamp to 0-100

    if pct <= 50:
        # Red (#DC2626) -> Yellow (#EAB308)
        t = pct / 50
        r = int(220 + (234 - 220) * t)  # 220 -> 234
        g = int(38 + (179 - 38) * t)    # 38 -> 179
        b = int(38 + (8 - 38) * t)      # 38 -> 8
    else:
        # Yellow (#EAB308) -> Green (#16A34A)
        t = (pct - 50) / 50
        r = int(234 + (22 - 234) * t)   # 234 -> 22
        g = int(179 + (163 - 179) * t)  # 179 -> 163
        b = int(8 + (74 - 8) * t)       # 8 -> 74

    return f"#{r:02X}{g:02X}{b:02X}"


def level_color(level: int) -> str:
    return [
        COLORS["absent"],
        COLORS["mentioned"],
        COLORS["partial"],
        COLORS["thorough"],
    ][level]


def load_reports() -> List[Dict[str, Any]]:
    scores_path = RESULTS_DIR / "scores.json"
    if not scores_path.exists():
        return []
    return json.loads(scores_path.read_text())


def load_leaderboard() -> pd.DataFrame:
    leaderboard_path = RESULTS_DIR / "leaderboard.csv"
    if leaderboard_path.exists():
        return pd.read_csv(leaderboard_path)

    reports = load_reports()
    if not reports:
        return pd.DataFrame()

    rows = []
    for report in reports:
        rows.append(
            {
                "model": report["model_name"],
                "eu_code_of_practice_pct": report["cop_percentage"],
                "stream_pct": report["stream_percentage"],
                "lab_safety_pct": report["lab_safety_percentage"],
                "overall_pct": report["overall_percentage"],
            }
        )

    df = pd.DataFrame(rows)
    return df.sort_values("overall_pct", ascending=False)


def load_requirements() -> List[Dict[str, Any]]:
    if not RUBRIC_PATH.exists():
        return []
    return json.loads(RUBRIC_PATH.read_text())


def requirement_map() -> Dict[str, Dict[str, Any]]:
    return {req["id"]: req for req in load_requirements()}
