
import os, json, time
from pathlib import Path
from typing import Optional
import typer
from rich import print

from src.ste.config import settings
from src.ste.runner import run_pytest_with_coverage, run_selected_tests
from src.ste.storage import load_history, save_history, load_last_pytest_report, TestStats
from src.ste.coverage_map import build_maps
from src.ste.git_diff import changed_files
from src.ste.agent import rank_with_explanations
from src.ste.report import write_report

app = typer.Typer(help="Selective Test Execution (STE) CLI w/ Dev Assistant Agent")

@app.command()
def record_run(project: Optional[str] = typer.Option(None, "--project", help="Path to tests folder"),
               pytest_opts: Optional[str] = typer.Option(None, "--pytest-opts", help="Extra pytest opts")):
    cfg = settings
    if project: cfg.project_path = project
    if pytest_opts: cfg.pytest_opts = pytest_opts

    code = run_pytest_with_coverage(cfg.project_path, cfg.state_dir, cfg.pytest_opts)
    if code not in (0, 5):
        print(f"[yellow]pytest exit code: {code}[/yellow]")

    file_to_tests, test_to_files = build_maps(cfg.state_dir, os.getcwd())

    hist = load_history(cfg.state_dir)
    hist.coverage_map = file_to_tests
    hist.test_to_files = test_to_files

    rpt = load_last_pytest_report(cfg.state_dir)
    tests = rpt.get("tests", {})
    for nodeid, info in tests.items():
        st = hist.tests.get(nodeid)
        if st is None:
            st = TestStats(nodeid=nodeid, runs=0, fails=0, flaky=0, avg_duration=0.0)
            hist.tests[nodeid] = st
        st.runs += 1
        if info.get("outcome") == "failed":
            st.fails += 1
        if st.fails > 0 and st.runs - st.fails > 0:
            st.flaky = 1
        dur = float(info.get("duration", 0.0) or 0.0)
        st.avg_duration = st.avg_duration + (dur - st.avg_duration) / max(st.runs, 1)

    hist.runs.append({
        "time": int(time.time()),
        "project": cfg.project_path,
        "count": len(tests),
        "failed": sum(1 for t in tests.values() if t.get("outcome") == "failed")
    })

    save_history(cfg.state_dir, hist)
    write_report(cfg.state_dir, cfg.report_dir, selection=None, explanations=None)
    print("[green]Recorded run, updated coverage map and history.[/green]")

@app.command()
def select(project: Optional[str] = typer.Option(None, "--project"),
           base: Optional[str] = typer.Option(None, "--base"),
           head: Optional[str] = typer.Option(None, "--head"),
           budget_tests: Optional[int] = typer.Option(None, "--budget-tests"),
           budget_time_seconds: Optional[int] = typer.Option(None, "--budget-time-seconds")):
    cfg = settings
    if project: cfg.project_path = project
    if base: cfg.base_ref = base
    if head: cfg.head_ref = head
    if budget_tests is not None: cfg.budget_tests = budget_tests
    if budget_time_seconds is not None: cfg.budget_time_seconds = budget_time_seconds

    hist = load_history(cfg.state_dir)
    files = changed_files(cfg.base_ref, cfg.head_ref)

    selected, explanations = rank_with_explanations(hist, files, cfg.budget_tests, cfg.budget_time_seconds)

    sel = {
        "base": cfg.base_ref,
        "head": cfg.head_ref,
        "project": cfg.project_path,
        "changed_files": files,
        "selected": selected,
        "budget_tests": cfg.budget_tests,
        "budget_time_seconds": cfg.budget_time_seconds,
    }
    Path(cfg.state_dir).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(cfg.state_dir, "selection.json")).write_text(json.dumps(sel, indent=2), encoding="utf-8")
    write_report(cfg.state_dir, cfg.report_dir, selection=sel, explanations=explanations)

    print(f"[green]Selected {len(selected)} tests.[/green]")
    if selected:
        for t in selected[:10]:
            print("  -", t)
        if len(selected) > 10:
            print(f"  ... and {len(selected)-10} more")

@app.command()
def run_selected(project: Optional[str] = typer.Option(None, "--project"),
                 pytest_opts: Optional[str] = typer.Option(None, "--pytest-opts")):
    cfg = settings
    if project: cfg.project_path = project
    if pytest_opts: cfg.pytest_opts = pytest_opts

    sel_path = os.path.join(cfg.state_dir, "selection.json")
    if not os.path.exists(sel_path):
        print("[red]No selection.json found. Run `select` first.[/red]")
        raise typer.Exit(code=2)
    sel = json.loads(Path(sel_path).read_text(encoding="utf-8"))
    selected = sel.get("selected", [])
    code = run_selected_tests(cfg.project_path, selected, cfg.pytest_opts)
    raise typer.Exit(code=code)

@app.command()
def report():
    cfg = settings
    path = write_report(cfg.state_dir, cfg.report_dir, selection=None, explanations=None)
    print(f"[green]Wrote report to {path}[/green]")

if __name__ == "__main__":
    app()
