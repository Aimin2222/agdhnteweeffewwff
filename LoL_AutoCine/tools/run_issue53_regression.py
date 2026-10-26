"""Run each test module in a fresh interpreter so native crashes are isolated."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


APP = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--temp-root", type=Path, help="Short writable path avoids Windows MAX_PATH in pytest fixtures")
    parser.add_argument("--app", type=Path, help="Read-only baseline checkout to compare against")
    parser.add_argument("--only", nargs="*", help="Run only these test module file names")
    args = parser.parse_args()
    app = args.app.resolve() if args.app else APP
    output = args.output.resolve()
    logs = output / "logs"
    temp = args.temp_root.resolve() if args.temp_root else output / "temp"
    logs.mkdir(parents=True, exist_ok=True)
    temp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMP=str(temp), TEMP=str(temp), PYTHONUTF8="1",
               PYTHONDONTWRITEBYTECODE="1", PYTEST_ADDOPTS="-p no:cacheprovider")
    results = []
    for path in sorted((app / "tests").glob("test_*.py")):
        if args.only is not None and path.name not in args.only:
            continue
        start = time.monotonic()
        status = "FAIL"
        try:
            run = subprocess.run([sys.executable, "-m", "pytest", "-q", str(path), "--tb=line"],
                                 cwd=app, env=env, capture_output=True, text=True,
                                 errors="replace", timeout=args.timeout, check=False)
            log = run.stdout + run.stderr
            if run.returncode == 0:
                status = "PASS"
            elif run.returncode == 5 and "no tests ran" in log:
                status = "NO_TESTS"
            elif run.returncode < 0 or run.returncode >= 0xC0000000:
                status = "CRASH"
            code = run.returncode
        except subprocess.TimeoutExpired as exc:
            status = "TIMEOUT"
            code = None
            log = f"Timed out after {args.timeout}s\n{exc.stdout or b''}\n{exc.stderr or b''}"
        match = re.findall(r"(\d+) passed", log)
        passed = int(match[-1]) if match else 0
        (logs / f"{path.stem}.txt").write_text(log, encoding="utf-8")
        item = dict(module=path.name, status=status, exit_code=code,
                    passed=passed, seconds=round(time.monotonic() - start, 2))
        results.append(item)
        (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{path.name}: {status}, {passed} passed, {item['seconds']}s", flush=True)
    totals = {state: sum(item["status"] == state for item in results)
              for state in ("PASS", "FAIL", "CRASH", "TIMEOUT", "NO_TESTS")}
    print(json.dumps({"modules": len(results), "passed_assertions": sum(x["passed"] for x in results),
                      "module_status": totals}, ensure_ascii=False), flush=True)
    if totals["FAIL"] or totals["CRASH"] or totals["TIMEOUT"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
