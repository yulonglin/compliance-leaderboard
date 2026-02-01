from pathlib import Path
from typing import List

import tiktoken


def read_model_card(path: Path) -> str:
    return path.read_text()


def chunk_text(text: str, max_tokens: int, overlap_tokens: int) -> List[str]:
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    chunks: List[str] = []

    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = encoder.decode(tokens[start:end])
        chunks.append(chunk)
        if end == len(tokens):
            break
        start = max(0, end - overlap_tokens)
    return chunks


def list_model_cards(model_card_dir: Path) -> List[Path]:
    return sorted(model_card_dir.glob("*.md"))
