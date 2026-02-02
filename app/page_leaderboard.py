import json
import streamlit as st
from pathlib import Path

from app.utils import load_leaderboard, score_color
from app.components.leaderboard_grid import render_leaderboard_grid


def _style_pct(value: float) -> str:
    color = score_color(float(value))
    return f"background-color: {color}; color: white; font-weight: 600;"


def render() -> None:
    st.title("AI Safety Compliance Leaderboard")
    st.caption(
        "Automated scoring of frontier AI model cards against the EU Code of Practice, "
        "STREAM ChemBio criteria, and lab safety commitments."
    )
    st.info(
        "This tool measures disclosure quality, not real-world compliance. "
        "Scores reflect what labs publish, not what they practice."
    )

    # Try to load raw scores for grid visualization
    scores_path = Path("results/scores.json")
    if scores_path.exists():
        try:
            scores_data = json.loads(scores_path.read_text())
            st.markdown("### Compliance Score Matrix")
            render_leaderboard_grid(scores_data)
        except Exception as e:
            st.error(f"Error loading grid: {e}")

    # Show traditional table view
    st.markdown("---")
    st.markdown("### Detailed Leaderboard Table")

    df = load_leaderboard()
    if df.empty:
        st.warning("No results found. Run `scripts/run_pipeline.py` to generate scores.")
        return

    df = df.copy()
    df.insert(0, "rank", range(1, len(df) + 1))

    # Format percentage columns to 1 decimal place
    for col in ["eu_code_of_practice_pct", "stream_pct", "lab_safety_pct", "overall_pct"]:
        df[col] = df[col].apply(lambda x: round(x, 1))

    df = df.rename(
        columns={
            "model": "Model",
            "model_card_url": "Model Card",
            "eu_code_of_practice_pct": "EU Code of Practice",
            "stream_pct": "STREAM ChemBio",
            "lab_safety_pct": "Lab Safety",
            "overall_pct": "Overall",
            "rank": "Rank",
        }
    )

    style_cols = ["EU Code of Practice", "STREAM ChemBio", "Lab Safety", "Overall"]
    styled = df.style.map(_style_pct, subset=style_cols)

    st.dataframe(
        styled,
        width="stretch",
        hide_index=True,
        column_config={
            "Model Card": st.column_config.LinkColumn(
                "Model Card",
                display_text="Open",
            ),
        },
    )
