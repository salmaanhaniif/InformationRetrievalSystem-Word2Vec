type Tab = 'results' | 'expansion' | 'map'

interface Props {
  active: Tab
  onChange: (t: Tab) => void
}

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'results',   label: 'Results',    icon: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2' },
  { id: 'expansion', label: 'Expansion',  icon: 'M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z' },
  { id: 'map',       label: 'MAP Report', icon: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z' },
]

export default function TabBar({ active, onChange }: Props) {
  return (
    <div className="flex gap-1 border-b border-gray-200 dark:border-[#21262d]">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onChange(tab.id)}
          className={`flex items-center gap-1.5 px-3.5 py-2.5 text-sm font-medium transition-all border-b-2 -mb-px rounded-t-sm ${
            active === tab.id
              ? 'border-[#0891b2] text-[#0891b2] dark:text-[#22d3ee] dark:drop-shadow-[0_0_6px_rgba(34,211,238,0.5)]'
              : 'border-transparent text-gray-500 dark:text-[#8b949e] hover:text-gray-700 dark:hover:text-[#e6edf3] hover:border-gray-300 dark:hover:border-[#30363d]'
          }`}
        >
          <svg className="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d={tab.icon} />
          </svg>
          {tab.label}
        </button>
      ))}
    </div>
  )
}
