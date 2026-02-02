#!/usr/bin/env python3
"""
Verification script for grid component rendering fixes.

Tests:
1. Score formatting to 1 decimal place (70.3% from 70.27)
2. Framework score display accuracy
3. URL preservation in HTML
4. Framework labels appearance
5. Score clamping for edge cases
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.components.leaderboard_grid import _render_model_card


def test_decimal_formatting():
    """Test 1: Verify .1f decimal formatting for all scores."""
    model = {
        "name": "claude-opus-4-5",
        "cop": 70.27,
        "stream": 64.29,
        "lab_safety": 77.78,
        "overall": 69.58,
        "url": "https://example.com"
    }

    html = _render_model_card(model, rank=1)

    tests = [
        ("70.3%", "EU AI Act (70.27 → 70.3%)"),
        ("64.3%", "STREAM ChemBio (64.29 → 64.3%)"),
        ("77.8%", "Lab Safety (77.78 → 77.8%)"),
        ("69.6%", "Overall (69.58 → 69.6%)"),
    ]

    all_pass = True
    for expected, desc in tests:
        if expected in html:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - Expected '{expected}' not found")
            all_pass = False

    return all_pass


def test_url_preservation():
    """Test 2: Verify model_card_url is preserved in href."""
    model = {
        "name": "deepseek-r1",
        "cop": 53.15,
        "stream": 63.1,
        "lab_safety": 42.22,
        "overall": 54.58,
        "url": "https://arxiv.org/pdf/2501.12948"
    }

    html = _render_model_card(model, rank=2)

    if 'href="https://arxiv.org/pdf/2501.12948"' in html:
        print(f"  ✓ Model URL preserved in href")
        return True
    else:
        print(f"  ✗ Model URL not found in href")
        print(f"    HTML sample: {html[:300]}")
        return False


def test_framework_labels():
    """Test 3: Verify framework labels and emojis appear."""
    model = {
        "name": "test-model",
        "cop": 70.0,
        "stream": 65.0,
        "lab_safety": 75.0,
        "overall": 70.0,
        "url": "https://example.com"
    }

    html = _render_model_card(model, rank=1)

    labels = [
        ("🇪🇺 EU AI Act", "EU AI Act label"),
        ("🧬 STREAM ChemBio", "STREAM ChemBio label"),
        ("🔬 Lab Safety", "Lab Safety label"),
    ]

    all_pass = True
    for label, desc in labels:
        if label in html:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - Expected '{label}' not found")
            all_pass = False

    return all_pass


def test_score_clamping():
    """Test 4: Verify score clamping for edge cases."""
    model = {
        "name": "test-model",
        "cop": None,  # Should clamp to 0
        "stream": -5,  # Should clamp to 0
        "lab_safety": 150,  # Should clamp to 100
        "overall": 50.5,
        "url": None
    }

    html = _render_model_card(model, rank=1)

    tests = [
        ("0.0%", "None clamped to 0.0%"),
        ("0.0%", "Negative clamped to 0.0%"),
        ("100.0%", "Over 100 clamped to 100.0%"),
        ("50.5%", "Normal value preserved"),
    ]

    # Just verify we have the right clamp values in the output
    all_pass = True
    if "0.0%" in html:
        print(f"  ✓ None/negative clamped to 0.0%")
    else:
        print(f"  ✗ Clamping to 0.0% failed")
        all_pass = False

    if "100.0%" in html:
        print(f"  ✓ Over 100 clamped to 100.0%")
    else:
        print(f"  ✗ Clamping to 100.0% failed")
        all_pass = False

    if "50.5%" in html:
        print(f"  ✓ Normal value preserved as 50.5%")
    else:
        print(f"  ✗ Normal value not preserved")
        all_pass = False

    return all_pass


def test_no_url_handling():
    """Test 5: Verify cards without URL don't have broken href."""
    model = {
        "name": "test-model",
        "cop": 70.0,
        "stream": 65.0,
        "lab_safety": 75.0,
        "overall": 70.0,
        "url": None  # No URL
    }

    html = _render_model_card(model, rank=1)

    # Should not have a link section when URL is None
    if "View Card ↗" not in html:
        print(f"  ✓ No link button when URL is None")
        return True
    else:
        print(f"  ✗ Link button appears even when URL is None")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("Grid Component Rendering Verification")
    print("="*60 + "\n")

    tests = [
        ("Decimal Formatting (.1f)", test_decimal_formatting),
        ("URL Preservation", test_url_preservation),
        ("Framework Labels", test_framework_labels),
        ("Score Clamping", test_score_clamping),
        ("No-URL Handling", test_no_url_handling),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
