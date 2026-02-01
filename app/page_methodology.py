import json
from pathlib import Path

import pandas as pd
import streamlit as st

from app.utils import RESULTS_DIR


def render() -> None:
    st.title("Methodology & Validation")

    st.header("How Scoring Works")
    rubric_df = pd.DataFrame(
        [
            {"Level": "ABSENT (0)", "Meaning": "No disclosure."},
            {"Level": "MENTIONED (1)", "Meaning": "Mention without details."},
            {"Level": "PARTIAL (2)", "Meaning": "Some details, missing key elements."},
            {"Level": "THOROUGH (3)", "Meaning": "Comprehensive disclosure with evidence."},
        ]
    )
    st.dataframe(rubric_df, width="stretch", hide_index=True)

    st.header("Pipeline Architecture")
    st.code(
        """
Model cards (PDF/HTML)
  -> ingest + chunking
  -> Stage A: claim extraction (LLM + Pydantic)
  -> Stage B: scoring (LLM + rubric)
  -> Stage C: aggregation
  -> results/ (JSON + CSV)
  -> Streamlit dashboard
""".strip(),
        language="text",
    )

    st.header("Validation Results")
    report_path = Path("validation/agreement_report.md")
    if report_path.exists():
        st.markdown(report_path.read_text())
    else:
        st.info("No validation report found. Run `scripts/run_validation.py`.")

    disagreements_path = RESULTS_DIR / "disagreements.json"
    if disagreements_path.exists():
        disagreements = json.loads(disagreements_path.read_text())
        if disagreements:
            st.subheader("Disagreement analysis")
            st.dataframe(pd.DataFrame(disagreements), width="stretch")

    st.header("Frameworks Used")
    st.write(
        "EU Code of Practice for general-purpose AI, STREAM ChemBio evaluation standard, "
        "and lab safety commitments (ASL/Preparedness Framework)."
    )

    st.header("Limitations")
    st.write(
        "- LLM scoring is not ground truth; it reflects disclosure quality.\n"
        "- Rubric interpretation is subjective; agreement metrics quantify reliability.\n"
        "- Model cards are snapshots and may change over time.\n"
        "- Labs could optimize for disclosure scores without improving safety.\n"
        "- Results are not compliance certifications."
    )

    st.header("Methodology Appendix: Prompts Used")
    st.subheader("Stage A: Claim Extraction")
    st.code(
        """
Requirement: {id} - {short_name}
Description: {description}

Chunk text:
{chunk_text}

Task: Determine if this chunk contains information relevant to the requirement.
If relevant, extract concise claims and direct quotes.
Return JSON with keys: relevant, claims, quotes.
""".strip(),
        language="text",
    )

    st.subheader("Stage B: Scoring")
    st.code(
        """
Requirement: {id} - {short_name}
Description: {description}

Scoring guidance:
ABSENT (0): {absent}
MENTIONED (1): {mentioned}
PARTIAL (2): {partial}
THOROUGH (3): {thorough}

Extracted claims: {claims}
Evidence quotes: {quotes}

Task: Assign a score 0-3 and justify using the evidence.
Return JSON with keys: requirement_id, score, justification, evidence, confidence.
""".strip(),
        language="text",
    )
