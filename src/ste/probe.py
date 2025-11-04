# src/ste/probe.py
from __future__ import annotations
import os, sys, subprocess, json, uuid
from typing import Dict, List, Set, Tuple

def _norm_rel(path: str, root: str) -> str:
    try:
        rel = os.path.relpath(path, root)
    except Exception:
        rel = path
    return rel.replace("\\", "/")

def _list_nodeids(project_path: str, env) -> List[str]:
    """
    Collect pytest nodeids (path::test_name) reliably.
    """
    cmd = [sys.executable, "-m", "pytest", "-q", "--collect-only", project_path]
    out = subprocess.check_output(cmd, env=env, text=True, stderr=subprocess.STDOUT)
    nodeids: List[str] = []
    for line in out.splitlines():
        s = line.strip()
        # Heuristic: nodeids contain '::' and end with a test function name
        if "::" in s and not s.startswith(("[", "=", "collected", "Platform", "plugins:", "ERROR", "WARNING")):
            nodeids.append(s)
    return nodeids

def _measure_files_for_test(project_path: str, nodeid: str, state_dir: str, env) -> Set[str]:
    """
    Run a SINGLE test under coverage and read the JSON report to know which files
    that test executed. This does NOT depend on contexts.
    """
    os.makedirs(state_dir, exist_ok=True)
    json_path = os.path.join(state_dir, f"probe_{uuid.uuid4().hex}.json")
    cmd = [
        sys.executable, "-m", "pytest", "-q",
        "-p", "src.ste.pytest_plugin",
        f"--cov={project_path}", "--cov-branch",
        f"--cov-report=json:{json_path}",
        nodeid,
    ]
    subprocess.call(cmd, env=env)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set()

    files: Set[str] = set()
    for fpath in (data.get("files") or {}).keys():
        files.add(fpath)
    return files

def probe_maps(project_path: str, state_dir: str, project_root: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build coverage maps by running each test once and mapping the executed files.
    This is a fallback used when contexts are unavailable/empty.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    os.makedirs(state_dir, exist_ok=True)

    file_to_tests: Dict[str, Set[str]] = {}
    test_to_files: Dict[str, Set[str]] = {}

    nodeids = _list_nodeids(project_path, env)
    for nid in nodeids:
        files = _measure_files_for_test(project_path, nid, state_dir, env)
        for f in files:
            rel = _norm_rel(f, project_root)
            file_to_tests.setdefault(rel, set()).add(nid)
            test_to_files.setdefault(nid, set()).add(rel)

    return (
        {k: sorted(v) for k, v in file_to_tests.items()},
        {k: sorted(v) for k, v in test_to_files.items()},
    )
