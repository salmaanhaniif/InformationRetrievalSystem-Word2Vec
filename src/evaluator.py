from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

from src.parser import parse_text
from src.preprocessor import preprocess
from src.query_expansion import get_expanded_query_terms


def parse_qrels(file_path: str) -> dict[str, set[str]]:
    """
    Parse qrels file (TREC format: query_id iter doc_id relevance).
    Returns dict of query_id -> set of relevant doc_ids.

    Handles two cases:
    1. Standard format with relevance > 0 in column 4
    2. Binary format where presence in file means relevant (all rel=0)
    """
    qrels: dict[str, set[str]] = {}
    path = Path(file_path)

    if not path.exists():
        return qrels

    raw = path.read_text(encoding="utf-8")
    has_nonzero = False

    # First pass: check if any relevance > 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 4 and int(parts[3]) > 0:
            has_nonzero = True
            break

    # Second pass: parse qrels
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 4:
            continue

        query_id = parts[0]
        # TREC format: query_id iter doc_id relevance
        # But CISI qrels may be: query_id doc_id iter relevance
        # Try column 2 first (standard TREC), fall back to column 1
        doc_id_raw = parts[2]
        relevance = int(parts[3])

        # If doc_id is 0, try column 1 instead
        if doc_id_raw == "0":
            doc_id_raw = parts[1]
            relevance = int(parts[2]) if len(parts) > 2 else 0

        # Normalize doc_id to match parser output (DOC###)
        doc_id = f"DOC{int(doc_id_raw):03d}"

        if has_nonzero:
            if relevance > 0:
                if query_id not in qrels:
                    qrels[query_id] = set()
                qrels[query_id].add(doc_id)
        else:
            if query_id not in qrels:
                qrels[query_id] = set()
            qrels[query_id].add(doc_id)

    return qrels


def parse_queries(file_path: str) -> dict[str, str]:
    """
    Parse queries from .text format (same as document format).
    Returns dict of query_id -> query_text.
    """
    raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    docs = parse_text(raw)
    return docs


def build_index_for_retrieval(
    docs: dict[str, str],
    stemming: bool = True,
    remove_stopword: bool = True,
) -> tuple[dict[str, dict[str, int]], dict[str, list[str]]]:
    """
    Build inverted index and store tokenized docs for retrieval.
    Returns (inverted_index, tokenized_docs).
    """
    inverted_index: dict[str, dict[str, int]] = {}
    tokenized_docs: dict[str, list[str]] = {}

    for doc_id, content in docs.items():
        tokens = preprocess(content, stemming, remove_stopword)
        if not tokens:
            continue

        tokenized_docs[doc_id] = tokens
        term_counts = Counter(tokens)

        for term, count in term_counts.items():
            if term not in inverted_index:
                inverted_index[term] = {}
            inverted_index[term][doc_id] = count

    return inverted_index, tokenized_docs


def compute_idf(
    inverted_index: dict[str, dict[str, int]],
    num_docs: int,
) -> dict[str, float]:
    """
    Compute IDF for each term in the inverted index.
    IDF(t) = log(N / df(t)) where df(t) is document frequency.
    """
    idf: dict[str, float] = {}
    for term, postings in inverted_index.items():
        df = len(postings)
        idf[term] = math.log(num_docs / df) if df > 0 else 0.0
    return idf


def compute_tf_idf_vector(
    tokens: list[str],
    idf: dict[str, float],
) -> dict[str, float]:
    """
    Compute TF-IDF vector for a document or query.
    Uses log-normalized TF: tf(t,d) = 1 + log(count(t,d)) if count > 0, else 0.
    """
    if not tokens:
        return {}

    term_counts = Counter(tokens)
    vector: dict[str, float] = {}

    for term, count in term_counts.items():
        tf = 1 + math.log(count) if count > 0 else 0.0
        idf_val = idf.get(term, 0.0)
        vector[term] = tf * idf_val

    return vector


def cosine_similarity(
    vec1: dict[str, float],
    vec2: dict[str, float],
) -> float:
    """
    Compute cosine similarity between two sparse vectors.
    """
    if not vec1 or not vec2:
        return 0.0

    common_terms = set(vec1.keys()) & set(vec2.keys())
    if not common_terms:
        return 0.0

    dot_product = sum(vec1[t] * vec2[t] for t in common_terms)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return dot_product / (norm1 * norm2)


