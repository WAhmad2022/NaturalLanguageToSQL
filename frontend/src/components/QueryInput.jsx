const EXAMPLES = [
  "What were total sales by region?",
  "Show total sales for each product category",
  "What is the average unit price?",
  "How many orders are in the database?",
  "List total quantity sold by region",
  "What were sales in January 2024?",
];

export default function QueryInput({
  value,
  onChange,
  onSubmit,
  disabled,
}) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-slate-600">
        Business question
      </label>
      <select
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm"
        defaultValue=""
        onChange={(e) => {
          const q = e.target.value;
          if (q) onChange(q);
          e.target.value = "";
        }}
        disabled={disabled}
      >
        <option value="" disabled>
          Try an example…
        </option>
        {EXAMPLES.map((q) => (
          <option key={q} value={q}>
            {q}
          </option>
        ))}
      </select>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          className="min-w-0 flex-1 rounded-lg border border-slate-200 px-4 py-3 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          placeholder='e.g. "What were total sales by region last quarter?"'
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit();
            }
          }}
          disabled={disabled}
        />
        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-6 py-3 font-medium text-white shadow-sm hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
        >
          Ask
        </button>
      </div>
    </div>
  );
}
