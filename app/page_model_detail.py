import pandas as pd
import streamlit as st

from app.utils import level_color, load_reports, requirement_map


def _style_score(value: int) -> str:
    color = level_color(int(value))
    return f"background-color: {color}; color: white; font-weight: 600;"


def _confidence_badge(confidence: float) -> str:
    """Return a colored confidence badge."""
    if confidence >= 0.85:
        return f"🟢 {confidence:.0%}"
    elif confidence >= 0.7:
        return f"🟡 {confidence:.0%}"
    else:
        return f"🔴 {confidence:.0%}"


def render() -> None:
    st.title("Model Deep Dive")

    reports = load_reports()
    if not reports:
        st.warning("No results found. Run `scripts/run_pipeline.py` to generate scores.")
        return

    req_map = requirement_map()
    model_names = [report["model_name"] for report in reports]
    selected = st.selectbox("Select model", model_names)

    report = next(r for r in reports if r["model_name"] == selected)

    cols = st.columns(4)
    cols[0].metric("EU Code of Practice", f"{report['cop_percentage']:.1f}%")
    cols[1].metric("STREAM ChemBio", f"{report['stream_percentage']:.1f}%")
    cols[2].metric("Lab Safety", f"{report['lab_safety_percentage']:.1f}%")
    cols[3].metric("Overall", f"{report['overall_percentage']:.1f}%")

    missing = []
    for score in report["scores"]:
        if int(score["score"]) <= 1:
            req = req_map.get(score["requirement_id"], {})
            missing.append(
                f"{score['requirement_id']} - {req.get('short_name', 'Unknown')}"
            )

    st.subheader("Missing Disclosures")
    if missing:
        st.markdown("\n".join([f"- {item}" for item in missing]))
    else:
        st.success("No missing disclosures detected (all scores >= 2).")

    frameworks = ["EU Code of Practice", "STREAM", "Lab Safety Commitments"]
    for framework in frameworks:
        with st.expander(framework, expanded=True):
            rows = []
            scored = [
                s
                for s in report["scores"]
                if req_map.get(s["requirement_id"], {}).get("framework") == framework
            ]
            for score in scored:
                req = req_map.get(score["requirement_id"], {})
                conf = score.get("confidence", 0.75)
                rows.append(
                    {
                        "Requirement": f"{score['requirement_id']} - {req.get('short_name', '')}",
                        "Score": int(score["score"]),
                        "Confidence": _confidence_badge(conf),
                        "Justification": score.get("justification", ""),
                    }
                )

            if rows:
                df = pd.DataFrame(rows)
                styled = df.style.map(_style_score, subset=["Score"])
                st.dataframe(styled, width="stretch", hide_index=True)
            else:
                st.write("No requirements found for this framework.")

            for score in scored:
                req = req_map.get(score["requirement_id"], {})
                conf = score.get("confidence", 0.75)
                substantive = score.get("substantive")
                conf_indicator = "⚠️ Low confidence" if conf < 0.7 else ""
                subst_indicator = ""
                if substantive is True:
                    subst_indicator = "✅"
                elif substantive is False:
                    subst_indicator = "🚩 Performative"
                title = f"{score['requirement_id']} - {req.get('short_name', '')} {conf_indicator} {subst_indicator}"
                with st.expander(title):
                    cols = st.columns([2, 1, 1])
                    cols[0].write(f"**Score:** {score['score']}/3")
                    cols[1].write(f"**Confidence:** {_confidence_badge(conf)}")
                    if substantive is not None:
                        subst_label = "Substantive" if substantive else "Performative"
                        subst_color = "green" if substantive else "orange"
                        cols[2].markdown(f"**Spirit:** :{subst_color}[{subst_label}]")
                    st.write(score.get("justification", ""))
                    if score.get("substantive_reasoning"):
                        st.info(f"**Spirit assessment:** {score['substantive_reasoning']}")
                    evidence = score.get("evidence", [])
                    if evidence:
                        st.write("**Evidence:**")
                        # Handle evidence as string or list
                        if isinstance(evidence, str):
                            st.markdown(f"- {evidence}")
                        else:
                            st.markdown("\n".join([f"- {item}" for item in evidence]))
                    else:
                        st.write("No evidence extracted.")
