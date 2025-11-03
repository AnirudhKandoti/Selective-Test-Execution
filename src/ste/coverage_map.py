
from __future__ import annotations
from typing import Dict, List, Set
import os
from .storage import load_coverage_json

def build_maps(state_dir: str, project_root: str) -> (Dict[str, List[str]], Dict[str, List[str]]):
    data = load_coverage_json(state_dir)
    files = data.get("files", {})
    file_to_tests: Dict[str, Set[str]] = {}
    test_to_files: Dict[str, Set[str]] = {}

    for fpath, fdata in files.items():
        rel = _relpath_safe(fpath, project_root)
        contexts = fdata.get("contexts", {})
        for ctx_name, ctx_data in contexts.items():
            nodeid = _extract_nodeid(ctx_name)
            if not nodeid:
                continue
            file_to_tests.setdefault(rel, set()).add(nodeid)
            test_to_files.setdefault(nodeid, set()).add(rel)

    return {k: sorted(list(v)) for k, v in file_to_tests.items()}, {k: sorted(list(v)) for k, v in test_to_files.items()}

def _extract_nodeid(ctx_name: str) -> str | None:
    if "::" in ctx_name:
        parts = ctx_name.split(":", 1)
        tail = parts[-1].strip()
        return tail if "::" in tail or tail.endswith(".py") else None
    return None

def _relpath_safe(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root)
    except Exception:
        return path
