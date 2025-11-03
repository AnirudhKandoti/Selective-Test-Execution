
from __future__ import annotations
import os, json, time
from typing import Dict, Any
from .storage import ensure_dir

def write_report(state_dir: str, report_dir: str, selection: Dict[str, Any] | None = None, explanations: Dict[str, Any] | None = None) -> str:
    ensure_dir(report_dir)
    data = {
        "generated_at": int(time.time()),
        "selection": selection or {},
        "explanations": explanations or {},
        "history": json.loads(open(os.path.join(state_dir, "history.json"), "r", encoding="utf-8").read()) if os.path.exists(os.path.join(state_dir, "history.json")) else {}
    }
    out = os.path.join(report_dir, "latest.json")
    open(out, "w", encoding="utf-8").write(json.dumps(data, indent=2))
    return out
