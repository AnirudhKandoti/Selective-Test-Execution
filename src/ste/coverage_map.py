from __future__ import annotations
from typing import Dict, List, Set, Tuple, Any
import os, json
from .storage import load_coverage_json

def build_maps(state_dir: str, project_root: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build:
      file_to_tests: file -> [test nodeids]
      test_to_files: test nodeid -> [files]
    Works across Windows/Unix and both coverage.py JSON shapes:
      - contexts as a dict {ctx: {...}}
      - contexts as a list ["test_function: tests/..::test_..", ...]
    """
    data = load_coverage_json(state_dir)
    files = data.get("files", {})

    file_to_tests: Dict[str, Set[str]] = {}
    test_to_files: Dict[str, Set[str]] = {}

    for fpath, fdata in files.items():
        rel = _relpath_norm(fpath, project_root)  # normalized "a/b/c.py"
        ctxs = fdata.get("contexts", {})

        # contexts can be a dict or a list depending on coverage version/flags
        if isinstance(ctxs, dict):
            ctx_iter = ctxs.keys()
        elif isinstance(ctxs, list):
            ctx_iter = ctxs
        else:
            ctx_iter = []

        for ctx_name in ctx_iter:
            nodeid = _extract_nodeid(ctx_name)
            if not nodeid:
                continue
            file_to_tests.setdefault(rel, set()).add(nodeid)
            test_to_files.setdefault(nodeid, set()).add(rel)

    return (
        {k: sorted(v) for k, v in file_to_tests.items()},
        {k: sorted(v) for k, v in test_to_files.items()},
    )

def _extract_nodeid(ctx_name: str) -> str | None:
    """
    Accepts:
      - "test_function: tests/test_x.py::test_y"
      - "tests/test_x.py::test_y"
      - Windows paths inside contexts are fine.
    """
    # keep only the last colon-split piece to drop "test_function:" prefix if present
    tail = ctx_name.split(":", 1)[-1].strip()
    return tail if "::" in tail else None

def _relpath_norm(path: str, root: str) -> str:
    try:
        rel = os.path.relpath(path, root)
    except Exception:
        rel = path
    return rel.replace("\\", "/")  # normalize for cross-platform matching
