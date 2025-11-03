
import subprocess
from typing import List

def changed_files(base: str, head: str) -> List[str]:
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", f"{base}..{head}"], text=True)
        files = [l.strip() for l in out.splitlines() if l.strip()]
        return files
    except Exception:
        return []
