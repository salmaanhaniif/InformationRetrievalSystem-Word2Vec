interface Props {
  value: string
  onChange: (v: string) => void
  onSearch: () => void
  loading: boolean
}

export default function SearchBar({ value, onChange, onSearch, loading }: Props) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex-1 group">
        <span className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-gray-400 dark:text-[#8b949e] group-focus-within:text-[#0891b2] transition-colors">
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06 1.06l-3.329-3.328A7 7 0 0 1 2 9Z" clipRule="evenodd" />
          </svg>
        </span>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          placeholder="Enter search query…"
          className="w-full rounded-xl border border-gray-200 dark:border-[#21262d] bg-white dark:bg-[#0d1117] text-gray-800 dark:text-[#e6edf3] pl-10 pr-4 py-3 text-sm placeholder-gray-400 dark:placeholder-[#8b949e]/60 focus:outline-none focus:border-[#0891b2] focus:ring-2 focus:ring-[#0891b2]/20 dark:focus:ring-[#0891b2]/15 transition-all"
        />
      </div>
      <button
        type="button"
        disabled={loading}
        onClick={onSearch}
        className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#0891b2] to-[#0284c7] hover:from-[#0e7490] hover:to-[#0369a1] disabled:opacity-50 text-white px-5 py-3 text-sm font-semibold transition-all shadow-[0_2px_16px_rgba(8,145,178,0.35)] hover:shadow-[0_2px_20px_rgba(8,145,178,0.5)] disabled:shadow-none cursor-pointer disabled:cursor-not-allowed"
      >
        {loading ? (
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4Z" />
          </svg>
        ) : (
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" d="M3 10a.75.75 0 0 1 .75-.75h10.638L10.23 5.29a.75.75 0 1 1 1.04-1.08l5.5 5.25a.75.75 0 0 1 0 1.08l-5.5 5.25a.75.75 0 1 1-1.04-1.08l4.158-3.96H3.75A.75.75 0 0 1 3 10Z" clipRule="evenodd" />
          </svg>
        )}
        {loading ? 'Searching…' : 'Search'}
      </button>
    </div>
  )
}
