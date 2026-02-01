#!/usr/bin/env python
"""Analyze scores.json to find presentation-worthy insights.

Outputs:
- Requirement with widest variance across models
- Universal failures (all models score ≤1)
- Counter-intuitive results
- Low confidence areas
"""

import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_data():
    """Load scores and requirements data."""
    scores_path = Path(__file__).parent.parent / "results" / "scores.json"
    req_path = Path(__file__).parent.parent / "data" / "rubrics" / "requirements.json"

    with open(scores_path) as f:
        scores = json.load(f)
    with open(req_path) as f:
        requirements = {r["id"]: r for r in json.load(f)}

    return scores, requirements


def analyze_variance(scores: list, requirements: dict) -> list:
    """Find requirements with highest score variance across models."""
    req_scores = defaultdict(list)

    for model in scores:
        for s in model["scores"]:
            req_scores[s["requirement_id"]].append(s["score"])

    variances = []
    for req_id, score_list in req_scores.items():
        if len(score_list) > 1:
            var = statistics.variance(score_list)
            req = requirements.get(req_id, {})
            variances.append({
                "requirement_id": req_id,
                "short_name": req.get("short_name", "Unknown"),
                "framework": req.get("framework", "Unknown"),
                "variance": var,
                "scores": score_list,
                "min": min(score_list),
                "max": max(score_list),
            })

    variances.sort(key=lambda x: x["variance"], reverse=True)
    return variances[:5]


def find_universal_failures(scores: list, requirements: dict) -> list:
    """Find requirements where ALL models score ≤1 (ABSENT or MENTIONED only)."""
    req_scores = defaultdict(list)

    for model in scores:
        for s in model["scores"]:
            req_scores[s["requirement_id"]].append(s["score"])

    failures = []
    for req_id, score_list in req_scores.items():
        if max(score_list) <= 1:
            req = requirements.get(req_id, {})
            failures.append({
                "requirement_id": req_id,
                "short_name": req.get("short_name", "Unknown"),
                "framework": req.get("framework", "Unknown"),
                "scores": score_list,
                "max_score": max(score_list),
            })

    return failures


def find_surprises(scores: list, requirements: dict) -> list:
    """Find counter-intuitive results where expectations differ from reality."""
    surprises = []

    # Build per-model score dict
    model_scores = {}
    for model in scores:
        model_scores[model["model_name"]] = {
            s["requirement_id"]: s["score"] for s in model["scores"]
        }

    # Surprise 1: DeepSeek beats others on specific requirements
    deepseek_wins = []
    for req_id in model_scores.get("deepseek-r1", {}):
        ds_score = model_scores["deepseek-r1"][req_id]
        others_max = max(
            model_scores[m].get(req_id, 0)
            for m in model_scores if m != "deepseek-r1"
        )
        if ds_score > others_max:
            req = requirements.get(req_id, {})
            deepseek_wins.append({
                "requirement_id": req_id,
                "short_name": req.get("short_name", "Unknown"),
                "deepseek_score": ds_score,
                "others_max": others_max,
            })
    if deepseek_wins:
        surprises.append({
            "type": "DeepSeek outperforms",
            "details": deepseek_wins,
        })

    # Surprise 2: Claude (the "safety leader") scores 0 on something
    claude_zeros = []
    for req_id, score in model_scores.get("claude-opus-4-5", {}).items():
        if score == 0:
            req = requirements.get(req_id, {})
            claude_zeros.append({
                "requirement_id": req_id,
                "short_name": req.get("short_name", "Unknown"),
            })
    if claude_zeros:
        surprises.append({
            "type": "Claude scores ABSENT (0)",
            "details": claude_zeros,
        })

    # Surprise 3: GPT-4o (major lab) underperforms on Lab Safety
    gpt_lab_safety = []
    for req_id, score in model_scores.get("gpt-4o", {}).items():
        if req_id.startswith("ASL-"):
            req = requirements.get(req_id, {})
            avg_others = statistics.mean(
                model_scores[m].get(req_id, 0)
                for m in model_scores if m != "gpt-4o"
            )
            if score < avg_others - 0.5:
                gpt_lab_safety.append({
                    "requirement_id": req_id,
                    "short_name": req.get("short_name", "Unknown"),
                    "gpt_score": score,
                    "others_avg": round(avg_others, 2),
                })
    if gpt_lab_safety:
        surprises.append({
            "type": "GPT-4o below average on Lab Safety",
            "details": gpt_lab_safety,
        })

    return surprises


def find_low_confidence(scores: list, requirements: dict) -> list:
    """Find requirements/models with lowest confidence scores."""
    low_conf = []

    for model in scores:
        for s in model["scores"]:
            conf = s.get("confidence", 1.0)
            if conf < 0.7:
                req = requirements.get(s["requirement_id"], {})
                low_conf.append({
                    "model": model["model_name"],
                    "requirement_id": s["requirement_id"],
                    "short_name": req.get("short_name", "Unknown"),
                    "confidence": conf,
                    "score": s["score"],
                })

    low_conf.sort(key=lambda x: x["confidence"])
    return low_conf[:5]


