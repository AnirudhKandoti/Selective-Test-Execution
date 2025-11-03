
from __future__ import annotations
import os, shlex, subprocess

def run_pytest_with_coverage(project_path: str, state_dir: str, pytest_opts: str = "") -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    cmd = f"coverage run -m pytest -q -p src.ste.pytest_plugin {shlex.quote(project_path)}"
    if pytest_opts:
        cmd += " " + pytest_opts
    print(f"[run] {cmd}")
    code = subprocess.call(cmd, shell=True, env=env)
    subprocess.call("coverage json -o state/coverage.json --pretty-print --show-contexts", shell=True, env=env)
    return code

def run_selected_tests(project_path: str, selected, pytest_opts: str = "") -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    if not selected:
        cmd = f"pytest -q -p src.ste.pytest_plugin {project_path}"
    else:
        nodeids = " ".join(shlex.quote(t) for t in selected)
        cmd = f"pytest -q -p src.ste.pytest_plugin {nodeids}"
    if pytest_opts:
        cmd += " " + pytest_opts
    print(f"[run] {cmd}")
    return subprocess.call(cmd, shell=True, env=env)
