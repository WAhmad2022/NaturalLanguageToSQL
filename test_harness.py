"""
Run prompt/query accuracy checks against a live FastAPI server.
Usage (from project root):
  uvicorn backend.main:app --host 127.0.0.1 --port 8081
  python test_harness.py
Optional: set BASE_URL=http://127.0.0.1:8081
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "test_cases.json"
DEFAULT_BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8081").rstrip("/")


def post_query(base: str, question: str) -> dict:
    payload = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/query",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def sql_matches(sql: str, fragments: list[str]) -> tuple[bool, str]:
    low = sql.lower()
    missing = [f for f in fragments if f.lower() not in low]
    if missing:
        return False, f"missing substrings: {missing}"
    return True, ""


def main() -> int:
    base = DEFAULT_BASE
    if not CASES_PATH.exists():
        print(f"Missing {CASES_PATH}", file=sys.stderr)
        return 1
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    passed = 0
    failures: list[str] = []

    for i, case in enumerate(cases, 1):
        q = case["question"]
        frags = case["expected_sql_contains"]
        expected_rows = case["expected_row_count"]
        try:
            out = post_query(base, q)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            failures.append(f"[{i}] HTTP {e.code} for {q!r}\n{body}")
            continue
        except Exception as e:
            failures.append(f"[{i}] {q!r} -> request error: {e}")
            continue

        sql = out.get("sql") or ""
        rows = out.get("results") or []
        ok_frag, msg = sql_matches(sql, frags)
        ok_count = len(rows) == expected_rows
        if ok_frag and ok_count:
            passed += 1
        else:
            parts = []
            if not ok_frag:
                parts.append(msg)
            if not ok_count:
                parts.append(f"row count {len(rows)} != expected {expected_rows}")
            failures.append(
                f"[{i}] {q!r}\n  SQL: {sql}\n  " + "; ".join(parts)
            )

    total = len(cases)
    print(f"Results: {passed}/{total} passed")
    if failures:
        print("\nFailures:\n")
        for block in failures:
            print(block)
            print()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
