
from __future__ import annotations
import os, json, time, pathlib

STATE_DIR = os.environ.get("STATE_DIR", "state")
pathlib.Path(STATE_DIR).mkdir(parents=True, exist_ok=True)

RUN = {
    "tests": {},
    "started_at": time.time(),
}

def pytest_runtest_logreport(report):
    if report.when != "call":
        return
    node = report.nodeid
    entry = RUN["tests"].setdefault(node, {"outcome": None, "duration": 0.0})
    entry["outcome"] = report.outcome
    entry["duration"] = getattr(report, "duration", 0.0)

def pytest_sessionfinish(session, exitstatus):
    RUN["exitstatus"] = exitstatus
    RUN["finished_at"] = time.time()
    out = os.path.join(STATE_DIR, "last_pytest_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(RUN, f, indent=2)
