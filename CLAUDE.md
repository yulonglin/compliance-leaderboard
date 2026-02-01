# CLAUDE.md

## Project Overview
AI Safety Compliance Leaderboard: automated scoring of frontier AI model cards against three frameworks (EU AI Act Code of Practice, STREAM ChemBio, Lab Safety). The system measures **disclosure quality** in model cards, not real-world compliance.

## Quickstart
```bash
uv sync
cp .env.example .env
# Edit .env with API keys
uv run python scripts/download_model_cards.py
uv run python scripts/run_pipeline.py
uv run streamlit run run_app.py
```

## Key Paths
- Model cards (markdown): `data/model_cards/`
- Rubric JSON: `data/rubrics/requirements.json`
- Pipeline outputs: `results/scores.json`, `results/leaderboard.csv`
- Validation data: `validation/human_scores.csv`

## Pipeline Notes
- Stages live in `src/pipeline.py` (claim extraction -> scoring -> aggregation).
- Models are configured via env vars in `src/config.py`:
  - `STAGE_A_MODEL` (default: `google/gemini-2.5-flash-lite`)
  - `STAGE_B_MODEL` (default: `anthropic/claude-sonnet-4-5-20250514`)
- LLM cache: `.cache/llm/`

## Streamlit App
- Launch with `uv run streamlit run run_app.py` (wrapper avoids import path issues).
- Validation UI lives in `app/page_validation.py`.

## Validation
- Human validation writes to `validation/human_scores.csv`.
- Agreement metrics: `uv run python scripts/run_validation.py`.

## Gotchas
- Model cards are snapshots; re-run `scripts/download_model_cards.py` when updating sources.
- For Streamlit, use `run_app.py` (direct module execution may break imports).
