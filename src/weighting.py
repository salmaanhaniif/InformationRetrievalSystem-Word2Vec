import math

_n_docs_cache = {}
_max_tf_cache = {}
_norm_cache = {}

def get_n_docs(index: dict) -> int:
    index_id = id(index)
    if index_id in _n_docs_cache:
        return _n_docs_cache[index_id]
        
    doc_ids = set()
    for entry in index.values():
        doc_ids.update(entry.get("postings", {}).keys())
        
    _n_docs_cache[index_id] = len(doc_ids)
    return _n_docs_cache[index_id]

def get_max_tf(doc_id: str, index: dict) -> int:
    index_id = id(index)
    if index_id not in _max_tf_cache:
        _max_tf_cache[index_id] = {}
        
    if doc_id in _max_tf_cache[index_id]:
        return _max_tf_cache[index_id][doc_id]
        
    max_tf = 0
    for entry in index.values():
        tf = entry.get("postings", {}).get(doc_id, 0)
        if tf > max_tf:
            max_tf = tf
            
    _max_tf_cache[index_id][doc_id] = max_tf
    return max_tf

def get_doc_norm(doc_id: str, index: dict, n_docs: int) -> float:
    index_id = id(index)
    if index_id not in _norm_cache:
        _norm_cache[index_id] = {}
        
    if doc_id in _norm_cache[index_id]:
        return _norm_cache[index_id][doc_id]
        
    norm_sq = 0.0
    for entry in index.values():
        tf = entry.get("postings", {}).get(doc_id, 0)
        if tf > 0:
            df = entry.get("df", 0)
            idf = math.log(n_docs / df) if df > 0 else 0.0
            tf_log = 1.0 + math.log(tf)
            w = tf_log * idf
            norm_sq += w * w
            
    norm = math.sqrt(norm_sq)
    _norm_cache[index_id][doc_id] = norm
    return norm

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
