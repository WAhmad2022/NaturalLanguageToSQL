export default function ResultsTable({ columns, rows }) {
  if (!columns?.length) return null;
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700">
        Results
      </div>
      <div className="max-h-80 overflow-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="sticky top-0 bg-slate-100">
            <tr>
              {columns.map((c) => (
                <th
                  key={c}
                  className="border-b border-slate-200 px-4 py-2 font-semibold text-slate-700"
                >
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className={i % 2 === 0 ? "bg-white" : "bg-slate-50/80"}
              >
                {row.map((cell, j) => (
                  <td
                    key={j}
                    className="border-b border-slate-100 px-4 py-2 text-slate-800"
                  >
                    {cell === null || cell === undefined ? "" : String(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
