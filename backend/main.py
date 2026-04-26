import os
import re
from datetime import date

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.database import DB_PATH, execute_query
from backend.prompt import build_system_prompt

load_dotenv()

MODEL = "claude-sonnet-4-20250514"

app = FastAPI(title="NL BI Query Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


def _strip_sql_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _is_numeric(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _column_suggests_date(name: str) -> bool:
    n = name.lower()
    return "date" in n or n.endswith("_at")


def _cell_looks_like_date(val) -> bool:
    if val is None:
        return False
    s = str(val)
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}", s))


def _infer_column_kinds(columns: list[str], sample_row: list | None) -> list[str]:
    kinds = []
    for i, col in enumerate(columns):
        val = sample_row[i] if sample_row and i < len(sample_row) else None
        if _column_suggests_date(col) and _cell_looks_like_date(val):
            kinds.append("date")
        elif _is_numeric(val):
            kinds.append("numeric")
        else:
            kinds.append("category")
    return kinds


def infer_chart_type(columns: list[str], rows: list[list]) -> str:
    if not columns:
        return "table"
    sample = rows[0] if rows else None
    kinds = _infer_column_kinds(columns, sample)

    numeric_idxs = [i for i, k in enumerate(kinds) if k == "numeric"]
    date_idxs = [i for i, k in enumerate(kinds) if k == "date"]
    cat_idxs = [i for i, k in enumerate(kinds) if k == "category"]

    if len(columns) == 1 and len(rows) == 1 and numeric_idxs == [0]:
        return "kpi"

    if len(numeric_idxs) >= 2 and (cat_idxs or date_idxs):
        return "bar"

    if len(columns) == 2 and len(numeric_idxs) == 1 and len(date_idxs) == 1:
        return "line"

    if len(columns) == 2 and len(numeric_idxs) == 1 and len(cat_idxs) == 1:
        return "bar"

    if len(numeric_idxs) == 1 and len(columns) == 2 and len(date_idxs) == 0:
        other = [i for i in range(len(columns)) if i not in numeric_idxs]
        if len(other) == 1 and kinds[other[0]] == "category":
            return "bar"

    if len(numeric_idxs) >= 2:
        return "bar"

    return "table"


def _call_claude_sql(question: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not configured")

    client = Anthropic(api_key=api_key)
    system = build_system_prompt(date.today())
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    if not message.content or message.content[0].type != "text":
        raise HTTPException(status_code=502, detail="Unexpected response from Claude")
    return _strip_sql_fences(message.content[0].text)


@app.get("/health")
def health():
    return {"ok": True, "db_exists": DB_PATH.exists()}


@app.post("/query")
def run_query(body: QueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="question is required")

    try:
        sql = _call_claude_sql(body.question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude error: {e!s}") from e

    try:
        columns, rows = execute_query(sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {e!s}") from e

    chart_type = infer_chart_type(columns, rows)
    return {
        "sql": sql,
        "results": rows,
        "columns": columns,
        "chart_type": chart_type,
    }
