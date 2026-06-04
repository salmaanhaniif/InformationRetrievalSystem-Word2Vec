import { useState, useEffect } from 'react'
import type { SearchParams } from '../types/search'
import { useSearch } from '../hooks/useSearch'
import ParameterPanel from '../components/ParameterPanel'
import SearchBar from '../components/SearchBar'
import TabBar from '../components/ui/TabBar'
import EmptyState from '../components/ui/EmptyState'
import ResultsTab from '../components/results/ResultsTab'
import ExpansionTab from '../components/results/ExpansionTab'
import MapReportTab from '../components/results/MapReportTab'

type ActiveTab = 'results' | 'expansion' | 'map'

export default function SearchPage() {
  const [params, setParams] = useState<SearchParams>({
    query: '',
    stemming: true,
    removeStopword: true,
    weightingScheme: 'tfidf_cos',
    topN: 5,
    expandAll: false,
  })
  const [activeTab, setActiveTab] = useState<ActiveTab>('results')
  const [darkMode, setDarkMode] = useState<boolean>(
    () => localStorage.getItem('darkMode') !== 'false',
  )
  const { data, loading, error, search } = useSearch()

  useEffect(() => {
    localStorage.setItem('darkMode', String(darkMode))
  }, [darkMode])

  return (
    <div
      className={`flex h-screen bg-[#f0fdff] dark:bg-[#070c14] ${darkMode ? 'dark' : ''}`}
    >
      <ParameterPanel params={params} onChange={setParams} />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="flex items-center justify-between px-6 py-3.5 shrink-0 border-b border-gray-200 dark:border-[#0891b2]/15 bg-white/90 dark:bg-[#0d1117]/80 backdrop-blur-sm">
          <div className="flex items-center gap-2.5">
            <div className="h-6 w-6 rounded-md bg-[#0891b2] flex items-center justify-center shadow-[0_0_10px_rgba(8,145,178,0.5)]">
              <svg className="h-3.5 w-3.5 text-white" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06 1.06l-3.329-3.328A7 7 0 0 1 2 9Z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-sm font-bold tracking-tight text-gray-800 dark:text-[#e6edf3]">
              IR System
              <span className="text-[#0891b2] dark:text-[#22d3ee]"> / </span>
              <span className="font-semibold text-gray-500 dark:text-[#8b949e]">Word2Vec</span>
            </h1>
          </div>

          <button
            type="button"
            onClick={() => setDarkMode((d) => !d)}
            className="p-1.5 rounded-md text-gray-400 dark:text-[#8b949e] hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg className="h-4.5 w-4.5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 2.25a.75.75 0 0 1 .75.75v2.25a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM7.5 12a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM18.894 6.166a.75.75 0 0 0-1.06-1.06l-1.591 1.59a.75.75 0 1 0 1.06 1.061l1.591-1.59ZM21.75 12a.75.75 0 0 1-.75.75h-2.25a.75.75 0 0 1 0-1.5H21a.75.75 0 0 1 .75.75ZM17.834 18.894a.75.75 0 0 0 1.06-1.06l-1.59-1.591a.75.75 0 1 0-1.061 1.06l1.59 1.591ZM12 18a.75.75 0 0 1 .75.75V21a.75.75 0 0 1-1.5 0v-2.25A.75.75 0 0 1 12 18ZM7.166 17.834a.75.75 0 0 0-1.06 1.06l1.59 1.591a.75.75 0 1 0 1.061-1.06l-1.591-1.591ZM6 12a.75.75 0 0 1-.75.75H3a.75.75 0 0 1 0-1.5h2.25A.75.75 0 0 1 6 12ZM6.166 6.166a.75.75 0 0 0 1.06 1.06l1.591-1.59a.75.75 0 1 0-1.061-1.061l-1.59 1.591Z" />
              </svg>
            ) : (
              <svg className="h-4.5 w-4.5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M9.528 1.718a.75.75 0 0 1 .162.819A8.97 8.97 0 0 0 9 6a9 9 0 0 0 9 9 8.97 8.97 0 0 0 3.463-.69.75.75 0 0 1 .981.98 10.503 10.503 0 0 1-9.694 6.46c-5.799 0-10.5-4.7-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 0 1 .818.162Z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        </header>

        {/* Search */}
        <div className="px-6 py-4 shrink-0 border-b border-gray-200 dark:border-[#21262d]">
          <SearchBar
            value={params.query}
            onChange={(v) => setParams((p) => ({ ...p, query: v }))}
            onSearch={() => search(params)}
            loading={loading}
          />
        </div>

        {/* Error banner */}
        {error && (
          <div className="mx-6 mt-3 shrink-0 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 px-3.5 py-2 text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
            <svg className="h-3.5 w-3.5 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto px-6 pb-6">
          {!data ? (
            <EmptyState />
          ) : (
            <>
              <div className="sticky top-0 bg-[#f0fdff] dark:bg-[#070c14] pt-4 pb-1 z-10">
                <TabBar active={activeTab} onChange={setActiveTab} />
              </div>
              {activeTab === 'results' && <ResultsTab data={data} />}
              {activeTab === 'expansion' && <ExpansionTab data={data} />}
              {activeTab === 'map' && <MapReportTab data={data} params={params} />}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
