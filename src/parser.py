from __future__ import annotations

from pathlib import Path
import re

_TAGS_WITH_TEXT = {"T", "A", "W"}


def parse_docs(file_path: str) -> dict[str, str]:
    """
    Parse documents from a file path and return a dict of doc_id -> content.
    """
    raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    return parse_text(raw)


def parse_text(raw: str) -> dict[str, str]:
    """
    Parse documents from raw text and return a dict of doc_id -> content.
    """
    docs: dict[str, str] = {}

    current_id: str | None = None
    current_lines: list[str] = []
    current_tag: str | None = None

    for line in raw.splitlines():
        line = line.rstrip("\n")

        if line.startswith(".I "):
            _finalize_doc(docs, current_id, current_lines)
            current_id = _normalize_doc_id(line[3:].strip())
            current_lines = []
            current_tag = None
            continue

        if line.startswith("."):
            tag = line[1:2] if len(line) >= 2 else ""
            current_tag = tag if tag in _TAGS_WITH_TEXT else None
            continue

        if current_id is None:
            continue

        if current_tag in _TAGS_WITH_TEXT:
            current_lines.append(line.strip())

    _finalize_doc(docs, current_id, current_lines)
    return docs


def _finalize_doc(docs: dict[str, str], doc_id: str | None, lines: list[str]) -> None:
    """
    Normalize document content and add it to the docs dict.
    """
    if doc_id is None:
        return
    content = _normalize_content(lines)
    docs[doc_id] = content


def _normalize_doc_id(raw_id: str) -> str:
    """
    Normalize raw document ID to the format DOC###.
    """
    raw_id = raw_id.strip()
    if raw_id.isdigit():
        normalized = str(int(raw_id))
        if len(normalized) <= 3:
            normalized = normalized.zfill(3)
        return f"DOC{normalized}"
    return f"DOC{raw_id}"


def _normalize_content(lines: list[str]) -> str:
    """
    Normalize document content by joining lines, collapsing whitespace, and stripping.
    """
    text = " ".join(part for part in lines if part)
    text = re.sub(r"\s+", " ", text).strip()
    return text

