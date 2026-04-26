import ReactECharts from "echarts-for-react";

function isNumeric(v) {
  return typeof v === "number" && Number.isFinite(v);
}

function colKinds(columns, sampleRow) {
  return columns.map((name, i) => {
    const v = sampleRow?.[i];
    const nl = name.toLowerCase();
    const dateish =
      nl.includes("date") &&
      v != null &&
      /^\d{4}-\d{2}-\d{2}/.test(String(v));
    if (dateish) return "date";
    if (isNumeric(v)) return "numeric";
    return "category";
  });
}

function buildBarOption(columns, rows) {
  if (!rows.length) return null;
  const kinds = colKinds(columns, rows[0]);
  const numIdx = kinds
    .map((k, i) => (k === "numeric" ? i : -1))
    .filter((i) => i >= 0);
  const catIdx = kinds.findIndex((k) => k === "category");
  const dateIdx = kinds.findIndex((k) => k === "date");

  const xIdx = catIdx >= 0 ? catIdx : dateIdx >= 0 ? dateIdx : 0;

  if (numIdx.length === 1 && xIdx >= 0 && xIdx !== numIdx[0]) {
    const xi = xIdx;
    const yi = numIdx[0];
    return {
      tooltip: { trigger: "axis" },
      grid: { left: 48, right: 24, top: 24, bottom: 48 },
      xAxis: {
        type: "category",
        data: rows.map((r) => String(r[xi] ?? "")),
        axisLabel: { rotate: rows.length > 8 ? 30 : 0 },
      },
      yAxis: { type: "value" },
      series: [{ type: "bar", data: rows.map((r) => r[yi]), name: columns[yi] }],
    };
  }

  if (numIdx.length >= 2 && xIdx >= 0) {
    return {
      tooltip: { trigger: "axis" },
      legend: { top: 0 },
      grid: { left: 48, right: 24, top: 40, bottom: 48 },
      xAxis: {
        type: "category",
        data: rows.map((r) => String(r[xIdx] ?? "")),
      },
      yAxis: { type: "value" },
      series: numIdx.map((yi) => ({
        type: "bar",
        name: columns[yi],
        data: rows.map((r) => r[yi]),
      })),
    };
  }

  if (numIdx.length === 1) {
    const yi = numIdx[0];
    return {
      tooltip: { trigger: "axis" },
      grid: { left: 48, right: 24, top: 24, bottom: 48 },
      xAxis: {
        type: "category",
        data: rows.map((_, i) => String(i + 1)),
      },
      yAxis: { type: "value" },
      series: [{ type: "bar", data: rows.map((r) => r[yi]), name: columns[yi] }],
    };
  }

  return null;
}

function buildLineOption(columns, rows) {
  const kinds = colKinds(columns, rows[0]);
  const numIdx = kinds.findIndex((k) => k === "numeric");
  const dateIdx = kinds.findIndex((k) => k === "date");
  if (numIdx < 0 || dateIdx < 0) return null;
  const sorted = [...rows].sort((a, b) =>
    String(a[dateIdx]).localeCompare(String(b[dateIdx])),
  );
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 48, right: 24, top: 24, bottom: 48 },
    xAxis: { type: "category", data: sorted.map((r) => String(r[dateIdx])) },
    yAxis: { type: "value" },
    series: [
      {
        type: "line",
        smooth: true,
        data: sorted.map((r) => r[numIdx]),
        name: columns[numIdx],
      },
    ],
  };
}

function kpiValue(columns, rows) {
  if (!rows.length) return null;
  const kinds = colKinds(columns, rows[0]);
  const numIdx = kinds.findIndex((k) => k === "numeric");
  if (numIdx < 0) return null;
  const v = rows[0][numIdx];
  return { label: columns[numIdx], value: v };
}

export default function ChartPanel({ chartType, columns, rows }) {
  if (!columns?.length || chartType === "table") {
    return (
      <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50/80 px-4 py-8 text-center text-sm text-slate-500">
        Chart not shown for this result shape. See the table below.
      </div>
    );
  }

  if (chartType === "kpi") {
    const kv = kpiValue(columns, rows);
    if (!kv) {
      return (
        <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-slate-500">
          No single numeric value to display.
        </div>
      );
    }
    return (
      <div className="flex min-h-[200px] flex-col items-center justify-center rounded-lg border border-slate-200 bg-gradient-to-b from-white to-slate-50 p-8 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          {kv.label}
        </p>
        <p className="mt-2 text-4xl font-semibold tabular-nums text-slate-900">
          {typeof kv.value === "number"
            ? kv.value.toLocaleString(undefined, { maximumFractionDigits: 2 })
            : kv.value}
        </p>
      </div>
    );
  }

  const option =
    chartType === "line"
      ? buildLineOption(columns, rows)
      : buildBarOption(columns, rows);

  if (!option) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
        Could not build a chart for this data.
      </div>
    );
  }

  return (
    <div className="h-[360px] w-full rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
      <ReactECharts option={option} style={{ height: "100%", width: "100%" }} />
    </div>
  );
}
