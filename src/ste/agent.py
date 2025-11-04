
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set
from .storage import History, TestStats
from .config import settings
import os

@dataclass
class Weights:
    affected: float = settings.weight_affected
    fail_rate: float = settings.weight_fail_rate
    flaky_rate: float = settings.weight_flaky_rate
    runtime: float = settings.weight_runtime

def _normalize_runtime(stats: Dict[str, TestStats]) -> Dict[str, float]:
    times = [s.avg_duration for s in stats.values() if s.avg_duration > 0]
    if not times:
        return {k: 0.0 for k in stats.keys()}
    mn, mx = min(times), max(times)
    span = max(mx - mn, 1e-6)
    return {k: (s.avg_duration - mn) / span if s.avg_duration > 0 else 0.0 for k, s in stats.items()}



def _affected_tests(h: History, changed_files: List[str]) -> Set[str]:
    def norm(p: str) -> str:
        return p.replace("\\", "/")

    affected: Set[str] = set()

    changed_norm = [norm(f) for f in changed_files]
    changed_basenames = {os.path.basename(f) for f in changed_norm}

    cov_keys_norm = {norm(k): k for k in h.coverage_map.keys()}
    for f in changed_norm:
        if f in cov_keys_norm:
            affected.update(h.coverage_map[cov_keys_norm[f]])
        for k_norm, k_raw in cov_keys_norm.items():
            if k_norm == f or k_norm.endswith("/" + f) or os.path.basename(k_norm) in changed_basenames:
                affected.update(h.coverage_map[k_raw])

    for nodeid, files in h.test_to_files.items():
        for file_path in files:
            kn = norm(file_path)
            if kn in changed_norm or any(kn.endswith("/" + c) for c in changed_norm) or os.path.basename(kn) in changed_basenames:
                affected.add(nodeid)
                break

    return affected

def rank_with_explanations(h: History, changed_files: List[str], budget_tests: int, budget_seconds: int) -> Tuple[List[str], Dict[str, Dict]]:
    all_tests = list(h.tests.keys())
    if not all_tests:
        return [], {}

    affected = _affected_tests(h, changed_files)
    w = Weights()
    norm_rt = _normalize_runtime(h.tests)

    expl: Dict[str, Dict] = {}
    scores: Dict[str, float] = {}
    for t in all_tests:
        s = h.tests.get(t, TestStats(nodeid=t))
        contrib = {
            "affected": 1.0 if t in affected else 0.0,
            "fail_rate": s.fail_rate,
            "flaky_rate": s.flaky_rate,
            "runtime_norm": norm_rt.get(t, 0.0),
        }
        score = (
            w.affected * contrib["affected"] +
            w.fail_rate * contrib["fail_rate"] +
            w.flaky_rate * contrib["flaky_rate"] +
            w.runtime * contrib["runtime_norm"]
        )
        scores[t] = score
        expl[t] = {
            "affected": bool(t in affected),
            "fail_rate": round(contrib["fail_rate"], 3),
            "flaky_rate": round(contrib["flaky_rate"], 3),
            "runtime_norm": round(contrib["runtime_norm"], 3),
            "weights": {"affected": w.affected, "fail_rate": w.fail_rate, "flaky_rate": w.flaky_rate, "runtime": w.runtime},
            "score": round(score, 4),
            "included": False,
            "reason": "",
        }

    ordered = sorted(all_tests, key=lambda t: (t not in affected, -scores[t]))

    selected: List[str] = []
    elapsed = 0.0
    for t in ordered:
        if budget_tests and len(selected) >= budget_tests:
            expl[t]["included"] = False
            expl[t]["reason"] = "Excluded due to test-count budget."
            continue
        if budget_seconds:
            dur = h.tests.get(t).avg_duration if t in h.tests else 0.0
            if elapsed + dur > budget_seconds and len(selected) > 0:
                expl[t]["included"] = False
                expl[t]["reason"] = "Excluded due to time budget."
                continue
            elapsed += dur
        selected.append(t)
        expl[t]["included"] = True
        if t in affected:
            expl[t]["reason"] = "Included: directly affected by changed files."
        else:
            expl[t]["reason"] = "Included: high risk score within remaining budget."

    for t in all_tests:
        if not expl[t]["included"] and not expl[t]["reason"]:
            if t in affected:
                expl[t]["reason"] = "Would be included (affected) but excluded by budgets."
            else:
                expl[t]["reason"] = "Deprioritized: not affected and lower score than budget cutoff."

    return selected, expl
