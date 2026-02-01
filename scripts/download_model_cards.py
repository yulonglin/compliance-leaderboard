"""Download and convert model cards from PDF to markdown."""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
import pymupdf4llm

from bootstrap import add_project_root

INDEX_PAGES = {
    "anthropic": "https://www.anthropic.com/system-cards/",
    "deepmind": "https://deepmind.google/models/model-cards/",
    "openai": "https://openai.com/news/safety-alignment/?display=list",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "model-card"


def _name_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).stem
    return _slugify(name)


def _relativize_image_paths(markdown: str, images_dir: Path) -> str:
    if not images_dir.is_absolute():
        return markdown
    abs_path = images_dir.as_posix()
    if not abs_path.endswith("/"):
        abs_path += "/"
    return markdown.replace(abs_path, f"{images_dir.name}/")


def download_and_convert(
    name: str,
    url: str,
    output_dir: Path,
    with_images: bool,
    force: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{name}.md"
    images_dir = output_dir / f"{name}_images"
    if out_path.exists() and not force:
        if with_images:
            has_images = images_dir.exists() and any(images_dir.iterdir())
            if has_images:
                print(f"  Skipping {name} (already exists with images)")
                return
        else:
            print(f"  Skipping {name} (already exists)")
            return

    print(f"  Downloading {name} from {url}...")
    resp = httpx.get(url, follow_redirects=True, timeout=60)
    resp.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as handle:
        handle.write(resp.content)
        tmp_path = handle.name

    print(f"  Converting {name} to markdown...")
    if with_images:
        images_dir.mkdir(parents=True, exist_ok=True)
        markdown = pymupdf4llm.to_markdown(
            tmp_path,
            write_images=True,
            image_path=str(images_dir),
        )
        markdown = _relativize_image_paths(markdown, images_dir)
    else:
        markdown = pymupdf4llm.to_markdown(tmp_path)
    out_path.write_text(markdown)
    print(f"  Saved {name} ({len(markdown)} chars)")


def _fetch_index_links(url: str) -> list[str]:
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    parser = LinkParser()
    parser.feed(response.text)
    links = []
    for link in parser.links:
        if link.startswith("mailto:"):
            continue
        links.append(urljoin(url, link))
    return links


def _select_pdf_links(links: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    pdfs = []
    for link in links:
        if not link.lower().endswith(".pdf"):
            continue
        if link in seen:
            continue
        seen.add(link)
        pdfs.append(link)
    return pdfs


def _report_non_pdf_links(links: Iterable[str]) -> None:
    keywords = ("system-card", "model-card", "safety", "alignment", "card")
    candidates = []
    for link in links:
        lowered = link.lower()
        if any(keyword in lowered for keyword in keywords):
            candidates.append(link)
    if candidates:
        print("  Non-PDF links of interest (manual follow-up may be needed):")
        for link in sorted(set(candidates)):
            print(f"   - {link}")


def _write_sources(output_dir: Path, sources: dict[str, str]) -> None:
    sources_path = output_dir / "sources.json"
    sources_path.write_text(json.dumps(sources, indent=2, ensure_ascii=True))
    print(f"  Updated sources index: {sources_path}")


def _download_from_index(
    output_dir: Path,
    limit: int | None,
    with_images: bool,
    sources: dict[str, str],
) -> None:
    for name, url in INDEX_PAGES.items():
        print(f"\nScanning index: {name} -> {url}")
        try:
            links = _fetch_index_links(url)
        except Exception as exc:
            print(f"  FAILED to fetch index: {exc}")
            continue

        pdf_links = _select_pdf_links(links)
        if not pdf_links:
            print("  No PDF links found on index page.")
            _report_non_pdf_links(links)
            continue

        if limit is not None:
            pdf_links = pdf_links[:limit]

        for pdf_url in pdf_links:
            card_name = _name_from_url(pdf_url)
            try:
                download_and_convert(card_name, pdf_url, output_dir, with_images)
                sources[card_name] = pdf_url
            except Exception as exc:
                print(f"  FAILED {card_name}: {exc}")
                print(
                    "  Please manually download from "
                    f"{pdf_url} and save markdown to {output_dir / f'{card_name}.md'}"
                )


if __name__ == "__main__":
    add_project_root()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-index",
        action="store_true",
        help="Scan index pages for PDF links and download those too.",
    )
    parser.add_argument(
        "--index-limit",
        type=int,
        default=None,
        help="Limit PDF downloads per index page.",
    )
    parser.add_argument(
        "--with-images",
        action="store_true",
        help="Extract images alongside markdown and rewrite image paths to relative.",
    )
    args = parser.parse_args()

    MODEL_CARDS = {
        "claude-opus-4-5": "https://assets.anthropic.com/m/64823ba7485345a7/Claude-Opus-4-5-System-Card.pdf",
        "gpt-4o": "https://cdn.openai.com/gpt-4o-system-card.pdf",
        "gpt-5-2": "https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf",
        "gemini-2-5-pro": "https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf",
        "llama-3-1-405b": "https://arxiv.org/pdf/2407.21783",
        "deepseek-r1": "https://arxiv.org/pdf/2501.12948",
    }

    EXPECTED_SNIPPETS = {
        "claude-opus-4-5": "Claude Opus 4.5",
        "gpt-4o": "GPT-4o",
        "gpt-5-2": "GPT-5.2",
        "gemini-2-5-pro": "Gemini 2.5",
        "llama-3-1-405b": "Llama 3.1",
        "deepseek-r1": "DeepSeek-R1",
    }

    output_dir = Path("data/model_cards")
    sources: dict[str, str] = dict(MODEL_CARDS)

    for name, url in MODEL_CARDS.items():
        try:
            expected = EXPECTED_SNIPPETS.get(name)
            force = False
            if expected:
                out_path = output_dir / f"{name}.md"
                if out_path.exists():
                    content = out_path.read_text()
                    if expected.lower() not in content.lower():
                        print(
                            f"  Warning: {name}.md does not mention '{expected}', re-downloading."
                        )
                        force = True
            download_and_convert(name, url, output_dir, args.with_images, force=force)
        except Exception as exc:
            print(f"  FAILED {name}: {exc}")
            print(
                "  Please manually download from "
                f"{url} and save markdown to {output_dir / f'{name}.md'}"
            )

    if args.from_index:
        _download_from_index(output_dir, args.index_limit, args.with_images, sources)

    _write_sources(output_dir, sources)
