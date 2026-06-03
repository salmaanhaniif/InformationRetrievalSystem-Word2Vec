import math
from collections import Counter
from src.weighting import get_weight, get_n_docs

def compute_query_weight(term: str, tf: int, max_tf: int, n_docs: int, df: int, scheme: str) -> float:
    if scheme == "tf_raw":
        return float(tf)
    elif scheme == "tf_log":
        return 1.0 + math.log(tf) if tf > 0 else 0.0
    elif scheme == "tf_bin":
        return 1.0 if tf > 0 else 0.0
    elif scheme == "tf_aug":
        return 0.5 + 0.5 * (tf / max_tf) if max_tf > 0 else 0.0
    elif scheme == "idf":
        return math.log(n_docs / df) if df > 0 else 0.0
    elif scheme in ("tfidf", "tfidf_cos"):
        tf_log = 1.0 + math.log(tf) if tf > 0 else 0.0
        idf = math.log(n_docs / df) if df > 0 else 0.0
        return tf_log * idf
    return 0.0

def rank_documents(query_terms: list[str], index: dict, scheme: str) -> list[tuple[str, float]]:
    if not query_terms:
        return []

    relevant_docs = set()
    for term in query_terms:
        if term in index:
            relevant_docs.update(index[term].get("postings", {}).keys())
            
    if not relevant_docs:
        return []

    n_docs = get_n_docs(index)
    query_counts = Counter(query_terms)
    max_query_tf = max(query_counts.values()) if query_counts else 0

    query_vector = {}
    for term, tf in query_counts.items():
        df = index.get(term, {}).get("df", 0)
        query_vector[term] = compute_query_weight(term, tf, max_query_tf, n_docs, df, scheme)

    if scheme == "tfidf_cos":
        q_norm = math.sqrt(sum(w*w for w in query_vector.values()))
        if q_norm > 0:
            for term in query_vector:
                query_vector[term] /= q_norm

    scores = []
    
    for doc_id in relevant_docs:
        doc_vector = {}
        for term in query_vector.keys():
            doc_vector[term] = get_weight(term, doc_id, scheme, index)
            
        score = sum(query_vector.get(t, 0.0) * doc_vector.get(t, 0.0) for t in query_vector)
            
        if score > 0:
            scores.append((doc_id, score))
            
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
