
import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_path: str = os.getenv("PROJECT_PATH", "examples/payments")
    state_dir: str = os.getenv("STATE_DIR", "state")
    report_dir: str = os.getenv("REPORT_DIR", "web/data")
    budget_tests: int = int(os.getenv("BUDGET_TESTS", "25"))
    budget_time_seconds: int = int(os.getenv("BUDGET_TIME_SECONDS", "120"))
    base_ref: str = os.getenv("BASE_BRANCH", "HEAD~1")
    head_ref: str = os.getenv("HEAD_REF", "HEAD")
    pytest_opts: str = os.getenv("PYTEST_OPTS", "")

    # Agent weights
    weight_affected: float = float(os.getenv("WEIGHT_AFFECTED", "1.0"))
    weight_fail_rate: float = float(os.getenv("WEIGHT_FAIL_RATE", "0.5"))
    weight_flaky_rate: float = float(os.getenv("WEIGHT_FLAKY_RATE", "0.2"))
    weight_runtime: float = float(os.getenv("WEIGHT_RUNTIME", "0.1"))

settings = Settings()
