import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from litellm import acompletion
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm_asyncio

from .cache import FileCache
from .config import (
    CACHE_DIR,
    CHUNK_MAX_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    STAGE_A_CONCURRENCY,
    STAGE_A_MODEL,
    STAGE_A_PROMPT_VERSION,
    STAGE_B_CONCURRENCY,
    STAGE_B_MODEL,
    STAGE_B_PROMPT_VERSION,
)
from .ingest import chunk_text, read_model_card
from .models import ClaimExtraction, ModelReport, QuoteSpan, Requirement, RequirementScore, ScoreLevel


class LlmResponseError(RuntimeError):
    pass


_PARA_SPLIT_RE = re.compile(r"\n\s*\n")


def _escape_newlines_in_strings(text: str) -> str:
    """Escape literal newlines inside JSON string values."""
    output: List[str] = []
    in_string = False
    escape = False
    for ch in text:
        if escape:
            output.append(ch)
            escape = False
            continue
        if ch == "\\":
            output.append(ch)
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            output.append(ch)
            continue
        # Replace literal newlines/carriage returns with space (preserves JSON validity)
        if in_string and ch in ("\n", "\r"):
            output.append(" ")
            continue
        output.append(ch)
    return "".join(output)


def _hash_key(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _extract_json(text: str) -> Dict:
    if not text:
        raise LlmResponseError("Empty response")
    start = text.find("{")
    if start == -1:
        raise LlmResponseError("No JSON object found")

    # Find matching closing brace by counting depth
    depth = 0
    in_string = False
    escape = False
    end = -1
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break

    if end == -1:
        # Handle incomplete JSON by adding closing braces
        payload = text[start:]
        # Count open braces and add appropriate closing braces
        depth = 0
        in_string = False
        escape = False
        for ch in payload:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if not in_string:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
        payload += "}" * max(0, depth)
    else:
        # Extract only up to the matching closing brace (first complete JSON object)
        payload = text[start : end + 1]

    payload = _escape_newlines_in_strings(payload)

    # Use raw_decode first to extract just the first JSON object
    # This handles cases where LLM returns multiple JSON objects or has trailing content
    decoder = json.JSONDecoder()
    try:
        result, idx = decoder.raw_decode(payload)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass  # Fall through to further attempts

    # Fallback: try standard JSON parsing (might fail but worth trying)
    try:
        result = json.loads(payload)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass  # Fall through to normalization

    # Normalization for malformed JSON
    # Fix trailing commas
    normalized = re.sub(r",\s*([}\]])", r"\1", payload)

    # Fix missing commas between top-level structures
    normalized = re.sub(r'(\})\s*(\{)', r'\1,\2', normalized)
    normalized = re.sub(r'(\])\s*(\[)', r'\1,\2', normalized)

    # Fix missing commas after strings in arrays - this is the critical one
    # Match: closing quote, optional whitespace, then { or [ or " (not followed by :)
    normalized = re.sub(r'(")\s*(?=[\{\[])', r'\1,', normalized)
    # Also handle string followed by string in array (most common case)
    normalized = re.sub(r'(")\s+(")', r'\1,\2', normalized)

    # Python boolean/None to JSON
    normalized = re.sub(r"\bTrue\b", "true", normalized)
    normalized = re.sub(r"\bFalse\b", "false", normalized)
    normalized = re.sub(r"\bNone\b", "null", normalized)

    # Fix malformed keys: ""key"" or ""key" or "key""
    normalized = re.sub(r'"+([a-zA-Z_][a-zA-Z0-9_]*)"*\s*:', r'"\1":', normalized)

    # Remove trailing empty string keys
    normalized = re.sub(r',\s*"":', r'', normalized)
    normalized = re.sub(r',\s*""\s*([}\]])', r'\1', normalized)

    # Remove ALL unescaped newlines/tabs outside strings (last resort)
    in_string = False
    escape = False
    cleaned = []
    for ch in normalized:
        if escape:
            cleaned.append(ch)
            escape = False
        elif ch == "\\":
            cleaned.append(ch)
            escape = True
        elif ch == '"':
            in_string = not in_string
            cleaned.append(ch)
        elif not in_string and ch in ("\n", "\r", "\t"):
            continue
        else:
            cleaned.append(ch)
    normalized = "".join(cleaned)
    try:
        return json.loads(normalized)
    except json.JSONDecodeError as exc:
        # Last resort: extract structured fields manually for common errors
        # This handles cases where LLM returns incomplete JSON structures
        try:
            result = {}
            # Extract relevant field
            relevant_match = re.search(r'"relevant"\s*:\s*(true|false)', normalized)
            result["relevant"] = relevant_match is not None and relevant_match.group(1) == "true"

            # Extract claims array
            claims_match = re.search(r'"claims"\s*:\s*\[(.*?)(?:\]|$)', normalized, re.DOTALL)
            result["claims"] = []
            if claims_match:
                claims_str = claims_match.group(1)
                # Find all quoted strings
                claim_matches = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', claims_str)
                result["claims"] = [c.replace('\\"', '"').replace('\\\\', '\\') for c in claim_matches if c]

            # Extract quote_spans if present
            quote_spans_match = re.search(r'"quote_spans"\s*:\s*\[(.*?)(?:\]|$)', normalized, re.DOTALL)
            result["quote_spans"] = []
            if quote_spans_match:
                spans_str = quote_spans_match.group(1)
                # Find all quote span objects
                span_matches = re.findall(r'\{[^}]*"quote"[^}]*\}', spans_str)
                for span_str in span_matches:
                    try:
                        span = json.loads(span_str + "}")
                        result["quote_spans"].append(span)
                    except:
                        pass

            # Return what we extracted (even if incomplete), with defaults
            return {
                "relevant": result.get("relevant", False),
                "claims": result.get("claims", []),
                "quote_spans": result.get("quote_spans", []),
            }
        except:
            # Last resort: return empty/false extraction
            return {"relevant": False, "claims": [], "quote_spans": []}


async def _call_llm_json(
    model: str,
    messages: List[Dict[str, str]],
    response_format: type | dict | None = None,
) -> Dict:
    async for attempt in AsyncRetrying(
        wait=wait_exponential(min=1, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    ):
        with attempt:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=0,
                response_format=response_format or {"type": "json_object"},
            )
            content = response.choices[0].message.content
            return _extract_json(content)
    raise LlmResponseError("LLM call failed after retries")


def _stage_a_prompt(requirement: Requirement, chunk_text: str) -> List[Dict[str, str]]:
    system = (
        "You are extracting compliance-related claims from a model card. "
        "Return only valid JSON."
    )
    user = (
        "Requirement:\n"
        f"ID: {requirement.id}\n"
        f"Framework: {requirement.framework}\n"
        f"Description: {requirement.description}\n\n"
        "Chunk text:\n"
        f"{chunk_text}\n\n"
        "Task: Determine if this chunk contains information relevant to the requirement. "
        "If relevant, extract concise claims and direct quotes. Quotes MUST be verbatim substrings "
        "from the chunk text and must include character offsets.\n\n"
        "Rules:\n"
        "- Do NOT restate the requirement text.\n"
        "- If there is no direct evidence in the chunk, set relevant=false and return empty lists.\n"
        "- Provide offsets as 0-indexed character positions in the chunk text (end is exclusive).\n"
        "- All strings must be single-line; replace any newlines with spaces.\n\n"
        "Return JSON with keys: relevant (boolean), claims (list of strings), "
        "quote_spans (list of objects with keys: quote, start, end)."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _stage_b_prompt(requirement: Requirement, claims: List[str], quotes: List[str]) -> List[Dict[str, str]]:
    system = (
        "You are scoring compliance disclosure quality. "
        "Use the rubric and evidence. Return only valid JSON. "
        "Beyond scoring presence of disclosure, also assess whether the disclosure is SUBSTANTIVE "
        "(genuine safety work with meaningful detail) vs PERFORMATIVE (checkbox compliance, vague claims, "
        "boilerplate language without specific commitments or results)."
    )
    guidance = requirement.scoring_guidance
    user = (
        "Requirement:\n"
        f"ID: {requirement.id}\n"
        f"Framework: {requirement.framework}\n"
        f"Short name: {requirement.short_name}\n"
        f"Description: {requirement.description}\n\n"
        "Scoring guidance:\n"
        f"ABSENT (0): {guidance.absent}\n"
        f"MENTIONED (1): {guidance.mentioned}\n"
        f"PARTIAL (2): {guidance.partial}\n"
        f"THOROUGH (3): {guidance.thorough}\n\n"
        "Extracted claims:\n"
        f"{json.dumps(claims, ensure_ascii=True)}\n\n"
        "Evidence quotes:\n"
        f"{json.dumps(quotes, ensure_ascii=True)}\n\n"
        "Rules:\n"
        "- Use only the provided evidence quotes; do not paraphrase or invent evidence.\n"
        "- Do NOT restate the requirement text as evidence.\n\n"
        "- All strings must be single-line; replace any newlines with spaces.\n\n"
        "Task: Assign a score 0-3 and justify using the evidence. "
        "Also assess whether the disclosure appears SUBSTANTIVE (true=genuine detail, specific methods, "
        "concrete results) or PERFORMATIVE (false=vague, boilerplate, no specifics).\n\n"
        "Return JSON with keys: requirement_id, score (0-3), justification, evidence (list of quotes), "
        "confidence (0-1), substantive (boolean), substantive_reasoning (brief explanation)."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _paragraph_spans(text: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    start = 0
    for match in _PARA_SPLIT_RE.finditer(text):
        end = match.start()
        if text[start:end].strip():
            spans.append((start, end))
        start = match.end()
    if text[start:].strip():
        spans.append((start, len(text)))
    return spans


def _coerce_quote_span(span: QuoteSpan, text: str) -> Tuple[str, int, int] | None:
    if not span.quote:
        return None
    if 0 <= span.start < span.end <= len(text) and text[span.start:span.end] == span.quote:
        return (span.quote, span.start, span.end)
    idx = text.find(span.quote)
    if idx == -1:
        return None
    return (span.quote, idx, idx + len(span.quote))


def _expand_quote_spans(text: str, spans: List[QuoteSpan], before: int = 2, after: int = 2) -> List[str]:
    para_spans = _paragraph_spans(text)
    expanded: List[str] = []
    for span in spans:
        coerced = _coerce_quote_span(span, text)
        if coerced is None:
            continue
        _, start, end = coerced
        if not para_spans:
            expanded.append(text[start:end].strip())
            continue
        para_index = next(
            (i for i, (s, e) in enumerate(para_spans) if start >= s and start < e),
            None,
        )
        if para_index is None:
            expanded.append(text[start:end].strip())
            continue
        start_idx = max(0, para_index - before)
        end_idx = min(len(para_spans) - 1, para_index + after)
        span_start = para_spans[start_idx][0]
        span_end = para_spans[end_idx][1]
        expanded.append(text[span_start:span_end].strip())
    return list(dict.fromkeys([item for item in expanded if item]))


async def _extract_claims_for_chunk(
    requirement: Requirement,
    chunk_text: str,
    cache: FileCache,
    semaphore: asyncio.Semaphore,
) -> ClaimExtraction:
    chunk_hash = _hash_key(chunk_text)
    cache_key = _hash_key(
        f"{STAGE_A_MODEL}:{STAGE_A_PROMPT_VERSION}:{requirement.id}:{chunk_hash}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return ClaimExtraction(**cached)

    async with semaphore:
        payload = await _call_llm_json(
            STAGE_A_MODEL,
            _stage_a_prompt(requirement, chunk_text),
        )

    extraction = ClaimExtraction(**payload)
    if extraction.quote_spans:
        extraction.quotes = _expand_quote_spans(chunk_text, extraction.quote_spans, before=2, after=2)
    cache.set(cache_key, extraction.model_dump())
    return extraction


async def _score_requirement(
    requirement: Requirement,
    claims: List[str],
    quotes: List[str],
    cache: FileCache,
    semaphore: asyncio.Semaphore,
) -> RequirementScore:
    # No evidence = score 0 (prevent guideline leakage)
    if not quotes or not claims:
        return RequirementScore(
            requirement_id=requirement.id,
            score=ScoreLevel.ABSENT,
            justification="No supporting evidence found in model card.",
            evidence=[],
            confidence=1.0,
            substantive=False,
            substantive_reasoning="Absence of evidence.",
        )

    claims_hash = _hash_key(json.dumps({"claims": claims, "quotes": quotes}, ensure_ascii=True))
    cache_key = _hash_key(
        f"{STAGE_B_MODEL}:{STAGE_B_PROMPT_VERSION}:{requirement.id}:{claims_hash}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return RequirementScore(**cached)

    async with semaphore:
        payload = await _call_llm_json(
            STAGE_B_MODEL,
            _stage_b_prompt(requirement, claims, quotes),
        )

    payload["requirement_id"] = requirement.id
    payload["score"] = ScoreLevel(int(payload["score"]))
    score = RequirementScore(**payload)
    cache.set(cache_key, score.model_dump())
    return score


def _aggregate_claims(extractions: Iterable[ClaimExtraction]) -> Tuple[List[str], List[str]]:
    claims: List[str] = []
    quotes: List[str] = []
    for extraction in extractions:
        if not extraction.relevant:
            continue
        claims.extend(extraction.claims)
        quotes.extend(extraction.quotes)
    dedup_claims = list(dict.fromkeys([c.strip() for c in claims if c.strip()]))
    dedup_quotes = list(dict.fromkeys([q.strip() for q in quotes if q.strip()]))
    return dedup_claims, dedup_quotes


def _compute_framework_percentage(scores: List[RequirementScore], requirement_ids: List[str]) -> float:
    if not requirement_ids:
        return 0.0
    score_map = {score.requirement_id: score.score for score in scores}
    total = sum(int(score_map.get(rid, 0)) for rid in requirement_ids)
    return round(100 * total / (3 * len(requirement_ids)), 2)


async def run_pipeline(
    model_name: str,
    model_card_path: Path,
    requirements: List[Requirement],
    model_card_url: str | None = None,
) -> ModelReport:
    cache = FileCache(CACHE_DIR)
    text = read_model_card(model_card_path)
    chunks = chunk_text(text, CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS)

    stage_a_sem = asyncio.Semaphore(STAGE_A_CONCURRENCY)
    stage_b_sem = asyncio.Semaphore(STAGE_B_CONCURRENCY)

    async def _process_requirement(req: Requirement) -> RequirementScore:
        extraction_tasks = [
            _extract_claims_for_chunk(req, chunk, cache, stage_a_sem) for chunk in chunks
        ]
        extractions = await asyncio.gather(*extraction_tasks)
        claims, quotes = _aggregate_claims(extractions)
        return await _score_requirement(req, claims, quotes, cache, stage_b_sem)

    scores = await tqdm_asyncio.gather(
        *[_process_requirement(req) for req in requirements],
        desc=f"  {model_name}",
    )

    cop_ids = [r.id for r in requirements if r.framework == "EU Code of Practice"]
    stream_ids = [r.id for r in requirements if r.framework == "STREAM"]
    lab_ids = [r.id for r in requirements if r.framework == "Lab Safety Commitments"]

    cop_pct = _compute_framework_percentage(scores, cop_ids)
    stream_pct = _compute_framework_percentage(scores, stream_ids)
    lab_pct = _compute_framework_percentage(scores, lab_ids)
    overall_pct = _compute_framework_percentage(scores, [r.id for r in requirements])

    return ModelReport(
        model_name=model_name,
        model_card_source=str(model_card_path),
        model_card_url=model_card_url,
        scores=list(scores),
        cop_percentage=cop_pct,
        stream_percentage=stream_pct,
        lab_safety_percentage=lab_pct,
        overall_percentage=overall_pct,
    )
