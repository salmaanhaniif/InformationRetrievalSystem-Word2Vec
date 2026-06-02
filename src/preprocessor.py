from __future__ import annotations

import re
from typing import Iterable

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


def preprocess(text: str, stemming: bool, remove_stopword: bool) -> list[str]:
    """
    Normalize, tokenize, and optionally remove stopwords and stem tokens.
    """
    if not text:
        return []

    normalized = _normalize_text(text)
    tokens = _tokenize(normalized)

    if remove_stopword:
        tokens = _remove_stopwords(tokens)

    if stemming:
        tokens = _stem_tokens(tokens)

    return tokens


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    return text.split(" ")


def _remove_stopwords(tokens: Iterable[str]) -> list[str]:
    try:
        stops = set(stopwords.words("english"))
    except LookupError:
        stops = set()
    return [token for token in tokens if token and token not in stops]


def _stem_tokens(tokens: Iterable[str]) -> list[str]:
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens if token]

