# Handover: Compliance Leaderboard

## Goal
Build and run the AI Safety Compliance Leaderboard pipeline + Streamlit dashboard for model card scoring across EU CoP, STREAM, and Lab Safety requirements.

## Current Status (as of 2026-02-01)
- Project scaffold and pipeline implemented in `~/projects/technical-ai-governance-hackathon/compliance-leaderboard`.
- Dependencies installed with `uv sync`.
- Model cards downloaded and converted to markdown.
- Full pipeline run succeeded; outputs written to `results/`.
- Streamlit app launches via `uv run streamlit run run_app.py`.

## Key Commands Run (with outputs)
- `uv sync`
  - Created `.venv` and installed dependencies.
- `uv run python scripts/download_model_cards.py`
  - Downloaded and converted PDFs to markdown:
    - `data/model_cards/claude-opus-4-5.md`
    - `data/model_cards/gpt-4o.md`
    - `data/model_cards/gemini-2-5-pro.md`
    - `data/model_cards/llama-3-1-405b.md`
    - `data/model_cards/deepseek-r1.md`
- `uv run python scripts/run_pipeline.py`
  - Wrote:
    - `results/scores.json`
    - `results/leaderboard.csv`

## Model Access Check (via API)
- OpenAI: many models available (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-5`, etc.).
- Anthropic: available models include
  - `claude-3-5-haiku-20241022`
  - `claude-3-7-sonnet-20250219`
  - `claude-3-haiku-20240307`
  - `claude-haiku-4-5-20251001`
  - `claude-opus-4-1-20250805`
  - `claude-opus-4-20250514`
  - `claude-opus-4-5-20251101`
  - `claude-sonnet-4-20250514`
  - `claude-sonnet-4-5-20250929`

## Config / Env Notes
- `.env` was copied from `~/code/sandbagging-detection/dev/.env` (contains API keys).
- `src/config.py` now calls `load_dotenv()` at import time, so env overrides are read immediately.
- `STAGE_A_MODEL` and `STAGE_B_MODEL` are read from env with defaults.
- `.env` updated with:
  - `STAGE_B_MODEL=anthropic/claude-haiku-4-5-20251001`

## Code Changes / Enhancements
- `scripts/download_model_cards.py` now supports `--from-index` to scan index pages for PDF links:
  - Usage: `uv run python scripts/download_model_cards.py --from-index --index-limit 5`
  - Prints non-PDF links for manual follow-up.
- README + report include model card index pages:
  - `https://www.anthropic.com/system-cards/`
  - `https://deepmind.google/models/model-cards/`
  - `https://openai.com/news/safety-alignment/?display=list`

## Known Issues / Bugs
1) **Streamlit import error**
   - Resolved by running the app via `run_app.py` so the package imports load from repo root.

2) **OpenAI safety index pagination**
   - `https://openai.com/news/safety-alignment/?display=list` has a “Load more” button; crawler only sees initial HTML.
   - Need to discover the underlying API or use headless browser if you want all posts.

## Next Steps (Recommended)
1) **Fix Streamlit imports**
   - Option A: Change imports in `app/app.py` to relative imports and run via `python -m app.app` (or move entrypoint to root).
   - Option B: Keep Streamlit invocation but move pages to a different package name (not `app`), e.g. `ui/`.
   - Option C: Keep `app/` but add a wrapper `run_app.py` at root that adjusts `sys.path` before importing.

2) **Validation (optional)**
   - Fill `validation/human_scores_rater1.csv`.
   - Run: `uv run python scripts/run_validation.py`.

3) **OpenAI index crawl (optional)**
   - Add a fetch step to follow non-PDF links and locate embedded PDF URLs.

## Notes
- There is no git repo initialized in this directory (`git status` failed).
- If you need exact model card sources, they’re listed in README/report.
- The results from pipeline run are already in `results/`.
