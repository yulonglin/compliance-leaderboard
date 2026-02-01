from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def add_project_root() -> None:
    paths_path = Path(__file__).resolve().parent.parent / "src" / "utils" / "paths.py"
    spec = spec_from_file_location("paths", paths_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load paths helper")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.add_project_root()
