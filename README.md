# Natural Language BI Query Engine

Full-stack demo: plain-English questions → **Claude** generates **SQLite** `SELECT` queries against a **retail sales** dataset; **FastAPI** runs them and returns results; **React** + **ECharts** charts the answer.

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Anthropic API key](https://console.anthropic.com/)

## Setup

1. Clone or open this repo and create a virtual environment (recommended).

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY`.

4. Build the SQLite database and sample CSV:

   ```bash
   python load_data.py
   ```

5. (Optional) Regenerate `test_cases.json` after changing the dataset:

   ```bash
   python scripts/generate_test_cases.py
   ```

## Run

The backend defaults to **port 8081** so it is less likely to clash with other tools or Windows reserved ranges (port 8000 often triggers `WinError 10013` on some PCs).

**Terminal 1 — backend** (from repo root):

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8081
```

**Terminal 2 — frontend**:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://127.0.0.1:5173`). The dev server proxies `/query` to `http://127.0.0.1:8081`.

### Windows PowerShell (5.x)

`&&` is not valid in older PowerShell. Run separate lines, or chain with `;`:

```powershell
cd frontend; npm install; npm run dev
```

### If you still see `WinError 10013`

Something else may be bound to that port, or Windows may exclude it. Pick any free port, for example **8765**:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

Then point the frontend proxy at the same port: in `frontend/vite.config.js`, set both proxy `target` values to `http://127.0.0.1:8765`, restart `npm run dev`, and run tests with:

```bash
set BASE_URL=http://127.0.0.1:8765
python test_harness.py
```

(On PowerShell use `$env:BASE_URL = "http://127.0.0.1:8765"` instead of `set`.)

## Prompt test harness

With the backend running:

```bash
python test_harness.py
```

Uses `test_cases.json` (61 cases by default). Set `BASE_URL` if the API is not on `http://127.0.0.1:8081`.

## Project layout

- `backend/` — FastAPI app, prompt builder, safe SQL execution
- `frontend/` — Vite + React + Tailwind + ECharts
- `load_data.py` — synthetic retail data → `retail.db` + `sample_sales.csv`
- `test_harness.py` / `test_cases.json` — benchmark harness
- `scripts/generate_test_cases.py` — rebuilds `test_cases.json` from `retail.db` counts

## Model

Configured for **`claude-sonnet-4-20250514`** (see `backend/main.py`).
