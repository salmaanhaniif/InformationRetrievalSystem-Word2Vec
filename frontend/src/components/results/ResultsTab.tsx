import type { SearchResponse, RankedDocument } from '../../types/search'

interface Props {
  data: SearchResponse
}

const RANK_STYLE: Record<number, string> = {
  1: 'bg-yellow-400/15 text-yellow-400 border-yellow-400/30',
  2: 'bg-gray-300/15 text-gray-300 border-gray-300/30',
  3: 'bg-amber-600/15 text-amber-500 border-amber-600/30',
}

function RankBadge({ rank }: { rank: number }) {
  const style = RANK_STYLE[rank] ?? 'bg-gray-100 dark:bg-[#21262d]/60 text-gray-400 dark:text-[#8b949e] border-transparent'
  return (
    <span className={`inline-flex items-center justify-center h-5 w-5 rounded-md text-[10px] font-bold border ${style} shrink-0`}>
      {rank}
    </span>
  )
}

function DocCard({ doc, improved }: { doc: RankedDocument; improved: boolean }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 border transition-all ${
        improved
          ? 'border-[#0891b2]/25 bg-[#0891b2]/5 dark:bg-[#0891b2]/8 shadow-[0_0_12px_rgba(8,145,178,0.08)]'
          : 'border-gray-200 dark:border-[#21262d] bg-white dark:bg-[#0d1117] hover:border-gray-300 dark:hover:border-[#30363d]'
      }`}
    >
      <RankBadge rank={doc.rank} />
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-mono text-gray-400 dark:text-[#8b949e]/70 leading-none mb-0.5">
          {doc.doc_id}
        </p>
        <p className="text-sm text-gray-800 dark:text-[#e6edf3] truncate leading-snug">
          {doc.title}
        </p>
      </div>
      <span className={`shrink-0 text-xs font-mono font-semibold tabular-nums ${improved ? 'text-[#0891b2]' : 'text-gray-400 dark:text-[#8b949e]'}`}>
        {doc.similarity.toFixed(4)}
      </span>
    </div>
  )
}

function ColHeader({ label, map }: { label: string; map: number }) {
  return (
    <div className="flex items-center justify-between mb-2.5">
      <p className="text-xs font-semibold text-gray-600 dark:text-[#e6edf3]/80 uppercase tracking-wide">
        {label}
      </p>
      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-gray-100 dark:bg-[#21262d] text-gray-500 dark:text-[#8b949e]">
        MAP {map.toFixed(4)}
      </span>
    </div>
  )
}

export default function ResultsTab({ data }: Props) {
  const origRankMap = new Map(data.results_original.map((d) => [d.doc_id, d.rank]))

  function isImproved(doc: RankedDocument): boolean {
    const origRank = origRankMap.get(doc.doc_id)
    return origRank === undefined || doc.rank < origRank
  }

  return (
    <div className="grid grid-cols-2 gap-5 mt-4">
      <div>
        <ColHeader label="Original query" map={data.map_original} />
        <div className="space-y-2">
          {data.results_original.map((doc) => (
            <DocCard key={doc.doc_id} doc={doc} improved={false} />
          ))}
        </div>
      </div>

      <div>
        <ColHeader label="Expanded query" map={data.map_expanded} />
        <div className="space-y-2">
          {data.results_expanded.map((doc) => (
            <DocCard key={doc.doc_id} doc={doc} improved={isImproved(doc)} />
          ))}
        </div>
      </div>
    </div>
  )
}
