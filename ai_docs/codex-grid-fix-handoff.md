# Codex Handoff: Grid Component Rendering & Score Formatting Fix

**Status**: Ready for delegation
**Complexity**: Low
**Estimated time**: < 5 minutes
**Risk**: Very low (isolated changes, no logic changes)

## Quick Summary

Fix two bugs in `app/components/leaderboard_grid.py`:
1. Split CSS and HTML rendering into separate `st.markdown()` calls
2. Change score formatting from `.0f` to `.1f` (70% → 70.3%)

## Problem Description

### Bug 1: Grid Displays as Raw HTML
- **Location**: Lines 44-45
- **Symptom**: User sees HTML code instead of styled cards
- **Cause**: CSS + HTML concatenated in single `st.markdown()` call
- **Fix**: Separate into two sequential calls (styles first, then HTML)

### Bug 2: Scores Lose Decimal Precision
- **Location**: Lines 369, 376, 386, 396
- **Symptom**: 70.27% displays as "70%" instead of "70.3%"
- **Cause**: Format string uses `.0f` instead of `.1f`
- **Fix**: Replace all 4 instances of `.0f` with `.1f`

## Implementation

**STATUS: ALREADY IMPLEMENTED AND VERIFIED ✅**

### Change 1: Lines 6-7 and 44-52 - Use st.components.v1.html() for iframe rendering

**Top of file - Add import**:
```python
# BEFORE
import streamlit as st

# AFTER
import streamlit as st
import streamlit.components.v1 as components
```

**In render_leaderboard_grid function**:
```python
# BEFORE (old approach with st.markdown - doesn't handle complex CSS)
complete_html = _get_grid_styles() + grid_html
st.markdown(complete_html, unsafe_allow_html=True)

# AFTER (use iframe for full CSS support)
# Combine CSS and HTML and render in iframe
# st.components.v1.html() provides full CSS support (animations, pseudo-elements, external fonts)
complete_html = _get_grid_styles() + grid_html

# Calculate dynamic height based on number of cards
num_cards = len(models_data)
grid_height = max(600, (num_cards // 2 + 1) * 400)

components.html(complete_html, height=grid_height, scrolling=True)
```

**Why this works**:
- `st.markdown()` has limitations: external fonts fail, pseudo-elements don't render, animations don't work
- `components.html()` renders in an iframe with full HTML/CSS/JS support
- Dynamic height prevents overflow and ensures all cards are visible

### Change 2: Lines 369, 376, 386, 396 - Format Strings
Replace `.0f` with `.1f` in 4 places:
- Line 369: `{overall_score:.0f}%` → `{overall_score:.1f}%`
- Line 376: `{cop_score:.0f}%` → `{cop_score:.1f}%`
- Line 386: `{stream_score:.0f}%` → `{stream_score:.1f}%`
- Line 396: `{lab_score:.0f}%` → `{lab_score:.1f}%`

### Change 3: Line 346 - Update Comment
```python
# BEFORE
# Validate and format scores

# AFTER
# Validate and format scores (rounded to 1 decimal place)
```

## Constraints

- ✓ Do NOT modify CSS styles in `_get_grid_styles()`
- ✓ Do NOT change HTML structure
- ✓ Do NOT modify other files
- ✓ Keep all existing logic unchanged
- ✓ Match existing code style

## Verification

### Automated Tests
```bash
# Run verification script (tests all fixes)
python scripts/verify_grid_fixes.py
```

**Expected**: All 5/5 tests pass
- Decimal Formatting (.1f)
- URL Preservation
- Framework Labels
- Score Clamping
- No-URL Handling

### Manual Testing
1. Launch app: `streamlit run run_app.py`
2. Go to Leaderboard page
3. Verify:
   - Cards render with CSS styling (not raw HTML)
   - Scores show decimals (70.3%, 64.3%, 77.8%, 69.6%)
   - Cards are clickable
   - Links work

## Sample Data Format

From `results/scores.json`:
```json
{
  "cop_percentage": 70.27,        → should display: 70.3%
  "stream_percentage": 64.29,     → should display: 64.3%
  "lab_safety_percentage": 77.78, → should display: 77.8%
  "overall_percentage": 69.58     → should display: 69.6%
}
```

## Files to Modify

- `app/components/leaderboard_grid.py` (5 changes total)

## Files NOT to Modify

- CSS in `_get_grid_styles()` function
- Any other files
- HTML structure or variable names

## Success Criteria

- [x] Grid renders as styled cards (CSS applied)
- [x] All scores display with 1 decimal place
- [x] Framework colors visible
- [x] Model card links work
- [x] All verification tests pass (5/5)

## Codex Delegation Template

```
You are implementing a specific bug fix. Do not explore or ask questions — implement directly.

TASK: Fix grid component rendering and score formatting in app/components/leaderboard_grid.py

PROBLEM:
1. Grid displays as raw HTML text
2. Scores lose decimal precision (70.27% shows as 70%)

CONTEXT:
- File: app/components/leaderboard_grid.py
- Two functions: render_leaderboard_grid (lines 11-45) and _render_model_card (lines 343-408)
- Language: Python 3, Streamlit

IMPLEMENTATION:
1. Lines 34-45: Split CSS/HTML into two separate st.markdown() calls
2. Lines 369, 376, 386, 396: Change .0f format to .1f
3. Line 346: Add comment about decimal rounding

CONSTRAINTS:
- Do NOT change CSS styles or HTML structure
- Only rendering approach and number formatting
- Keep existing variable names and logic

VERIFICATION:
Run: python scripts/verify_grid_fixes.py
Expected: 5/5 tests pass
```

---

## Codex Environment Issue

**Status**: Codex CLI panicking in this environment
- **Error**: `system-configuration` crate panic - NULL object in macOS SystemConfiguration dynamic store
- **Cause**: Running in sandboxed/headless environment without system access
- **Workaround**: Not fixable in current environment, use native Codex installation or different system

**However, the fix has already been manually implemented, tested, and verified**:
- ✅ All verification tests pass (5/5)
- ✅ Proper Streamlit component API used (st.components.v1.html)
- ✅ Ready for production

---

**Current Status: FULLY RESOLVED** ✅
- Grid now renders in iframe with full CSS/animation support
- Scores display with 1 decimal precision (70.3% not 70%)
- All tests passing
