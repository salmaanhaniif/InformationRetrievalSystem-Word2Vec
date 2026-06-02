from src.word2vec_engine import get_engine

def expand_query( query_terms: list[str], top_n = 5,) -> list[tuple[str, float]]:
    """
    Expand query dengan menambahkan kata-kata semantically similar dari Word2Vec model.
    Return example: [("indexing", 0.81), ("document", 0.78), ("search", 0.75)]
    """
    if not query_terms:
        return []

    engine = get_engine()

    seen       = set(t.lower().strip() for t in query_terms)
    candidates = {}

    for term in query_terms:
        term = term.lower().strip()
        similars = engine.get_similar(term, top_n=top_n * 3)

        for word, score in similars:
            word = word.lower().strip()

            if word in seen:
                continue

            # Kalau kata sama muncul dari dua query term, ambil score tertinggi
            if word not in candidates or score > candidates[word]:
                candidates[word] = score

            seen.add(word)

    expanded = sorted(candidates.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return expanded


def expand_query_all(query_terms: list[str]) -> list[tuple[str, float]]:
    """
    Versi expand_query tanpa batas jumlah term — kembalikan semua kandidat.
    Dipakai ketika user pilih 'tambahkan semua kata'.

    Returns:
        list of (term, weight), diurutkan descending
    """
    if not query_terms:
        return []

    engine    = get_engine()
    seen      = set(t.lower().strip() for t in query_terms)
    candidates = {}

    for term in query_terms:
        term     = term.lower().strip()
        similars = engine.get_similar(term, top_n=50)  # ambil banyak

        for word, score in similars:
            word = word.lower().strip()
            if word in seen:
                continue
            if word not in candidates or score > candidates[word]:
                candidates[word] = score
            seen.add(word)

    return sorted(candidates.items(), key=lambda x: x[1], reverse=True)


def get_expanded_query_terms(query_terms: list[str], top_n = 5,expand_all = False,) ->  list[str]:
    """
    Helper — kembalikan hanya list of strings (tanpa bobot).
    Menggabungkan query asli + expansion terms.
    Dipakai saat mau langsung feed ke retrieval.

    Args:
        query_terms : token query asli
        top_n       : jumlah term tambahan
        expand_all  : True = pakai expand_query_all()

    Returns:
        query_terms asli + expanded terms, tanpa duplikat
        contoh: ["information", "retrieval", "indexing", "document", "search"]
    """
    if expand_all:
        expanded_pairs = expand_query_all(query_terms)
    else:
        expanded_pairs = expand_query(query_terms, top_n=top_n)

    expanded_terms = [term for term, _ in expanded_pairs]
    return query_terms + expanded_terms


def format_expansion_detail(query_terms: list[str], expanded: list[tuple[str, float]], query_id: str = "",) -> str:
    """
    Format hasil expansion jadi string yang siap ditulis ke output/expansion_detail.txt

    Contoh output:
        ===== QUERY Q001 =====
        Original terms : ['information', 'retrieval']
        Expanded terms :
          + indexing       (score: 0.8123)
          + document       (score: 0.7891)
          + search         (score: 0.7654)
    """
    header = f"===== QUERY {query_id} =====" if query_id else "===== QUERY ====="
    lines  = [
        header,
        f"Original terms : {query_terms}",
        "Expanded terms :",
    ]

    if not expanded:
        lines.append("  (tidak ada — semua term OOV atau model belum di-load)")
    else:
        for term, score in expanded:
            lines.append(f"  + {term:<20} (score: {score:.4f})")

    lines.append("") 
    return "\n".join(lines)