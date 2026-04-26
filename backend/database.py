import re
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "retail.db"


def _normalize_sql(sql: str) -> str:
    s = sql.strip()
    while s.endswith(";"):
        s = s[:-1].strip()
    return s


def _validate_select_only(sql: str) -> None:
    s = _normalize_sql(sql)
    if not s:
        raise ValueError("Empty SQL")
    lowered = s.lower()
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    if ";" in s:
        raise ValueError("Multiple statements are not allowed")
    for pattern in (
        r"\binsert\b",
        r"\bupdate\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\battach\b",
        r"\bpragma\b",
        r"\bcreate\b",
        r"\balter\b",
        r"\btruncate\b",
    ):
        if re.search(pattern, lowered):
            raise ValueError("Query contains disallowed operations")


def execute_query(sql: str) -> tuple[list[str], list[list]]:
    sql = _normalize_sql(sql)
    _validate_select_only(sql)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(sql)
        if cur.description is None:
            return [], []
        columns = [d[0] for d in cur.description]
        rows = [list(row) for row in cur.fetchall()]
        return columns, rows
    finally:
        conn.close()