def calculate_framework_averages(scores: list, requirements: dict) -> dict:
    """Calculate average scores by framework and model."""
    framework_scores = defaultdict(lambda: defaultdict(list))

    for model in scores:
        for s in model["scores"]:
            req = requirements.get(s["requirement_id"], {})
            framework = req.get("framework", "Unknown")
            framework_scores[model["model_name"]][framework].append(s["score"])

    averages = {}
    for model, frameworks in framework_scores.items():
        averages[model] = {}
        for framework, score_list in frameworks.items():
            averages[model][framework] = round(
                sum(score_list) / len(score_list) / 3 * 100, 1
            )

    return averages


def main():
    scores, requirements = load_data()

    print("=" * 70)
    print("MODEL CARD TRANSPARENCY TRACKER - KEY INSIGHTS")
    print("=" * 70)
    print()

    # 1. High-variance requirements (most differentiating)
    print("1. REQUIREMENTS WITH HIGHEST VARIANCE (Most Differentiating)")
    print("-" * 70)
    variances = analyze_variance(scores, requirements)
    for v in variances[:3]:
        print(f"   {v['requirement_id']}: {v['short_name']}")
        print(f"   Framework: {v['framework']}")
        print(f"   Score range: {v['min']} to {v['max']} (variance: {v['variance']:.2f})")
        print(f"   Scores: {v['scores']}")
        print()

    # 2. Universal failures
    print("2. UNIVERSAL GAPS (All Models Score ≤1)")
    print("-" * 70)
    failures = find_universal_failures(scores, requirements)
    if failures:
        for f in failures:
            print(f"   {f['requirement_id']}: {f['short_name']}")
            print(f"   Framework: {f['framework']}")
            print(f"   Max score across all models: {f['max_score']}")
            print()
    else:
        print("   No requirements where ALL models fail (score ≤1)")
        print()

    # 3. Surprises
    print("3. COUNTER-INTUITIVE FINDINGS")
    print("-" * 70)
    surprises = find_surprises(scores, requirements)
    for s in surprises:
        print(f"   {s['type']}:")
        for d in s["details"]:
            if "deepseek_score" in d:
                print(f"     - {d['requirement_id']} ({d['short_name']}): "
                      f"DeepSeek={d['deepseek_score']}, Others max={d['others_max']}")
            elif "gpt_score" in d:
                print(f"     - {d['requirement_id']} ({d['short_name']}): "
                      f"GPT={d['gpt_score']}, Others avg={d['others_avg']}")
            else:
                print(f"     - {d['requirement_id']}: {d['short_name']}")
        print()

    # 4. Low confidence areas
    print("4. LOW CONFIDENCE SCORES (< 0.70)")
    print("-" * 70)
    low_conf = find_low_confidence(scores, requirements)
    if low_conf:
        for lc in low_conf:
            print(f"   {lc['model']} on {lc['requirement_id']} ({lc['short_name']})")
            print(f"   Score: {lc['score']}, Confidence: {lc['confidence']}")
            print()
    else:
        print("   All scores have confidence >= 0.70")
        print()

    # 5. Framework averages
    print("5. FRAMEWORK TRANSPARENCY RATES BY MODEL")
    print("-" * 70)
    averages = calculate_framework_averages(scores, requirements)
    print(f"   {'Model':<20} {'EU CoP':>10} {'STREAM':>10} {'Lab Safety':>12}")
    print(f"   {'-'*20} {'-'*10} {'-'*10} {'-'*12}")
    for model, frameworks in sorted(averages.items()):
        cop = frameworks.get("EU Code of Practice", 0)
        stream = frameworks.get("STREAM", 0)
        lab = frameworks.get("Lab Safety Commitments", 0)
        print(f"   {model:<20} {cop:>9.1f}% {stream:>9.1f}% {lab:>11.1f}%")
    print()

    # Summary for presentation
    print("=" * 70)
    print("PRESENTATION TALKING POINTS")
    print("=" * 70)
    print()

    if failures:
        print(f"KEY FINDING 1: Industry-wide gap in {failures[0]['short_name']}")
        print(f"  - ALL 5 labs score ≤1 on {failures[0]['requirement_id']}")
        print()

    if variances:
        top = variances[0]
        print(f"KEY FINDING 2: {top['short_name']} most differentiates labs")
        print(f"  - Score range: {top['min']} to {top['max']} across models")
        print()

    for s in surprises:
        if s["type"] == "Claude scores ABSENT (0)":
            for d in s["details"]:
                print(f"KEY FINDING 3: Even Anthropic scores 0 on {d['short_name']}")
                print(f"  - {d['requirement_id']}: complete absence of disclosure")
                break


if __name__ == "__main__":
    main()
