import { useState } from 'react'
import { rebuildIndex } from '../api/search'
import type { SearchParams, WeightingScheme } from '../types/search'

interface Props {
  params: SearchParams
  onChange: (p: SearchParams) => void
}

const SCHEMES: { value: WeightingScheme; label: string }[] = [
  { value: 'tf_raw', label: 'TF Raw' },
  { value: 'tf_log', label: 'TF Log' },
  { value: 'tf_bin', label: 'TF Binary' },
  { value: 'tf_aug', label: 'TF Augmented' },
  { value: 'idf', label: 'IDF' },
  { value: 'tfidf', label: 'TF-IDF' },
  { value: 'tfidf_cos', label: 'TF-IDF Cosine' },
]

function Toggle({ value, onChange }: { value: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={value}
      onClick={() => onChange(!value)}
      className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-all duration-200 ${
        value
          ? 'bg-[#0891b2] shadow-[0_0_8px_rgba(8,145,178,0.4)]'
          : 'bg-gray-200 dark:bg-[#21262d]'
      }`}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
          value ? 'translate-x-4.5' : 'translate-x-0.5'
        }`}
      />
    </button>
  )
}

function SectionLabel({ children }: { children: string }) {
  return (
    <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-gray-400 dark:text-[#8b949e]/70 flex items-center gap-1.5">
      <span className="inline-block h-px w-3 bg-current opacity-50" />
      {children}
    </p>
  )
}

export default function ParameterPanel({ params, onChange }: Props) {
  const [loading, setLoading] = useState(false)

  const handleRebuild = async () => {
    if (!confirm('Apakah Anda yakin ingin menghapus semua index dan cache MAP? Proses ini akan memakan waktu saat pencarian berikutnya.')) return
    
    setLoading(true)
    try {
      const res = await rebuildIndex()
      alert(res.message)
    } catch (err) {
      alert('Gagal menghapus index: ' + err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="w-56 shrink-0 flex flex-col border-r border-gray-200 dark:border-[#0891b2]/10 bg-white dark:bg-[#0a0d16] h-full overflow-y-auto">
      {/* Brand strip */}
      <div className="px-4 pt-4 pb-3 border-b border-gray-100 dark:border-[#21262d]/60">
        <SectionLabel>Parameters</SectionLabel>
      </div>

      <div className="p-4 space-y-5 flex-1">
        {/* Preprocessing */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-600 dark:text-[#8b949e]">Stemming</label>
            <Toggle value={params.stemming} onChange={(v) => onChange({ ...params, stemming: v })} />
          </div>
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-600 dark:text-[#8b949e]">Stopwords</label>
            <Toggle value={params.removeStopword} onChange={(v) => onChange({ ...params, removeStopword: v })} />
          </div>
        </div>

        <div className="h-px bg-gray-100 dark:bg-[#21262d]/60" />

        {/* Weighting */}
        <div className="space-y-2">
          <SectionLabel>Weighting</SectionLabel>
          <select
            value={params.weightingScheme}
            onChange={(e) =>
              onChange({ ...params, weightingScheme: e.target.value as WeightingScheme })
            }
            className="w-full text-sm rounded-lg border border-gray-200 dark:border-[#21262d] bg-gray-50 dark:bg-[#0d1117] text-gray-800 dark:text-[#e6edf3] px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-[#0891b2]/30 focus:border-[#0891b2] transition-all appearance-none cursor-pointer"
          >
            {SCHEMES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>

        <div className="h-px bg-gray-100 dark:bg-[#21262d]/60" />

        {/* Retrieval */}
        <div className="space-y-3">
          <SectionLabel>Retrieval</SectionLabel>
          <div className="space-y-1.5">
            <label className="block text-xs text-gray-500 dark:text-[#8b949e]/70">
              Top-N results
            </label>
            <input
              type="number"
              min={1}
              max={50}
              value={params.topN}
              disabled={params.expandAll}
              onChange={(e) => onChange({ ...params, topN: Number(e.target.value) })}
              className="w-full text-sm rounded-lg border border-gray-200 dark:border-[#21262d] bg-gray-50 dark:bg-[#0d1117] text-gray-800 dark:text-[#e6edf3] px-2.5 py-2 focus:outline-none focus:ring-2 focus:ring-[#0891b2]/30 focus:border-[#0891b2] disabled:opacity-40 transition-all"
            />
          </div>

          <label className="flex items-center gap-2.5 cursor-pointer group">
            <div className={`h-4 w-4 rounded flex items-center justify-center border transition-all ${
              params.expandAll
                ? 'bg-[#0891b2] border-[#0891b2] shadow-[0_0_6px_rgba(8,145,178,0.4)]'
                : 'border-gray-300 dark:border-[#30363d] group-hover:border-[#0891b2]/60'
            }`}>
              <input
                type="checkbox"
                checked={params.expandAll}
                onChange={(e) => onChange({ ...params, expandAll: e.target.checked })}
                className="sr-only"
              />
              {params.expandAll && (
                <svg className="h-2.5 w-2.5 text-white" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                  <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </div>
            <span className="text-sm text-gray-600 dark:text-[#8b949e]">Expand all</span>
          </label>
        </div>

        <div className="h-px bg-gray-100 dark:bg-[#21262d]/60" />

        {/* Actions */}
        <div className="space-y-2">
          <SectionLabel>Management</SectionLabel>
          <button
            onClick={handleRebuild}
            disabled={loading}
            className="w-full text-xs font-medium py-2 px-3 rounded-lg border border-red-200 dark:border-red-900/30 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/20 transition-all disabled:opacity-50"
          >
            {loading ? 'Rebuilding...' : 'Rebuild Index'}
          </button>
        </div>
      </div>
    </aside>
  )
}
