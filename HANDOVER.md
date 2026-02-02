# Handover: Compliance Leaderboard

## Context / Goal
- Fix pipeline reliability and evidence quality (no guideline leakage), add model card links in UI, support PDF→MD conversion, rerun pipeline and refresh dashboard.

## Current State
- `src/pipeline.py` has uncommitted edits; no other files modified right now.
- Mini-run succeeded: `run_pipeline()` on `deepseek-r1` with 3 requirements completed without JSON errors.
- Full pipeline still not rerun after recent changes.

## What Was Done (Files / Behavior)
- Model card sources:
  - Added `data/model_cards/sources.json` mapping model → URL.
  - Fixed Claude Opus 4.5 model card URL (was pointing to wrong doc).
  - Added GPT‑5.2 model card.
  - `scripts/download_model_cards.py` now writes `sources.json` and can `--with-images` (saves images per model, rewrites paths).
- Evidence expansion:
  - Stage A returns `quote_spans` with offsets.
  - Quotes expanded to ±2 paragraphs around each span.
- Cache hardening:
  - Prompt-version salts in cache keys: `STAGE_A_PROMPT_VERSION`, `STAGE_B_PROMPT_VERSION`.
- UI:
  - Leaderboard shows “Model Card” link column.
  - Validation page shows a model-card source banner.
- Stage A model default:
  - If `OPENROUTER_API_KEY` set, use `openrouter/google/gemini-2.5-flash`.
  - Otherwise `gemini/gemini-2.5-flash`.

## Commands Run (Outcomes)
- `uv run python scripts/download_model_cards.py`
  - Regenerated Opus 4.5, added GPT‑5.2, wrote `data/model_cards/sources.json`.
- Ad‑hoc Stage A/B calls via `litellm.acompletion` (JSON returned OK in samples).
- Mini pipeline run (3 requirements on `deepseek-r1`) succeeded.

## Known Issues / Bugs
### 1) JSON parse failures in full pipeline
**Symptom:** Stage A sometimes returns invalid JSON (seen in full run), causing `LlmResponseError: Invalid JSON`.
**Evidence:** Sporadic; ad‑hoc calls + mini‑run were OK.
**Current mitigation:** `_extract_json` normalizes output (trailing commas, True/False/None, double‑quoted keys).
**Likely root cause:** Model occasionally emits malformed JSON under load/concurrency; schema not enforced.
**Proposed fix:** Use strict `response_format` / JSON schema (Pydantic) for Stage A/B calls; if still flaky, consider stricter parsing or model switch for Stage A.

### 2) “Guidelines leakage” (requirement/scoring text appears as evidence)
**Symptom:** Evidence/claims show requirement text or scoring guidance not present in model card.
**Root cause:** Stage A sees requirement + guidance in prompt; claims are not validated against quotes. Even if quotes are empty, claims can survive and propagate into Stage B/UX.
**Fix options (recommended):**
1) If `quote_spans` empty → force `relevant=false` and `claims=[]`.
2) Drop any claim without at least one supporting quote span.
3) Filter claims that are near‑duplicates of requirement/guidance text.
4) In Stage B, ignore claims and score from `quotes` only.

## Open Decisions
- PDF→MD conversion toolchain with images:
  - Option A: PyMuPDF (pure Python)
  - Option B: Poppler CLI (`pdftotext` + `pdfimages`)
  - Option C: `marker` (higher fidelity, heavier deps)

## Outstanding TODOs
- Implement guardrails to prevent guideline leakage (see options above).
- Improve JSON reliability (schema response_format or model swap).
- Add PDF→MD script (once toolchain chosen).
- Rerun full pipeline + refresh Streamlit dashboard.
- Run CodeRabbit review once CLI is installed/authenticated.

## Rerun Checklist
1) Ensure `.env` has required keys (OpenRouter/Gemini/Anthropic as applicable).
2) If prompt changes, bump `STAGE_A_PROMPT_VERSION` / `STAGE_B_PROMPT_VERSION` or clear `.cache/llm`.
3) Re-download model cards if sources changed:
   - `uv run python scripts/download_model_cards.py [--with-images]`
4) Run pipeline:
   - `uv run python scripts/run_pipeline.py`
5) Run app:
   - `uv run streamlit run run_app.py`

