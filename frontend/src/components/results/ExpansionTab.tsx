import type { SearchResponse } from '../../types/search'

interface Props {
  data: SearchResponse
}

export default function ExpansionTab({ data }: Props) {
  const sorted = [...data.expansion_terms].sort((a, b) => b.score - a.score)
  const originalSet = new Set(data.query_original)

  return (
    <div className="mt-4 space-y-6">
      {/* Term pills */}
      <div className="rounded-xl border border-gray-200 dark:border-[#21262d] bg-white dark:bg-[#0d1117] p-4">
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70 mb-3">
          Query terms
        </p>
        <div className="flex flex-wrap gap-2">
          {data.query_original.map((term) => (
            <span
              key={term}
              className="inline-flex items-center rounded-lg bg-gray-100 dark:bg-[#21262d] text-gray-600 dark:text-[#e6edf3] px-3 py-1 text-xs font-mono border border-gray-200 dark:border-[#30363d]"
            >
              {term}
            </span>
          ))}
          {data.query_expanded
            .filter((t) => !originalSet.has(t))
            .map((term) => (
              <span
                key={term}
                className="inline-flex items-center rounded-lg bg-[#0891b2]/10 text-[#0891b2] dark:text-[#22d3ee] px-3 py-1 text-xs font-mono border border-[#0891b2]/25 shadow-[0_0_8px_rgba(8,145,178,0.1)]"
              >
                <span className="mr-1 opacity-60">+</span>
                {term}
              </span>
            ))}
        </div>
      </div>

      {/* Score table */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70 mb-3 flex items-center gap-1.5">
          <span className="inline-block h-px w-3 bg-current opacity-50" />
          Expansion terms
        </p>
        <div className="rounded-xl border border-gray-200 dark:border-[#21262d] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 dark:bg-[#0a0d16] border-b border-gray-100 dark:border-[#21262d]">
                <th className="text-left px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70 w-32">
                  Term
                </th>
                <th className="text-left px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70">
                  Similarity score
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-[#21262d]">
              {sorted.map((et, i) => (
                <tr
                  key={et.term}
                  className={`transition-colors ${
                    i === 0
                      ? 'bg-[#0891b2]/5 dark:bg-[#0891b2]/5'
                      : 'bg-white dark:bg-[#0d1117]'
                  }`}
                >
                  <td className="px-4 py-3">
                    <span className="font-mono text-sm text-gray-800 dark:text-[#e6edf3]">
                      {et.term}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-1.5 rounded-full bg-gray-100 dark:bg-[#21262d] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-[#0891b2] to-[#38bdf8]"
                          style={{ width: `${et.score * 100}%` }}
                        />
                      </div>
                      <span className="w-14 text-right font-mono text-xs text-[#0891b2] dark:text-[#22d3ee] tabular-nums font-semibold">
                        {et.score.toFixed(4)}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
