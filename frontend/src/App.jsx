import { useCallback, useState } from "react";
import ChartPanel from "./components/ChartPanel.jsx";
import QueryInput from "./components/QueryInput.jsx";
import ResultsTable from "./components/ResultsTable.jsx";
import SqlDisplay from "./components/SqlDisplay.jsx";

const initialState = {
  sql: "",
  columns: [],
  results: [],
  chart_type: "table",
};

export default function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(initialState);

  const runQuery = useCallback(async () => {
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    setError("");
    setData(initialState);
    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        const msg =
          typeof body.detail === "string"
            ? body.detail
            : Array.isArray(body.detail)
              ? body.detail.map((d) => d.msg || d).join("; ")
              : res.statusText;
        throw new Error(msg || "Request failed");
      }
      setData({
        sql: body.sql ?? "",
        columns: body.columns ?? [],
        results: body.results ?? [],
        chart_type: body.chart_type ?? "table",
      });
    } catch (e) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [question]);

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto max-w-5xl px-4 py-6">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Natural Language BI Query Engine
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Ask questions in plain English. SQL is generated with Claude and run
            on the retail <code className="rounded bg-slate-100 px-1">sales</code>{" "}
            dataset.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <QueryInput
            value={question}
            onChange={setQuestion}
            onSubmit={runQuery}
            disabled={loading}
          />
          {loading && (
            <div className="mt-6 flex items-center gap-3 text-sm text-slate-600">
              <span
                className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent"
                aria-hidden
              />
              Generating SQL and running query…
            </div>
          )}
          {error && (
            <div
              className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
              role="alert"
            >
              {error}
            </div>
          )}
        </section>

        {(data.sql || data.columns.length > 0) && (
          <section className="space-y-6">
            <SqlDisplay sql={data.sql} />
            <div>
              <h2 className="mb-2 text-sm font-medium text-slate-700">
                Visualization
              </h2>
              <ChartPanel
                chartType={data.chart_type}
                columns={data.columns}
                rows={data.results}
              />
            </div>
            <ResultsTable columns={data.columns} rows={data.results} />
          </section>
        )}
      </main>
    </div>
  );
}
