import json
from pathlib import Path
from typing import Dict, List

from .models import Requirement


def load_requirements(path: Path) -> List[Requirement]:
    data = json.loads(path.read_text())
    return [Requirement(**item) for item in data]


def group_requirements(requirements: List[Requirement]) -> Dict[str, List[Requirement]]:
    grouped: Dict[str, List[Requirement]] = {}
    for req in requirements:
        grouped.setdefault(req.framework, []).append(req)
    return grouped
