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

    n_docs = get_n_docs(index)
    query_counts = Counter(query_terms)
    max_query_tf = max(query_counts.values()) if query_counts else 0

    query_vector = {}
    for term, tf in query_counts.items():
        df = index.get(term, {}).get("df", 0)
        if df > 0:
            query_vector[term] = compute_query_weight(term, tf, max_query_tf, n_docs, df, scheme)

    if scheme == "tfidf_cos":
        q_norm = math.sqrt(sum(w*w for w in query_vector.values()))
        if q_norm > 0:
            for term in query_vector:
                query_vector[term] /= q_norm

    scores_dict = {}
    
    for term, q_w in query_vector.items():
        if q_w == 0.0:
            continue
            
        postings = index.get(term, {}).get("postings", {})
        for doc_id, tf in postings.items():
            if tf > 0:
                d_w = get_weight(term, doc_id, scheme, index)
                if doc_id not in scores_dict:
                    scores_dict[doc_id] = 0.0
                scores_dict[doc_id] += q_w * d_w
            
    scores = [(doc_id, score) for doc_id, score in scores_dict.items() if score > 0]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
