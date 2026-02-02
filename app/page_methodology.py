import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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

    st.header("Frameworks & Standards")
    components.html(
        """
<style>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap");

body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.framework-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin: 24px 0;
    padding: 20px;
}

.framework-card {
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.framework-card:hover {
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
    transform: translateY(-2px);
}

.framework-card.eu {
    background: linear-gradient(135deg, #fef3c7 0%, #fefce8 100%);
    border-left: 4px solid #f59e0b;
}

.framework-card.stream {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
    border-left: 4px solid #0284c7;
}

.framework-card.lab-safety {
    background: linear-gradient(135deg, #f0fdf4 0%, #f7fee7 100%);
    border-left: 4px solid #10b981;
}

.framework-card .label {
    font-family: "IBM Plex Sans", sans-serif;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 600;
    opacity: 0.7;
    margin-bottom: 8px;
}

.framework-card .title {
    font-family: "Fraunces", serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 12px;
    line-height: 1.3;
}

.framework-card .description {
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.9rem;
    color: #1e293b;
    line-height: 1.6;
    margin-bottom: 14px;
}

.framework-card a {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: "IBM Plex Sans", sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    text-decoration: none;
    color: #0c4a6e;
    border-bottom: 2px solid rgba(12, 74, 110, 0.25);
    padding-bottom: 1px;
    transition: all 0.2s ease;
}

.framework-card a:hover {
    color: #075985;
    border-bottom-color: rgba(7, 89, 133, 0.5);
}

.framework-card.eu a { color: #d97706; border-bottom-color: rgba(217, 119, 6, 0.3); }
.framework-card.eu a:hover { color: #b45309; border-bottom-color: rgba(180, 83, 9, 0.5); }

.framework-card.stream a { color: #0369a1; border-bottom-color: rgba(3, 105, 161, 0.3); }
.framework-card.stream a:hover { color: #075985; border-bottom-color: rgba(7, 89, 133, 0.5); }

.framework-card.lab-safety a { color: #059669; border-bottom-color: rgba(5, 150, 105, 0.3); }
.framework-card.lab-safety a:hover { color: #047857; border-bottom-color: rgba(4, 120, 87, 0.5); }
</style>

<div class="framework-grid">
    <div class="framework-card eu">
        <div class="label">European Union</div>
        <div class="title">AI Act Code of Practice</div>
        <div class="description">
            Transparency, copyright, and safety requirements for general-purpose AI models under the EU AI Act. Enforcement begins August 2026.
        </div>
        <a href="https://code-of-practice.ai/" target="_blank" rel="noopener noreferrer">
            View framework ↗
        </a>
    </div>

    <div class="framework-card stream">
        <div class="label">GovAI & Expert Consortium</div>
        <div class="title">STREAM ChemBio</div>
        <div class="description">
            Standard for Transparently Reporting Evaluations in AI Model Reports. 28 criteria across threat relevance, test construction, and results interpretation for CBRN risks.
        </div>
        <a href="https://streamevals.com/" target="_blank" rel="noopener noreferrer">
            View framework ↗
        </a>
    </div>

    <div class="framework-card lab-safety">
        <div class="label">Frontier AI Labs</div>
        <div class="title">Lab Safety Commitments</div>
        <div class="description">
            Responsible Scaling Policies (Anthropic, OpenAI, DeepMind) defining capability thresholds, evaluation cadences, and deployment safeguards for frontier models.
        </div>
        <a href="https://www.anthropic.com/responsible-scaling-policy" target="_blank" rel="noopener noreferrer">
            Anthropic RSP ↗
        </a>
        <span style="margin: 0 8px; opacity: 0.4;">|</span>
        <a href="https://openai.com/index/updating-our-preparedness-framework/" target="_blank" rel="noopener noreferrer">
            OpenAI Preparedness ↗
        </a>
    </div>
</div>
""",
        height=600,
        scrolling=True,
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
