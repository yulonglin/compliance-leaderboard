# AI Safety Compliance Leaderboard - ICLR 2026 Report

## Report Status: COMPLETE (AWAITING SCREENSHOT)

### Main Deliverables

**Report File:** `compliance_leaderboard_report.tex`
- **Structure:** 5 main sections + 7 appendices
- **Target:** 4 pages main body + unlimited appendices
- **Template:** ICLR 2026 Conference Format

### Report Contents

#### Main Body (4 pages)

1. **Introduction** (0.5 pages)
   - Problem: AI Lab Watch shutdown + EU CoP enforcement gap
   - Solution: First automated, evidence-based compliance scoring system
   - Key finding preview: Biosafety disclosure gap across all models

2. **Methodology** (1.5 pages)
   - Framework operationalization (80 requirements: EU CoP, STREAM, Lab Safety)
   - Three-stage pipeline with exact architecture
   - Validation framework with metrics

3. **Results** (1.0 page)
   - Leaderboard rankings (Claude Opus leads 69.6%)
   - Framework analysis (biosafety gap: 4.6 percentage points)
   - Disclosure patterns (score distribution: 0-6.8%, 1-31.5%, 2-32.5%, 3-29.2%)
   - Evidence examples with quotes

4. **Discussion & Conclusions** (1.0 page)
   - Key findings and implications
   - Limitations: measurement vs. actual safety, LLM variability, rubric subjectivity
   - Dual-use considerations: gaming risk, regulatory misuse, information extraction
   - Recommendations for developers, regulators, researchers

#### Appendices (7 sections)

- **Appendix A:** Complete 80-requirement rubric structure
- **Appendix B:** Pipeline prompts (Stage A claim extraction, Stage B scoring)
- **Appendix C:** Model card sources (download dates, URLs)
- **Appendix D:** Validation details (agreement by framework, by score level)
- **Appendix E:** Technical implementation (caching, concurrency, JSON parsing)
- **Appendix F:** Extended results (requirement-level breakdown)
- **Appendix G:** Limitations of automated scoring (failure modes, edge cases)

### Generated Figures & Tables

**Completed:**
✓ Figure 2: Pipeline architecture (TikZ diagram) — `figures/figure_2_pipeline.tex`
✓ Figure 3: Cross-framework heatmap (LaTeX table) — `figures/figure_3_cross_framework_table.tex`
✓ Table 1: Validation metrics — `figures/table_1_validation.tex`
✓ Summary statistics — `figures/summary_stats.json`

**Still Needed (from user):**
⚠️ Figure 1: Leaderboard grid screenshot
   - Browser window showing main leaderboard page
   - All 5 models with rank badges and circular framework gauges
   - Ensure grid fully renders before screenshot

### Key Findings Summary

| Metric | Value |
|--------|-------|
| **Top Model** | Claude Opus 4.5 (69.6%) |
| **Range** | 15.0 percentage points (69.6% - 54.6%) |
| **EU CoP Average** | 64.3% |
| **STREAM Average** | 59.8% |
| **Lab Safety Average** | 57.3% |
| **Biosafety Gap** | 4.6 points (systematic across all models) |
| **Validation Agreement** | 100% exact, Cohen's κ = 1.000 |
| **Score Distribution** | Mostly Partial (32.5%) and Mentioned (31.5%) |

### Data Files Included

```
report/
├── compliance_leaderboard_report.tex          # Main report
├── iclr2026_conference.sty                   # ICLR template files
├── iclr2026_conference.bib
├── iclr2026_conference.bst
├── fancyhdr.sty
├── natbib.sty
│
├── figures/
│   ├── figure_2_pipeline.tex                 # TikZ pipeline diagram
│   ├── figure_3_cross_framework_table.tex    # Cross-framework heatmap
│   ├── table_1_validation.tex                # Validation metrics
│   └── summary_stats.json                    # Summary statistics
│
└── tables/
    └── [validation metrics table]
```

### How to Compile

```bash
cd report/
pdflatex compliance_leaderboard_report.tex
bibtex compliance_leaderboard_report
pdflatex compliance_leaderboard_report.tex
pdflatex compliance_leaderboard_report.tex
```

(Standard LaTeX compilation with bibliography)

### Next Steps

1. **User Action Required:** Provide leaderboard grid screenshot
   - Navigate to Streamlit app main page
   - Ensure grid component fully renders
   - Capture full browser window

2. **Screenshot Integration:** Insert Figure 1 (leaderboard screenshot) into main body
   - Will be embedded in Results section
   - Demonstrates working system and cross-framework variation

3. **Final Compilation:** Generate PDF and verify 4-page target
   - Check figure rendering
   - Verify section breaks
   - Confirm no overfull hbox warnings

4. **Quality Review:** Check against judging criteria
   - ✓ Impact/Innovation: First automated cross-framework system addressing AI Lab Watch gap
   - ✓ Execution Quality: 80-requirement rubric, validated pipeline, clear methodology
   - ✓ Presentation/Clarity: Evidence-based scoring with quote extraction, honest limitations

### Judging Criteria Alignment

**Innovation (Target: 4-5/5)**
- First automated, evidence-based (not binary) compliance measurement
- Addresses real governance gap (AI Lab Watch shutdown)
- Cross-framework integration (EU CoP + STREAM + Lab Safety)
- Evidence extraction enables auditability

**Execution Quality (Target: 4-5/5)**
- Rigorous methodology with three-stage pipeline
- Perfect validation agreement (κ = 1.0) on diverse model cards
- Concrete findings: biosafety gap identified across all models
- Technical sophistication: LLM caching, concurrent processing, JSON fallbacks

**Presentation & Clarity (Target: 4-5/5)**
- Clear problem statement with governance context
- Transparent limitations section (not an afterthought)
- Evidence-quoted examples make scoring auditable
- Honest about dual-use risks and measurement boundaries

### Files Ready for Review

All supporting data files are available in the compliance-leaderboard project:
- `/results/leaderboard.csv` — Rankings
- `/results/scores.json` — Full 400 scores with evidence
- `/validation/human_scores.csv` — Validation data
- `/data/rubrics/requirements.json` — 80-requirement rubric

---

**Status:** Ready for compilation once Figure 1 (leaderboard screenshot) is received.

**Estimated Time to Final PDF:** <10 minutes (compile + embedding screenshot)
