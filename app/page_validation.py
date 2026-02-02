"""Human validation page for comparing LLM scores against human judgment."""
import csv
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from app.utils import (
    COLORS,
    RESULTS_DIR,
    load_reports,
    load_requirements,
    requirement_map,
    level_color,
)

VALIDATION_DIR = Path("validation")
HUMAN_SCORES_PATH = VALIDATION_DIR / "human_scores.csv"


def _get_validated_pairs() -> set:
    """Get set of (model, requirement_id) pairs already validated."""
    if not HUMAN_SCORES_PATH.exists():
        return set()

    validated = set()
    with open(HUMAN_SCORES_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("score"):  # Only count rows with actual scores
                validated.add((row["model"], row["requirement_id"]))
    return validated


def _get_scoreable_items() -> List[Tuple[str, str, Dict[str, Any]]]:
    """Get list of (model, requirement_id, score_data) that can be validated."""
    reports = load_reports()
    if not reports:
        return []

    items = []
    for report in reports:
        model = report["model_name"]
        model_card_url = report.get("model_card_url")
        model_card_source = report.get("model_card_source")
        for score in report["scores"]:
            score = dict(score)
            if model_card_url:
                score["model_card_url"] = model_card_url
            if model_card_source:
                score["model_card_source"] = model_card_source
            items.append((model, score["requirement_id"], score))
    return items


def _get_random_unvalidated_item() -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """Get a random item that hasn't been validated yet."""
    validated = _get_validated_pairs()
    items = _get_scoreable_items()

    unvalidated = [
        (m, r, s) for m, r, s in items
        if (m, r) not in validated
    ]

    if not unvalidated:
        return None

    return random.choice(unvalidated)


def _save_validation(
    model: str,
    requirement_id: str,
    human_score: int,
    auto_score: int,
    justification: str,
    evidence_quote: str,
    auto_justification: str,
) -> None:
    """Save a human validation to CSV."""
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = HUMAN_SCORES_PATH.exists()

    with open(HUMAN_SCORES_PATH, "a", newline="") as f:
        fieldnames = [
            "timestamp",
            "model",
            "requirement_id",
            "score",
            "auto_score",
            "justification",
            "evidence_quote",
            "auto_justification",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "requirement_id": requirement_id,
            "score": human_score,
            "auto_score": auto_score,
            "justification": justification,
            "evidence_quote": evidence_quote,
            "auto_justification": auto_justification,
        })


