from __future__ import annotations
import os, sys, subprocess

def run_pytest_with_coverage(project_path: str, state_dir: str, pytest_opts: str = "") -> int:
    """
    Windows-safe:
    1) run pytest with pytest-cov and per-test contexts (--cov-context=test)
    2) export coverage JSON with contexts via coverage API -> state/coverage.json
    """
    os.makedirs(state_dir, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    # write coverage data into ./state/.coverage so we know where to read from
    env["COVERAGE_FILE"] = os.path.join(state_dir, ".coverage")

    # 1) run tests under coverage with per-test contexts
    cmd = [
        sys.executable, "-m", "pytest", "-q",
        "-p", "src.ste.pytest_plugin",
        f"--cov={project_path}", "--cov-branch", "--cov-context=test",
        project_path,
    ]
    if pytest_opts:
        cmd.extend(pytest_opts.split())
    print("[run]", " ".join(cmd))
    code = subprocess.call(cmd, env=env)

    # 2) export JSON *with contexts* via coverage API (no shell quoting issues)
    export_code = (
        "import os, coverage; "
        f"cov = coverage.Coverage(data_file=r'{os.path.join(state_dir, '.coverage')}'); "
        "cov.load(); "
        f"cov.json_report(outfile=r'{os.path.join(state_dir, 'coverage.json')}', show_contexts=True, pretty_print=True)"
    )
    print("[run] coverage API -> state/coverage.json")
    _ = subprocess.call([sys.executable, "-c", export_code], env=env)

    return code

def run_selected_tests(project_path: str, selected, pytest_opts: str = "") -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    if not selected:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "src.ste.pytest_plugin", project_path]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "src.ste.pytest_plugin", *selected]
    if pytest_opts:
        cmd.extend(pytest_opts.split())
    print("[run]", " ".join(cmd))
    return subprocess.call(cmd, env=env)
