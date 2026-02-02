"""
Verification tests for leaderboard grid component rendering fixes.

Tests verify:
1. Scores display with 1 decimal place (70.3% not 70%)
2. CSS and HTML are properly separated in markdown calls
3. Model card URL links are preserved in HTML
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.components.leaderboard_grid import _render_model_card, _get_grid_styles


def test_score_formatting_one_decimal():
    """Verify scores are formatted to 1 decimal place, not 0."""
    model = {
        "name": "claude-opus-4-5",
        "cop": 70.27,
        "stream": 64.29,
        "lab_safety": 77.78,
        "overall": 69.58,
        "url": "https://example.com/card.pdf"
    }

    html = _render_model_card(model, rank=1)

    # Check overall score is 1 decimal place: 69.6% (from 69.58)
    assert "69.6%" in html, f"Expected '69.6%' in HTML but got: {html[:200]}"
    assert "69%" not in html or "69.6%" in html, "Should not show 69% without decimal"

    # Check framework scores are 1 decimal place
    assert "70.3%" in html, f"Expected '70.3%' (EU AI Act) in HTML"
    assert "64.3%" in html, f"Expected '64.3%' (STREAM) in HTML"
    assert "77.8%" in html, f"Expected '77.8%' (Lab Safety) in HTML"


def test_model_card_url_preserved():
    """Verify model_card_url is correctly embedded in the HTML href."""
    model = {
        "name": "deepseek-r1",
        "cop": 53.15,
        "stream": 63.1,
        "lab_safety": 42.22,
        "overall": 54.58,
        "url": "https://arxiv.org/pdf/2501.12948"
    }

    html = _render_model_card(model, rank=2)

    # Check URL is in the HTML
    assert 'href="https://arxiv.org/pdf/2501.12948"' in html, \
        f"Expected model_card_url in href attribute. Got: {html[:300]}"

    # Check the CTA button exists
    assert "View Card ↗" in html, "Expected 'View Card ↗' button text"


def test_css_styles_present():
    """Verify CSS styles are generated correctly."""
    css = _get_grid_styles()

    # Check for critical CSS classes
    assert ".leaderboard-grid" in css, "Missing .leaderboard-grid class"
    assert ".model-card" in css, "Missing .model-card class"
    assert ".gauge-value" in css, "Missing .gauge-value class"
    assert ".overall-value" in css, "Missing .overall-value class"

    # Check for CSS variables for framework colors
    assert "--color-cop" in css, "Missing --color-cop variable"
    assert "--color-stream" in css, "Missing --color-stream variable"
    assert "--color-lab" in css, "Missing --color-lab variable"

    # Check for framework labels and emojis in HTML structure
    assert "🇪🇺" in css or "EU AI Act" in css, "Missing EU AI Act label"


def test_score_ranges_clamped():
    """Verify scores are clamped between 0-100."""
    model = {
        "name": "test-model",
        "cop": None,  # Test None handling
        "stream": -5,  # Test negative
        "lab_safety": 150,  # Test > 100
        "overall": 50.5,
        "url": None
    }

    html = _render_model_card(model, rank=1)

    # Should clamp None to 0, -5 to 0, 150 to 100
    assert "0.0%" in html, f"Expected '0.0%' for clamped None/negative. Got: {html}"
    assert "100.0%" in html, f"Expected '100.0%' for clamped > 100. Got: {html}"
    assert "50.5%" in html, f"Expected '50.5%' for normal value. Got: {html}"


def test_all_frameworks_labeled():
    """Verify all framework names and emojis appear in rendered card."""
    model = {
        "name": "test-model",
        "cop": 70.0,
        "stream": 65.0,
        "lab_safety": 75.0,
        "overall": 70.0,
        "url": "https://example.com"
    }

    html = _render_model_card(model, rank=1)

    # Check all framework labels are present
    assert "🇪🇺 EU AI Act" in html, "Missing EU AI Act label"
    assert "🧬 STREAM ChemBio" in html, "Missing STREAM label"
    assert "🔬 Lab Safety" in html, "Missing Lab Safety label"

    # Verify they're in the correct structure (gauge divs)
    assert html.count("gauge-label") >= 3, "Expected at least 3 gauge labels"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
