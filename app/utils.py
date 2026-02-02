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
        df = pd.read_csv(leaderboard_path)
        if "model_card_url" not in df.columns:
            df["model_card_url"] = ""
        return df

    reports = load_reports()
    if not reports:
        return pd.DataFrame()

    rows = []
    for report in reports:
        rows.append(
            {
                "model": report["model_name"],
                "model_card_url": report.get("model_card_url", ""),
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


def render_model_card_banner(model_name: str, model_card_url: str) -> str:
    """Generate HTML for model card source banner.

    Args:
        model_name: Name of the model to display
        model_card_url: URL to the model card source document

    Returns:
        HTML string with tri-gradient banner styling
    """
    return f"""
    <style>
    @import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap");
    .model-card-banner {{
        border: 1px solid #0f172a;
        background: linear-gradient(135deg, #fef3c7 0%, #e0f2fe 55%, #f0fdf4 100%);
        border-radius: 16px;
        padding: 14px 18px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.18);
        margin: 6px 0 18px 0;
    }}
    .model-card-banner .label {{
        font-family: "IBM Plex Sans", sans-serif;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-size: 0.7rem;
        color: #0f172a;
        font-weight: 600;
    }}
    .model-card-banner .title {{
        font-family: "Fraunces", serif;
        font-size: 1.2rem;
        color: #0f172a;
        margin-top: 6px;
    }}
    .model-card-banner a {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 10px;
        font-family: "IBM Plex Sans", sans-serif;
        font-weight: 600;
        color: #0c4a6e;
        text-decoration: none;
        border-bottom: 2px solid rgba(12, 74, 110, 0.3);
        padding-bottom: 2px;
    }}
    .model-card-banner a:hover {{
        color: #075985;
        border-bottom-color: rgba(7, 89, 133, 0.6);
    }}
    </style>
    <div class="model-card-banner">
        <div class="label">Model Card Source</div>
        <div class="title">{model_name}</div>
        <a href="{model_card_url}" target="_blank" rel="noopener noreferrer">
            Open model card ↗
        </a>
    </div>
    """