def retrieve_documents(
    query_tokens: list[str],
    inverted_index: dict[str, dict[str, int]],
    tokenized_docs: dict[str, list[str]],
    idf: dict[str, float],
    top_k: int = 100,
) -> list[tuple[str, float]]:
    """
    Retrieve documents ranked by TF-IDF cosine similarity.
    Returns list of (doc_id, score) sorted by score descending.
    """
    if not query_tokens:
        return []

    query_vector = compute_tf_idf_vector(query_tokens, idf)
    if not query_vector:
        return []

    scores: list[tuple[str, float]] = []
    for doc_id, doc_tokens in tokenized_docs.items():
        doc_vector = compute_tf_idf_vector(doc_tokens, idf)
        score = cosine_similarity(query_vector, doc_vector)
        if score > 0.0:
            scores.append((doc_id, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def compute_ap(rankings: list[str], relevant_docs: set[str]) -> float:
    """
    Compute Average Precision for a single query.

    Args:
        rankings: list of doc_ids in ranked order (retrieved results)
        relevant_docs: set of relevant doc_ids from qrels

    Returns:
        Average Precision score (0.0 if no relevant docs or no retrieval)
    """
    if not relevant_docs or not rankings:
        return 0.0

    hits = 0
    precision_sum = 0.0

    for rank, doc_id in enumerate(rankings, start=1):
        if doc_id in relevant_docs:
            hits += 1
            precision_sum += hits / rank

    return precision_sum / len(relevant_docs)


def compute_map(
    rankings: dict[str, list[str]],
    qrels: dict[str, set[str]],
) -> tuple[dict[str, float], float]:
    """
    Compute Mean Average Precision.

    Args:
        rankings: dict of query_id -> list of doc_ids in ranked order
        qrels: dict of query_id -> set of relevant doc_ids

    Returns:
        (per_query_ap, overall_map)
        per_query_ap: dict of query_id -> AP score
        overall_map: mean of all AP scores
    """
    per_query_ap: dict[str, float] = {}

    for query_id, relevant_docs in qrels.items():
        if query_id in rankings:
            ap = compute_ap(rankings[query_id], relevant_docs)
        else:
            ap = 0.0
        per_query_ap[query_id] = ap

    if not per_query_ap:
        return per_query_ap, 0.0

    overall_map = sum(per_query_ap.values()) / len(per_query_ap)
    return per_query_ap, overall_map


def normalize_doc_id(raw_id: str) -> str:
    """
    Normalize document/query ID to match qrels format.
    Qrels uses numeric IDs like "1", "2", etc.
    Parser produces "DOC001", "DOC002", etc.
    """
    if raw_id.startswith("DOC"):
        return str(int(raw_id[3:]))
    return raw_id


def normalize_to_doc_format(raw_id: str) -> str:
    """
    Normalize numeric ID to DOC### format used by parser.
    """
    try:
        num = int(raw_id)
        return f"DOC{num:03d}"
    except ValueError:
        return raw_id


def run_experiment(
    docs_path: str = "data/cisi.all",
    queries_path: str = "data/query.text",
    qrels_path: str = "data/qrels.text",
    top_k: int = 100,
    expansion_top_n: int = 5,
    stemming: bool = True,
    remove_stopword: bool = True,
    use_expansion: bool = True,
) -> dict:
    """
    Run IR experiment comparing original vs expanded queries.

    Returns dict with:
        - map_original: overall MAP for original queries
        - map_expanded: overall MAP for expanded queries
        - per_query_ap_original: per-query AP for original
        - per_query_ap_expanded: per-query AP for expanded
        - rankings_original: per-query rankings for original
        - rankings_expanded: per-query rankings for expanded
        - qrels: parsed qrels
        - num_queries: number of queries evaluated
        - num_docs: number of documents in collection
    """
    # Parse data
    docs = parse_text(Path(docs_path).read_text(encoding="utf-8", errors="ignore"))
    queries = parse_queries(queries_path)
    qrels = parse_qrels(qrels_path)

    # Build index
    inverted_index, tokenized_docs = build_index_for_retrieval(
        docs, stemming, remove_stopword
    )
    idf = compute_idf(inverted_index, len(tokenized_docs))

    # Run retrieval for each query
    rankings_original: dict[str, list[str]] = {}
    rankings_expanded: dict[str, list[str]] = {}

    for query_id, query_text in queries.items():
        q_id_normalized = normalize_doc_id(query_id)

        # Only evaluate queries that have qrels
        if q_id_normalized not in qrels:
            continue

        # Original query
        original_tokens = preprocess(query_text, stemming, remove_stopword)
        original_results = retrieve_documents(
            original_tokens, inverted_index, tokenized_docs, idf, top_k
        )
        rankings_original[q_id_normalized] = [doc_id for doc_id, _ in original_results]

        # Expanded query
        if use_expansion:
            try:
                expanded_terms = get_expanded_query_terms(
                    original_tokens, top_n=expansion_top_n, expand_all=False
                )
            except RuntimeError:
                expanded_terms = original_tokens
        else:
            expanded_terms = original_tokens

        expanded_results = retrieve_documents(
            expanded_terms, inverted_index, tokenized_docs, idf, top_k
        )
        rankings_expanded[q_id_normalized] = [doc_id for doc_id, _ in expanded_results]

    # Compute MAP
    per_query_ap_original, map_original = compute_map(rankings_original, qrels)
    per_query_ap_expanded, map_expanded = compute_map(rankings_expanded, qrels)

    return {
        "map_original": map_original,
        "map_expanded": map_expanded,
        "per_query_ap_original": per_query_ap_original,
        "per_query_ap_expanded": per_query_ap_expanded,
        "rankings_original": rankings_original,
        "rankings_expanded": rankings_expanded,
        "qrels": qrels,
        "num_queries": len(qrels),
        "num_docs": len(tokenized_docs),
    }


def format_report(results: dict) -> str:
    """
    Format experiment results into a readable report string.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("INFORMATION RETRIEVAL EVALUATION REPORT")
    lines.append("Mean Average Precision (MAP) Analysis")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"Collection size: {results['num_docs']} documents")
    lines.append(f"Queries evaluated: {results['num_queries']}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("OVERALL RESULTS")
    lines.append("-" * 60)
    lines.append(f"MAP (Original Queries) : {results['map_original']:.4f}")
    lines.append(f"MAP (Expanded Queries) : {results['map_expanded']:.4f}")

    if results['map_original'] > 0:
        change = (
            (results['map_expanded'] - results['map_original'])
            / results['map_original']
            * 100
        )
        lines.append(f"Change                 : {change:+.2f}%")
    lines.append("")

    lines.append("-" * 60)
    lines.append("PER-QUERY RESULTS")
    lines.append("-" * 60)
    lines.append(f"{'Query':<8} {'AP Original':<14} {'AP Expanded':<14} {'Relevant':<10}")
    lines.append("-" * 46)

    qrels = results['qrels']
    per_orig = results['per_query_ap_original']
    per_exp = results['per_query_ap_expanded']

    for q_id in sorted(qrels.keys(), key=lambda x: int(x)):
        ap_orig = per_orig.get(q_id, 0.0)
        ap_exp = per_exp.get(q_id, 0.0)
        num_rel = len(qrels[q_id])
        lines.append(f"{q_id:<8} {ap_orig:<14.4f} {ap_exp:<14.4f} {num_rel:<10}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    return "\n".join(lines)


def write_report(results: dict, output_path: str = "map_report.txt") -> None:
    """
    Write experiment report to file.
    """
    report = format_report(results)
    Path(output_path).write_text(report, encoding="utf-8")


def main() -> None:
    """
    Run the full evaluation experiment and write results.
    
    Note: Query expansion requires Word2Vec model initialization.
    To enable expansion, initialize the engine before calling run_experiment:
        from src.word2vec_engine import init_engine
        init_engine()
    Then set use_expansion=True in run_experiment().
    """
    print("Running IR evaluation experiment...")

    # Run without expansion by default (Word2Vec model not loaded)
    results = run_experiment(
        docs_path="data/cisi.all",
        queries_path="data/query.text",
        qrels_path="data/qrels.txt",
        top_k=100,
        expansion_top_n=5,
        use_expansion=False,
    )

    # Write report
    write_report(results, "map_report.txt")

    # Print summary
    print(f"MAP (Original) : {results['map_original']:.4f}")
    print(f"MAP (Expanded) : {results['map_expanded']:.4f}")
    print(f"Report written to: map_report.txt")


if __name__ == "__main__":
    main()
