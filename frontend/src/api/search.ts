import type { SearchParams, SearchResponse, ExpansionTerm, QueryMapResult } from '../types/search'

const BASE_URL = 'http://localhost:8000'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export function searchDocuments(params: SearchParams): Promise<SearchResponse> {
  return post<SearchResponse>('/api/search', params)
}

export function expandQuery(terms: string[], topN: number): Promise<ExpansionTerm[]> {
  return post<ExpansionTerm[]>('/api/expand', { terms, topN })
}

export function getInvertedIndex(docId: string): Promise<Record<string, unknown>> {
  return get<Record<string, unknown>>(`/api/index/${docId}`)
}

export function getMapReport(): Promise<QueryMapResult[]> {
  return get<QueryMapResult[]>('/api/map')
}

export function rebuildIndex(): Promise<{ message: string }> {
  return post<{ message: string }>('/api/index/rebuild', {})
}

export function recalculateMapSingle(params: SearchParams): Promise<{ message: string }> {
  return post<{ message: string }>('/api/map/recalculate/single', params)
}

export function recalculateMapAll(): Promise<{ message: string }> {
  return post<{ message: string }>('/api/map/recalculate/all', {})
}
