import httpx
from pathlib import Path
import pymupdf4llm
import tempfile
import os

# Disable SOCKS proxy auto-detection
os.environ["HTTPX_TRUST_ENV"] = "0"

url = "https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf"
output_dir = Path("data/model_cards")

print(f"Downloading {url}...")
resp = httpx.get(url, follow_redirects=True, timeout=60, verify=False, trust_env=False)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as handle:
        handle.write(resp.content)
        tmp_path = handle.name

    print(f"Converting to markdown...")
    markdown = pymupdf4llm.to_markdown(tmp_path)
    out_path = output_dir / "gemini-3-pro.md"
    out_path.write_text(markdown)
    print(f"Saved {out_path} ({len(markdown)} chars)")
else:
    print(f"ERROR: {resp.status_code} - {resp.text[:200]}")
