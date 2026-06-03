import math

_index_cache_id = None
_n_docs = 0
_max_tf_cache = {}
_norm_cache = {}

def _populate_cache_if_needed(index: dict):
    global _index_cache_id, _n_docs, _max_tf_cache, _norm_cache
    
    current_id = id(index)
    if _index_cache_id == current_id:
        return
        
    _index_cache_id = current_id
    _n_docs = 0
    _max_tf_cache = {}
    _norm_cache = {}
    
    # Track document IDs
    doc_ids = set()
    for entry in index.values():
        doc_ids.update(entry.get("postings", {}).keys())
    _n_docs = len(doc_ids)
    
    # Pass 1: compute max_tf
    for term, entry in index.items():
        postings = entry.get("postings", {})
        for doc_id, tf in postings.items():
            if doc_id not in _max_tf_cache:
                _max_tf_cache[doc_id] = 0
            if tf > _max_tf_cache[doc_id]:
                _max_tf_cache[doc_id] = tf
                
    # Pass 2: compute norms (tfidf_cos)
    norm_sq = {doc_id: 0.0 for doc_id in doc_ids}
    for term, entry in index.items():
        df = entry.get("df", 0)
        if df == 0:
            continue
            
        idf = math.log(_n_docs / df)
        postings = entry.get("postings", {})
        
        for doc_id, tf in postings.items():
            if tf > 0:
                tf_log = 1.0 + math.log(tf)
                w = tf_log * idf
                norm_sq[doc_id] += w * w
                
    for doc_id, sq in norm_sq.items():
        _norm_cache[doc_id] = math.sqrt(sq)

def get_n_docs(index: dict) -> int:
    _populate_cache_if_needed(index)
    return _n_docs

def get_max_tf(doc_id: str, index: dict) -> int:
    _populate_cache_if_needed(index)
    return _max_tf_cache.get(doc_id, 0)

def get_doc_norm(doc_id: str, index: dict, n_docs: int) -> float:
    _populate_cache_if_needed(index)
    return _norm_cache.get(doc_id, 0.0)

def get_weight(term: str, doc_id: str, scheme: str, index: dict) -> float:
    term_entry = index.get(term, {})
    tf = term_entry.get("postings", {}).get(doc_id, 0)
    
    if tf == 0 and scheme != "idf":
        return 0.0
        
    n_docs = get_n_docs(index)
    df = term_entry.get("df", 0)
    idf = math.log(n_docs / df) if df > 0 else 0.0
    
    if scheme == "tf_raw":
        return float(tf)
    elif scheme == "tf_log":
        return 1.0 + math.log(tf) if tf > 0 else 0.0
    elif scheme == "tf_bin":
        return 1.0 if tf > 0 else 0.0
    elif scheme == "tf_aug":
        max_tf = get_max_tf(doc_id, index)
        return 0.5 + 0.5 * (tf / max_tf) if max_tf > 0 else 0.0
    elif scheme == "idf":
        return idf
    elif scheme == "tfidf":
        tf_log = 1.0 + math.log(tf) if tf > 0 else 0.0
        return tf_log * idf
    elif scheme == "tfidf_cos":
        tf_log = 1.0 + math.log(tf) if tf > 0 else 0.0
        w = tf_log * idf
        norm = get_doc_norm(doc_id, index, n_docs)
        return w / norm if norm > 0 else 0.0
    else:
        raise ValueError(f"Unknown weighting scheme: {scheme}")
