"""
Production-grade leaderboard grid component with compliance visualization.
Displays models with framework scores as circular gauges in a maximalist dashboard aesthetic.
"""

import streamlit as st
import pandas as pd
from pathlib import Path


def render_leaderboard_grid(scores_data: list[dict]):
    """
    Render a visually striking leaderboard grid with compliance rings.

    Args:
        scores_data: List of model report dicts with compliance scores
    """

    # Extract framework scores for each model
    models_data = []
    for report in scores_data:
        models_data.append({
            "name": report["model_name"],
            "cop": report["cop_percentage"],
            "stream": report["stream_percentage"],
            "lab_safety": report["lab_safety_percentage"],
            "overall": report["overall_percentage"],
            "url": report.get("model_card_url")
        })

    # Sort by overall score descending
    models_data.sort(key=lambda x: x["overall"], reverse=True)

    # Create grid container
    grid_html = '<div class="leaderboard-grid">'

    for idx, model in enumerate(models_data):
        rank = idx + 1
        grid_html += _render_model_card(model, rank)

    grid_html += '</div>'

    # Combine CSS and HTML into a single markdown call
    complete_html = _get_grid_styles() + grid_html
    st.markdown(complete_html, unsafe_allow_html=True)


def _get_grid_styles() -> str:
    """Return all CSS for the leaderboard grid component."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --color-cop: #f59e0b;      /* Amber for EU AI Act */
    --color-stream: #06b6d4;   /* Cyan for STREAM */
    --color-lab: #10b981;      /* Emerald for Lab Safety */
    --color-bg: #0f172a;       /* Deep navy */
    --color-card: #1e293b;     /* Slate 800 */
    --color-accent: #ec4899;   /* Fuchsia accent */
    --color-text: #f1f5f9;     /* Slate 100 */
    --color-text-dim: #cbd5e1; /* Slate 300 */
    --duration: 0.35s;
    --ease: cubic-bezier(0.16, 1, 0.3, 1);
}

.leaderboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2.5rem;
    padding: 2rem 0;
    margin: 1rem 0;
}

/* Model Card */
.model-card {
    position: relative;
    background: linear-gradient(135deg, var(--color-card) 0%, rgba(30, 41, 59, 0.8) 100%);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 16px;
    padding: 1.75rem;
    cursor: pointer;
    transition: all var(--duration) var(--ease);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Animated background gradient on hover */
.model-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(236, 72, 153, 0.08) 0%,
        rgba(16, 185, 129, 0.05) 100%
    );
    opacity: 0;
    transition: opacity var(--duration) var(--ease);
    pointer-events: none;
}

.model-card:hover::before {
    opacity: 1;
}

.model-card:hover {
    border-color: rgba(236, 72, 153, 0.3);
    box-shadow:
        0 0 30px rgba(236, 72, 153, 0.15),
        0 10px 40px rgba(0, 0, 0, 0.4);
    transform: translateY(-6px) scale(1.01);
}

/* Rank Badge */
.rank-badge {
    position: absolute;
    top: -12px;
    right: -12px;
    width: 64px;
    height: 64px;
    background: conic-gradient(
        var(--color-accent),
        var(--color-stream),
        var(--color-lab)
    );
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.5rem;
    color: var(--color-bg);
    box-shadow: 0 8px 16px rgba(236, 72, 153, 0.25);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

/* Header Section */
.card-header {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    position: relative;
    z-index: 1;
}

.model-name {
    font-family: 'Lora', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text);
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.model-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--color-text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Overall Score Highlight */
.overall-score {
    background: linear-gradient(
        135deg,
        rgba(236, 72, 153, 0.1) 0%,
        rgba(16, 185, 129, 0.1) 100%
    );
    border: 1px solid rgba(236, 72, 153, 0.2);
    border-radius: 12px;
    padding: 0.875rem;
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    position: relative;
    z-index: 1;
}

.overall-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--color-text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.overall-value {
    font-family: 'Lora', serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--color-accent), var(--color-stream));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Compliance Gauges Section */
.compliance-gauges {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: relative;
    z-index: 1;
}

.gauge {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.gauge-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.gauge-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--color-text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.gauge-value {
    font-family: 'Lora', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text);
}

/* Circular Progress Gauge */
.gauge-bar {
    position: relative;
    height: 8px;
    background: rgba(71, 85, 105, 0.3);
    border-radius: 4px;
    overflow: hidden;
}

.gauge-fill {
    height: 100%;
    border-radius: 4px;
    transition: width var(--duration) var(--ease);
    background-size: 200% 100%;
    animation: shimmer 2s ease-in-out infinite;
}

.gauge-fill.cop {
    background: linear-gradient(90deg, var(--color-cop), rgba(245, 158, 11, 0.6));
}

.gauge-fill.stream {
    background: linear-gradient(90deg, var(--color-stream), rgba(6, 182, 212, 0.6));
}

.gauge-fill.lab {
    background: linear-gradient(90deg, var(--color-lab), rgba(16, 185, 129, 0.6));
}

@keyframes shimmer {
    0%, 100% { background-position: 200% 0; }
    50% { background-position: -200% 0; }
}

.model-card:hover .gauge-fill {
    box-shadow: 0 0 8px currentColor;
}

/* CTA Button */
.card-cta {
    position: relative;
    z-index: 1;
    margin-top: 0.5rem;
}

.cta-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: linear-gradient(135deg, var(--color-accent), #d946ef);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all var(--duration) var(--ease);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.cta-button:hover {
    transform: translateX(4px);
    box-shadow: 0 8px 16px rgba(236, 72, 153, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
    .leaderboard-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .model-name {
        font-size: 1.25rem;
    }

    .overall-value {
        font-size: 1.5rem;
    }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

</style>
"""


