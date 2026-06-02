export type WeightingScheme =
  | 'tf_raw' | 'tf_log' | 'tf_bin' | 'tf_aug'
  | 'idf' | 'tfidf' | 'tfidf_cos'

export interface SearchParams {
  query: string
  stemming: boolean
  removeStopword: boolean
  weightingScheme: WeightingScheme
  topN: number
  expandAll: boolean
}

export interface RankedDocument {
  doc_id: string
  title: string
  similarity: number
  rank: number
}

export interface ExpansionTerm {
  term: string
  score: number
}

export interface QueryMapResult {
  query_id: string
  query_text: string
  map_original: number
  map_expanded: number
}

export interface SearchResponse {
  query_original: string[]
  query_expanded: string[]
  expansion_terms: ExpansionTerm[]
  results_original: RankedDocument[]
  results_expanded: RankedDocument[]
  map_original: number
  map_expanded: number
  per_query_map: QueryMapResult[]
}
