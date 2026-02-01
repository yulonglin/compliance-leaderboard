import json
from pathlib import Path
from typing import Any, Optional


class FileCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._path(key)
        if path.exists():
            return json.loads(path.read_text())
        return None

    def set(self, key: str, value: Any) -> None:
        self._path(key).write_text(json.dumps(value, ensure_ascii=True))