def _render_model_card(model: dict, rank: int) -> str:
    """Render a single model card."""

    # Validate and format scores
    cop_score = max(0, min(100, model["cop"] or 0))
    stream_score = max(0, min(100, model["stream"] or 0))
    lab_score = max(0, min(100, model["lab_safety"] or 0))
    overall_score = max(0, min(100, model["overall"] or 0))

    # Determine click behavior
    card_class = "model-card"
    onclick = ""
    if model["url"]:
        onclick = f'onclick="window.open(\'{model["url"]}\', \'_blank\')"'

    card_html = f"""
    <div class="{card_class}" {onclick} style="cursor: {'pointer' if model['url'] else 'default'};">
        <div class="rank-badge">{rank}</div>

        <div class="card-header">
            <div class="model-name">{model['name']}</div>
            <div class="model-subtitle">AI Model Card</div>
        </div>

        <div class="overall-score">
            <div class="overall-label">Overall</div>
            <div class="overall-value">{overall_score:.0f}%</div>
        </div>

        <div class="compliance-gauges">
            <div class="gauge">
                <div class="gauge-label">
                    <span class="gauge-name">🇪🇺 EU AI Act</span>
                    <span class="gauge-value">{cop_score:.0f}%</span>
                </div>
                <div class="gauge-bar">
                    <div class="gauge-fill cop" style="width: {cop_score}%;"></div>
                </div>
            </div>

            <div class="gauge">
                <div class="gauge-label">
                    <span class="gauge-name">🧬 STREAM ChemBio</span>
                    <span class="gauge-value">{stream_score:.0f}%</span>
                </div>
                <div class="gauge-bar">
                    <div class="gauge-fill stream" style="width: {stream_score}%;"></div>
                </div>
            </div>

            <div class="gauge">
                <div class="gauge-label">
                    <span class="gauge-name">🔬 Lab Safety</span>
                    <span class="gauge-value">{lab_score:.0f}%</span>
                </div>
                <div class="gauge-bar">
                    <div class="gauge-fill lab" style="width: {lab_score}%;"></div>
                </div>
            </div>
        </div>

        {f'<div class="card-cta"><a href="{model["url"]}" target="_blank" rel="noopener noreferrer" class="cta-button">View Card ↗</a></div>' if model['url'] else ''}
    </div>
    """

    return card_html


def integrate_with_streamlit():
    """
    Example integration for Streamlit app.
    Call this from your main leaderboard page.
    """
    st.markdown("""
    ## Compliance Leaderboard

    Model disclosure quality across three governance frameworks.
    """)

    # Load scores
    scores_path = Path("results/scores.json")
    if scores_path.exists():
        import json
        scores_data = json.loads(scores_path.read_text())
        render_leaderboard_grid(scores_data)
    else:
        st.warning("No scores found. Run the pipeline first.")
