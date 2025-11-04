from __future__ import annotations
from typing import Dict, List, Set, Tuple
import os
from .storage import load_coverage_json

def build_maps(state_dir: str, project_root: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build:
      file_to_tests: file -> [pytest nodeids]
      test_to_files: pytest nodeid -> [files]

    Robust across coverage.py JSON variants:
    - contexts at file level
    - contexts nested under functions/classes
    - list or dict forms
    - Windows/Unix paths
    """
    data = load_coverage_json(state_dir)
    files = data.get("files", {})

    file_to_tests: Dict[str, Set[str]] = {}
    test_to_files: Dict[str, Set[str]] = {}

    for fpath, fdata in files.items():
        rel = _relpath_norm(fpath, project_root)

        # Gather ALL context names: file-level, functions, classes
        ctx_names: Set[str] = set()

        # 1) file-level contexts
        _collect_context_names(fdata.get("contexts"), ctx_names)

        # 2) function-level contexts
        for fn in (fdata.get("functions") or {}).values():
            _collect_context_names(fn.get("contexts"), ctx_names)

        # 3) class-level contexts
        for cl in (fdata.get("classes") or {}).values():
            _collect_context_names(cl.get("contexts"), ctx_names)

        # Map contexts -> pytest nodeids
        for ctx_name in ctx_names:
            nodeid = _extract_nodeid(ctx_name)
            if not nodeid:
                continue
            file_to_tests.setdefault(rel, set()).add(nodeid)
            test_to_files.setdefault(nodeid, set()).add(rel)

    return (
        {k: sorted(v) for k, v in file_to_tests.items()},
        {k: sorted(v) for k, v in test_to_files.items()},
    )

def _collect_context_names(ctx, out: Set[str]) -> None:
    """Accept dict({ctx: ...}) or list([ctx, ...]) and add context names to out."""
    if not ctx:
        return
    if isinstance(ctx, dict):
        out.update(ctx.keys())
    elif isinstance(ctx, list):
        out.update([str(x) for x in ctx])

def _extract_nodeid(ctx_name: str) -> str | None:
    """
    Accepts:
      - "test_function: tests/test_x.py::test_y"
      - "tests/test_x.py::test_y"
      - Windows paths are fine.
    """
    tail = ctx_name.split(":", 1)[-1].strip()
    return tail if "::" in tail else None

def _relpath_norm(path: str, root: str) -> str:
    try:
        rel = os.path.relpath(path, root)
    except Exception:
        rel = path
    return rel.replace("\\", "/")
