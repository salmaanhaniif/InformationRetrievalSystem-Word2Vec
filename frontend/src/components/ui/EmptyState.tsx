export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-5 select-none">
      <div className="relative">
        {/* Glow ring */}
        <div className="absolute inset-0 rounded-full bg-[#0891b2] glow-pulse" style={{ margin: '-16px' }} />
        <div className="relative z-10 h-16 w-16 rounded-full bg-[#0d1117] dark:bg-[#0a0d16] border border-[#21262d] dark:border-[#0891b2]/20 flex items-center justify-center shadow-[0_0_0_1px_rgba(8,145,178,0.1)]">
          <svg
            className="h-7 w-7 text-[#0891b2] opacity-70"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
        </div>
      </div>

      <div className="text-center space-y-1">
        <p className="text-sm font-medium text-gray-600 dark:text-[#8b949e]">
          Enter a query to start searching
        </p>
        <p className="text-xs text-gray-400 dark:text-[#8b949e]/50">
          Results, expansion terms, and MAP report will appear here
        </p>
      </div>
    </div>
  )
}
