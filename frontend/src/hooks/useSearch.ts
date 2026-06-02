import { useState } from 'react'
import { searchDocuments } from '../api/search'
import type { SearchParams, SearchResponse } from '../types/search'

const MOCK: SearchResponse = {
  query_original: ['inform', 'retriev'],
  query_expanded: ['inform', 'retriev', 'index', 'document', 'search'],
  expansion_terms: [
    { term: 'index', score: 0.81 },
    { term: 'document', score: 0.78 },
    { term: 'search', score: 0.75 },
  ],
  results_original: [
    { doc_id: 'DOC001', title: 'Information Retrieval Systems', similarity: 0.91, rank: 1 },
    { doc_id: 'DOC002', title: 'Indexing and Document Retrieval', similarity: 0.87, rank: 2 },
    { doc_id: 'DOC003', title: 'Boolean Query Processing', similarity: 0.74, rank: 3 },
  ],
  results_expanded: [
    { doc_id: 'DOC002', title: 'Indexing and Document Retrieval', similarity: 0.94, rank: 1 },
    { doc_id: 'DOC001', title: 'Information Retrieval Systems', similarity: 0.90, rank: 2 },
    { doc_id: 'DOC004', title: 'Search Engine Architecture', similarity: 0.82, rank: 3 },
  ],
  map_original: 0.6373,
  map_expanded: 0.7340,
  per_query_map: [
    { query_id: 'Q001', query_text: 'information retrieval', map_original: 0.61, map_expanded: 0.73 },
    { query_id: 'Q002', query_text: 'library indexing', map_original: 0.58, map_expanded: 0.69 },
    { query_id: 'Q003', query_text: 'document classification', map_original: 0.72, map_expanded: 0.78 },
  ],
}

export interface UseSearchReturn {
  data: SearchResponse | null
  loading: boolean
  error: string | null
  search: (params: SearchParams) => void
}

export function useSearch(): UseSearchReturn {
  const [data, setData] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const search = (params: SearchParams): void => {
    setLoading(true)
    setError(null)
    searchDocuments(params)
      .then((result) => {
        setData(result)
      })
      .catch((e: unknown) => {
        const msg = e instanceof Error ? e.message : 'Unknown error'
        setError(`Backend unavailable (${msg}) — showing mock data`)
        setData(MOCK)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  return { data, loading, error, search }
}
