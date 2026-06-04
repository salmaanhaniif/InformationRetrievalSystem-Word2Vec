from __future__ import annotations

from collections import Counter
import json
import pickle
from pathlib import Path

from src.preprocessor import preprocess

DEFAULT_STEMMING = True
DEFAULT_REMOVE_STOPWORD = True


def build_index(docs: dict[str, str], stemming: bool = DEFAULT_STEMMING, remove_stopword: bool = DEFAULT_REMOVE_STOPWORD) -> dict[str, dict]:
    """
    Build an inverted index from a dict of doc_id -> content.
    """
    index: dict[str, dict] = {}

    for doc_id, content in docs.items():
        tokens = preprocess(content, stemming, remove_stopword)
        if not tokens:
            continue

        term_counts = Counter(tokens)

        for term, count in term_counts.items():
            entry = index.get(term)
            if entry is None:
                entry = {"df": 0, "postings": {}}
                index[term] = entry

            postings = entry["postings"]
            postings[doc_id] = count
            entry["df"] = len(postings)

    return index


def save_index(index: dict[str, dict], file_path: str) -> None:
    """
    Save inverted index to JSON or Pickle based on file extension.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(index, ensure_ascii=True, indent=2), encoding="utf-8")
        return

    if suffix in {".pkl", ".pickle"}:
        with path.open("wb") as f:
            pickle.dump(index, f)
        return

    raise ValueError("Unsupported index format. Use .json or .pkl")


def load_index(file_path: str) -> dict[str, dict]:
    """
    Load inverted index from JSON or Pickle based on file extension.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))

    if suffix in {".pkl", ".pickle"}:
        with path.open("rb") as f:
            return pickle.load(f)

    raise ValueError("Unsupported index format. Use .json or .pkl")


def get_document_terms(index: dict[str, dict], doc_id: str) -> list[dict[str, int | str]]:
    """
    Retrieve all indexed terms for a specific document sorted by term.
    """
    terms: list[dict[str, int | str]] = []

    for term, entry in index.items():
        postings = entry.get("postings", {})
        if doc_id in postings:
            terms.append({"term": term, "tf": postings[doc_id]})

    terms.sort(key=lambda item: item["term"])
    return terms
