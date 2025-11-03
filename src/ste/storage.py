
from __future__ import annotations
import os, json, time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

@dataclass
class TestStats:
    nodeid: str
    runs: int = 0
    fails: int = 0
    flaky: int = 0
    avg_duration: float = 0.0

    @property
    def fail_rate(self) -> float:
        return self.fails / self.runs if self.runs else 0.0

    @property
    def flaky_rate(self) -> float:
        return self.flaky / self.runs if self.runs else 0.0

@dataclass
class History:
    tests: Dict[str, TestStats]
    coverage_map: Dict[str, List[str]]  # file -> [nodeid]
    test_to_files: Dict[str, List[str]]
    runs: List[Dict[str, Any]]

def load_history(state_dir: str) -> History:
    path = os.path.join(state_dir, "history.json")
    if not os.path.exists(path):
        return History(tests={}, coverage_map={}, test_to_files={}, runs=[])
    data = json.loads(open(path, "r", encoding="utf-8").read())
    tests = {k: TestStats(**v) for k, v in data.get("tests", {}).items()}
    return History(
        tests=tests,
        coverage_map=data.get("coverage_map", {}),
        test_to_files=data.get("test_to_files", {}),
        runs=data.get("runs", []),
    )

def save_history(state_dir: str, h: History) -> None:
    ensure_dir(state_dir)
    data = {
        "tests": {k: asdict(v) for k, v in h.tests.items()},
        "coverage_map": h.coverage_map,
        "test_to_files": h.test_to_files,
        "runs": h.runs,
        "updated_at": int(time.time())
    }
    open(os.path.join(state_dir, "history.json"), "w", encoding="utf-8").write(json.dumps(data, indent=2))

def load_last_pytest_report(state_dir: str) -> Dict[str, Any]:
    p = os.path.join(state_dir, "last_pytest_report.json")
    if os.path.exists(p):
        return json.loads(open(p, "r", encoding="utf-8").read())
    return {}

def load_coverage_json(state_dir: str) -> Dict[str, Any]:
    p = os.path.join(state_dir, "coverage.json")
    if os.path.exists(p):
        return json.loads(open(p, "r", encoding="utf-8").read())
    return {}