def _compute_agreement_stats() -> Dict[str, Any]:
    """Compute agreement statistics from validation data."""
    if not HUMAN_SCORES_PATH.exists():
        return {"n": 0}

    human_scores = []
    auto_scores = []

    with open(HUMAN_SCORES_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("score") and row.get("auto_score"):
                human_scores.append(int(row["score"]))
                auto_scores.append(int(row["auto_score"]))

    if not human_scores:
        return {"n": 0}

    n = len(human_scores)
    exact_matches = sum(1 for h, a in zip(human_scores, auto_scores) if h == a)
    within_one = sum(1 for h, a in zip(human_scores, auto_scores) if abs(h - a) <= 1)

    return {
        "n": n,
        "exact_agreement": round(100 * exact_matches / n, 1),
        "within_one_agreement": round(100 * within_one / n, 1),
        "mean_human": round(sum(human_scores) / n, 2),
        "mean_auto": round(sum(auto_scores) / n, 2),
        "over_scores": sum(1 for h, a in zip(human_scores, auto_scores) if a > h),
        "under_scores": sum(1 for h, a in zip(human_scores, auto_scores) if a < h),
    }


def render() -> None:
    st.title("Human Validation")
    st.caption(
        "Validate LLM-assigned scores against your human judgment. "
        "This helps calibrate the automated scoring system."
    )

    # Show progress stats
    validated = _get_validated_pairs()
    total = len(_get_scoreable_items())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Validated", len(validated))
    with col2:
        st.metric("Remaining", total - len(validated))
    with col3:
        pct = round(100 * len(validated) / total, 1) if total > 0 else 0
        st.metric("Progress", f"{pct}%")

    # Show agreement stats if we have data
    stats = _compute_agreement_stats()
    if stats["n"] >= 5:
        st.subheader("Agreement Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Exact Agreement", f"{stats['exact_agreement']}%")
        with col2:
            st.metric("Within-1 Agreement", f"{stats['within_one_agreement']}%")
        with col3:
            st.metric("LLM Overscores", stats["over_scores"])
        with col4:
            st.metric("LLM Underscores", stats["under_scores"])

    st.divider()

    # Get or refresh item to validate
    if "validation_item" not in st.session_state:
        st.session_state.validation_item = _get_random_unvalidated_item()

    if st.button("🔄 Get New Item"):
        st.session_state.validation_item = _get_random_unvalidated_item()
        st.rerun()

    item = st.session_state.validation_item

    if item is None:
        st.success("All items have been validated! 🎉")
        return

    model, req_id, score_data = item
    req_map = requirement_map()
    req = req_map.get(req_id, {})
    model_card_url = score_data.get("model_card_url")

    # Display the item to validate
    st.subheader(f"Model: {model}")
    st.subheader(f"Requirement: {req_id}")

    if model_card_url:
        from app.utils import render_model_card_banner
        st.markdown(render_model_card_banner(model, model_card_url), unsafe_allow_html=True)

    # Requirement details
    with st.expander("📋 Requirement Details", expanded=True):
        st.write(f"**{req.get('short_name', 'Unknown')}**")
        st.write(req.get("description", "No description available."))

    # Scoring rubric
    with st.expander("📊 Scoring Rubric", expanded=True):
        guidance = req.get("scoring_guidance", {})
        rubric_data = [
            {"Score": "0 - ABSENT", "Criteria": guidance.get("absent", "N/A")},
            {"Score": "1 - MENTIONED", "Criteria": guidance.get("mentioned", "N/A")},
            {"Score": "2 - PARTIAL", "Criteria": guidance.get("partial", "N/A")},
            {"Score": "3 - THOROUGH", "Criteria": guidance.get("thorough", "N/A")},
        ]
        st.table(rubric_data)

    # Evidence from LLM
    with st.expander("📝 LLM Evidence & Justification", expanded=True):
        evidence_raw = score_data.get("evidence", [])
        if isinstance(evidence_raw, str):
            evidence = evidence_raw if evidence_raw else "No evidence extracted."
        elif evidence_raw:
            evidence = "\n".join(f"• {item}" for item in evidence_raw)
        else:
            evidence = "No evidence extracted."
        justification = score_data.get("justification", "No justification provided.")

        st.write("**Evidence from model card:**")
        st.text_area(
            "Evidence",
            value=evidence,
            height=150,
            disabled=True,
            label_visibility="collapsed",
        )

        st.write("**LLM's justification:**")
        st.text_area(
            "Justification",
            value=justification,
            height=100,
            disabled=True,
            label_visibility="collapsed",
        )

    # LLM score (hidden initially to avoid bias)
    show_llm_score = st.checkbox("Show LLM score (check after making your decision)")
    if show_llm_score:
        llm_score = int(score_data.get("score", 0))
        color = level_color(llm_score)
        st.markdown(
            f"**LLM Score:** <span style='background-color: {color}; "
            f"color: white; padding: 4px 8px; border-radius: 4px;'>"
            f"{llm_score}</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Human scoring form
    st.subheader("Your Assessment")

    human_score = st.radio(
        "Score (0-3)",
        options=[0, 1, 2, 3],
        format_func=lambda x: {
            0: "0 - ABSENT",
            1: "1 - MENTIONED",
            2: "2 - PARTIAL",
            3: "3 - THOROUGH",
        }[x],
        horizontal=True,
    )

    human_justification = st.text_area(
        "Your justification (optional)",
        placeholder="Why did you choose this score?",
        height=100,
    )

    if st.button("✅ Submit Validation", type="primary"):
        evidence_raw = score_data.get("evidence", [])
        if isinstance(evidence_raw, list):
            evidence_for_csv = " | ".join(evidence_raw)
        else:
            evidence_for_csv = evidence_raw or ""
        _save_validation(
            model=model,
            requirement_id=req_id,
            human_score=human_score,
            auto_score=int(score_data.get("score", 0)),
            justification=human_justification,
            evidence_quote=evidence_for_csv,
            auto_justification=score_data.get("justification", ""),
        )

        # Show comparison
        llm_score = int(score_data.get("score", 0))
        if human_score == llm_score:
            st.success(f"✓ Exact match! Both you and the LLM scored this as {human_score}.")
        elif abs(human_score - llm_score) == 1:
            st.info(f"≈ Close match. You: {human_score}, LLM: {llm_score} (difference of 1)")
        else:
            st.warning(f"✗ Disagreement. You: {human_score}, LLM: {llm_score} (difference of {abs(human_score - llm_score)})")

        # Get next item
        st.session_state.validation_item = _get_random_unvalidated_item()
        st.rerun()
