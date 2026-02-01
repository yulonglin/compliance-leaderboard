import pandas as pd
import streamlit as st

from app.utils import load_reports, load_requirements


def render() -> None:
    st.title("Requirement Deep Dive")

    requirements = load_requirements()
    reports = load_reports()

    if not requirements:
        st.warning("No rubric found. Ensure data/rubrics/requirements.json exists.")
        return
    if not reports:
        st.warning("No results found. Run `scripts/run_pipeline.py` to generate scores.")
        return

    options = [
        f"{req['framework']} | {req['id']} - {req['short_name']}" for req in requirements
    ]
    selected = st.selectbox("Select requirement", options)
    selected_req = requirements[options.index(selected)]

    st.subheader(f"{selected_req['id']} - {selected_req['short_name']}")
    st.write(selected_req["description"])

    st.markdown("**Scoring guidance**")
    guidance = selected_req["scoring_guidance"]
    guidance_df = pd.DataFrame(
        [
            {"Level": "ABSENT (0)", "Definition": guidance["absent"]},
            {"Level": "MENTIONED (1)", "Definition": guidance["mentioned"]},
            {"Level": "PARTIAL (2)", "Definition": guidance["partial"]},
            {"Level": "THOROUGH (3)", "Definition": guidance["thorough"]},
        ]
    )
    st.dataframe(guidance_df, width="stretch", hide_index=True)

    rows = []
    for report in reports:
        score_entry = next(
            (s for s in report["scores"] if s["requirement_id"] == selected_req["id"]),
            None,
        )
        if score_entry is None:
            rows.append(
                {
                    "Model": report["model_name"],
                    "Score": None,
                    "Justification": "Missing score for this requirement.",
                    "Key Evidence": "",
                }
            )
            continue
        evidence = score_entry.get("evidence", [])
        if isinstance(evidence, str):
            evidence_str = evidence
        else:
            evidence_str = " | ".join(evidence)
        rows.append(
            {
                "Model": report["model_name"],
                "Score": int(score_entry["score"]),
                "Justification": score_entry.get("justification", ""),
                "Key Evidence": evidence_str,
            }
        )

    st.subheader("Cross-model comparison")
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    scored_rows = [row for row in rows if row["Score"] is not None]
    if not scored_rows:
        st.info("No scores available for this requirement yet.")
        return

    best = max(scored_rows, key=lambda r: r["Score"])
    if best["Score"] <= 1:
        st.warning(
            "Industry Gap: No lab provides thorough disclosure for this requirement."
        )
    else:
        st.success(
            f"Best practice: {best['Model']} (score {best['Score']}). "
            "Use this as the gold standard in practice."
        )
