# AI Safety Compliance Leaderboard

## Abstract

[TODO: 150-word abstract summarizing problem, approach, key findings.]

## Problem

AI Lab Watch and similar efforts require manual monitoring that does not scale. The EU Code of Practice, STREAM ChemBio criteria, and lab safety commitments demand systematic disclosure tracking across frontier AI labs.

## Approach

We operationalize 24 requirements across three frameworks into a machine-readable rubric and apply a two-stage LLM pipeline: claim extraction per requirement and rubric-based scoring with evidence. Scores are aggregated into a compliance leaderboard and presented in a Streamlit dashboard.

## Results

[TODO: Insert leaderboard table or screenshot, plus key findings.]

## Validation

We compare automated scores against human ratings on a subset of model cards to compute exact agreement, within-one agreement, and Cohen's kappa. See `validation/agreement_report.md`.

## Model Card Sources

```text
https://www.anthropic.com/system-cards/
https://deepmind.google/models/model-cards/
https://openai.com/news/safety-alignment/?display=list
```

## Limitations & Dual-Use Considerations

- LLM scores are approximations; they measure disclosure quality, not compliance.
- Rubric interpretation is subjective; agreement metrics quantify reliability.
- Model cards are snapshots and may change over time.
- Labs could optimize disclosures without improving safety.
- Results should not be treated as compliance certification.

## Judging Criteria Alignment

- Impact & innovation: scalable compliance monitoring across major safety frameworks.
- Execution quality: structured rubric, evidence-backed scoring, validation pipeline.
- Presentation: dashboard + report with clear methodology and limitations.

## Future Work

- Add more frameworks and regional requirements.
- Track model card updates over time.
- Improve extraction accuracy with human-in-the-loop review.

## Appendix A: Prompts Used

See the Methodology page in the dashboard for prompt templates.

## Appendix B: Requirements

See `data/rubrics/requirements.json` for all 24 requirements.
