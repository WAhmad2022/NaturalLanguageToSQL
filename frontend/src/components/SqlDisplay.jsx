export default function SqlDisplay({ sql }) {
  if (!sql) return null;
  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950 shadow-inner">
      <div className="border-b border-slate-800 px-3 py-1.5 text-xs font-medium text-slate-400">
        Generated SQL
      </div>
      <pre className="m-0 overflow-x-auto p-4 font-mono text-sm leading-relaxed text-emerald-400">
        <code>{sql}</code>
      </pre>
    </div>
  );
}
