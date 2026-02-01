# AI Safety Compliance Leaderboard

Automated scoring of frontier AI model cards against three frameworks:
- EU AI Act Code of Practice (12 requirements)
- STREAM ChemBio evaluation standard (7 criteria)
- Lab safety commitments (5 requirements from ASL/Preparedness Framework)

This tool measures disclosure quality in model cards, not real-world compliance.

## Quickstart

```bash
uv sync
cp .env.example .env
# Edit .env with API keys
uv run python scripts/download_model_cards.py
# Optional: include extracted images alongside markdown
# uv run python scripts/download_model_cards.py --with-images
uv run python scripts/run_pipeline.py
uv run streamlit run run_app.py
```

## Architecture (text diagram)

```
Model cards (PDF/HTML)
  -> ingest + chunking
  -> Stage A: claim extraction (LLM + Pydantic)
  -> Stage B: scoring (LLM + rubric)
  -> Stage C: aggregation
  -> results/ (JSON + CSV)
  -> Streamlit dashboard
```

## Judging Criteria Alignment

- Impact & innovation: scales compliance monitoring across labs and frameworks.
- Execution quality: structured rubric, evidence-backed scoring, and validation pipeline.
- Presentation: dashboard + report with clear limitations and methodology.

## Limitations & Dual-Use Considerations

- LLM scoring is not ground truth; it approximates disclosure quality.
- Rubric interpretation has subjectivity; validation is required.
- Model cards are snapshots and may update over time.
- Risk of gaming disclosures; evidence-based scoring mitigates but does not eliminate.
- Not a compliance certification; results should be used for transparency and research.

## Model Card Sources (Index Pages)

```text
https://www.anthropic.com/system-cards/
https://deepmind.google/models/model-cards/
https://openai.com/news/safety-alignment/?display=list
```

## Repo Structure

```
app/        Streamlit dashboard
src/        Pipeline code
scripts/    CLI entry points
data/       Model cards + rubric JSON
results/    Pipeline outputs
validation/ Human scoring + agreement
```
