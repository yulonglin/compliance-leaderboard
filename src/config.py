from pathlib import Path

import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_CARD_DIR = DATA_DIR / "model_cards"
RUBRIC_PATH = DATA_DIR / "rubrics" / "requirements.json"
RESULTS_DIR = PROJECT_ROOT / "results"
CACHE_DIR = PROJECT_ROOT / ".cache" / "llm"
VALIDATION_DIR = PROJECT_ROOT / "validation"

STAGE_A_MODEL = os.getenv("STAGE_A_MODEL", "gemini/gemini-2.5-flash")
STAGE_B_MODEL = os.getenv(
    "STAGE_B_MODEL",
    "anthropic/claude-sonnet-4-5-20250514",
)
STAGE_A_PROMPT_VERSION = os.getenv("STAGE_A_PROMPT_VERSION", "2026-02-01-evidence-v2")
STAGE_B_PROMPT_VERSION = os.getenv("STAGE_B_PROMPT_VERSION", "2026-02-01-judge-v1")

STAGE_A_CONCURRENCY = 50
STAGE_B_CONCURRENCY = 10

CHUNK_MAX_TOKENS = 1200
CHUNK_OVERLAP_TOKENS = 100


def load_env() -> None:
    load_dotenv()
