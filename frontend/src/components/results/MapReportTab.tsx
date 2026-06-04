import { useState } from 'react'
import { recalculateMapAll, recalculateMapSingle } from '../../api/search'
import type { SearchResponse, SearchParams } from '../../types/search'

interface Props {
  data: SearchResponse
  params: SearchParams
}

export default function MapReportTab({ data, params }: Props) {
  const [loading, setLoading] = useState(false)
  const globalDelta = data.map_expanded - data.map_original
  const pctGain = ((globalDelta / data.map_original) * 100).toFixed(1)

  const handleRecalculateSingle = async () => {
    if (!confirm('Recalculate MAP ONLY for current parameter and weighting?')) return
    setLoading(true)
    try {
      const res = await recalculateMapSingle(params)
      alert(res.message)
    } catch (err) {
      alert('Gagal kalkulasi ulang: ' + err)
    } finally {
      setLoading(false)
    }
  }

  const handleRecalculateAll = async () => {
    if (!confirm('Recalculate MAP benchmark for all 28 variations? Ini akan memakan waktu beberapa menit.')) return
    setLoading(true)
    try {
      const res = await recalculateMapAll()
      alert(res.message)
    } catch (err) {
      alert('Gagal kalkulasi ulang: ' + err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4 space-y-5">
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70">
            Precision Metrics
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRecalculateSingle}
            disabled={loading}
            className="flex-1 text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg border border-gray-200 dark:border-[#21262d] bg-white dark:bg-[#0d1117] text-gray-500 dark:text-[#8b949e] hover:bg-gray-50 dark:hover:bg-[#161b22] transition-all disabled:opacity-50"
          >
            {loading ? 'Recalculating...' : 'Recalculate MAP for this parameter and weighting'}
          </button>
          <button
            onClick={handleRecalculateAll}
            disabled={loading}
            className="flex-1 text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg border border-[#0891b2]/20 dark:border-[#0891b2]/10 bg-[#0891b2]/5 dark:bg-[#0891b2]/8 text-[#0891b2] dark:text-[#22d3ee] hover:bg-[#0891b2]/10 dark:hover:bg-[#0891b2]/15 transition-all disabled:opacity-50"
          >
            {loading ? 'Recalculating all...' : 'Recalculate MAP for all 28 variations'}
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-gray-200 dark:border-[#21262d] bg-white dark:bg-[#0d1117] p-5">
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70 mb-3">
            MAP Original
          </p>
          <p className="text-4xl font-bold tabular-nums text-gray-800 dark:text-[#e6edf3] leading-none">
            {data.map_original.toFixed(4)}
          </p>
          <p className="text-xs text-gray-400 dark:text-[#8b949e]/60 mt-2">Baseline</p>
        </div>

        <div className="rounded-xl border border-[#0891b2]/30 dark:border-[#0891b2]/20 bg-[#0891b2]/5 dark:bg-[#0891b2]/8 p-5 shadow-[0_0_24px_rgba(8,145,178,0.1)] relative overflow-hidden">
          {/* Background glow */}
          <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-[#0891b2]/10 blur-2xl" />
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#0891b2]/70 dark:text-[#22d3ee]/60 mb-3 relative">
            MAP Expanded
          </p>
          <p className="text-4xl font-bold tabular-nums text-[#0891b2] dark:text-[#22d3ee] leading-none relative">
            {data.map_expanded.toFixed(4)}
          </p>
          <div className="flex items-center gap-2 mt-2 relative">
            <span
              className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
                globalDelta >= 0
                  ? 'bg-green-500/15 text-green-400'
                  : 'bg-red-500/15 text-red-400'
              }`}
            >
              {globalDelta >= 0 ? '↑' : '↓'}
              {globalDelta >= 0 ? '+' : ''}{globalDelta.toFixed(4)}
            </span>
            <span className="text-xs text-gray-400 dark:text-[#8b949e]/60">
              {globalDelta >= 0 ? '+' : ''}{pctGain}%
            </span>
          </div>
        </div>
      </div>

      {/* Per-query table */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70 mb-3 flex items-center gap-1.5">
          <span className="inline-block h-px w-3 bg-current opacity-50" />
          Per-query breakdown
        </p>
        <div className="rounded-xl border border-gray-200 dark:border-[#21262d] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 dark:bg-[#0a0d16] border-b border-gray-100 dark:border-[#21262d]">
                <th className="text-left px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70">
                  Query
                </th>
                <th className="text-right px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70">
                  Original
                </th>
                <th className="text-right px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70">
                  Expanded
                </th>
                <th className="text-right px-4 py-2.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-[#8b949e]/70">
                  Δ Delta
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-[#21262d]">
              {data.per_query_map.map((row) => {
                const delta = row.map_expanded - row.map_original
                return (
                  <tr key={row.query_id} className="bg-white dark:bg-[#0d1117] hover:bg-gray-50 dark:hover:bg-[#0a0d16] transition-colors">
                    <td className="px-4 py-3 text-gray-800 dark:text-[#e6edf3]">
                      <span className="inline-block text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-[#21262d] text-gray-400 dark:text-[#8b949e] mr-2">
                        {row.query_id}
                      </span>
                      {row.query_text}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-gray-500 dark:text-[#8b949e]">
                      {row.map_original.toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-[#0891b2] dark:text-[#22d3ee]">
                      {row.map_expanded.toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span
                        className={`inline-flex items-center justify-end gap-0.5 font-mono text-xs font-semibold tabular-nums ${
                          delta >= 0 ? 'text-green-500' : 'text-red-500'
                        }`}
                      >
                        {delta >= 0 ? '+' : ''}{delta.toFixed(4)}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
