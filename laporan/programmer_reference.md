# Programmer's Reference
## Information Retrieval System - Word2Vec Query Expansion

---

## 1. Overview

Sistem Information Retrieval (IR) dengan fitur Query Expansion menggunakan Word2Vec untuk meningkatkan relevansi hasil pencarian. Sistem ini menggunakan dataset CISI (Collection of Scientific Information) sebagai koleksi dokumen uji.

### Fitur Utama
- TF-IDF based document retrieval
- Word2Vec semantic query expansion
- Mean Average Precision (MAP) evaluation
- REST API dengan FastAPI
- Web frontend (React/Vite)

---

## 2. Team Members

| Role | Nama | File Utama | Tanggung Jawab |
|------|------|------------|----------------|
| Programmer 1 | `Orvin Andika` | `src/preprocessor.py`, `src/parser.py` | Text preprocessing, document parsing |
| Programmer 2 | `Fajar Kurniawan` | `src/indexer.py` | Inverted index construction |
| Programmer 3 | `Salman Hanif` | `src/word2vec_engine.py` | Word2Vec model management |
| Programmer 4 | `Aryo Wisangeni` | `src/query_expansion.py` | Query expansion logic |
| Programmer 5 | `Sabilul Huda` | `src/evaluator.py`, `laporan/` | Evaluation (MAP), laporan |

---

## 3. Project Structure

```
InformationRetrievalSystem-Word2Vec/
├── src/
│   ├── __init__.py
│   ├── preprocessor.py      # Text normalization, tokenization, stemming, stopword removal
│   ├── parser.py            # Parse CISI document format (.I, .T, .A, .W, .B tags)
│   ├── indexer.py           # Build and manage inverted index
│   ├── word2vec_engine.py   # Word2Vec model wrapper (gensim)
│   ├── query_expansion.py   # Semantic query expansion using Word2Vec
│   └── evaluator.py         # MAP computation, experiment runner
├── api/
│   └── main.py              # FastAPI REST API endpoints
├── frontend/                # React/Vite web interface
├── data/
│   ├── cisi.all             # CISI document collection (1460 docs)
│   ├── query.text           # Test queries (112 queries)
│   ├── qrels.text           # Ground truth relevance judgments
│   └── qrels.txt            # Copy of qrels.text for evaluator
├── main.py                  # Entry point
├── pyproject.toml           # Project dependencies
├── map_report.txt           # Evaluation results
└── laporan/
    ├── laporan.docx         # Full project report
    └── programmer_reference.md  # This file
```

---

## 4. Architecture

### Data Flow

```
User Query → Preprocessor → Query Expansion (Word2Vec) → TF-IDF Retrieval → Ranked Results
                                                                              ↓
Document Collection → Parser → Preprocessor → Inverted Index → IDF Computation
```

### Component Interaction

1. **Parser** (`parser.py`)
   - Input: File `.all` format (CISI)
   - Output: `dict[doc_id, content]`
   - Tags: `.I` (ID), `.T` (Title), `.A` (Author), `.W` (Abstract), `.B` (Bibliography)

2. **Preprocessor** (`preprocessor.py`)
   - Input: Raw text string
   - Output: `list[str]` (tokens)
   - Steps: lowercase → remove punctuation → tokenize → remove stopwords → stemming (PorterStemmer)

3. **Indexer** (`indexer.py`)
   - Input: `dict[doc_id, content]`
   - Output: Inverted index `dict[term, dict[doc_id, tf]]`
   - Format: JSON atau Pickle

4. **Word2Vec Engine** (`word2vec_engine.py`)
   - Singleton pattern via `init_engine()` / `get_engine()`
   - Support: Pre-trained model (gensim downloader) atau custom trained model
   - Methods: `get_similar()`, `similarity()`, `is_in_vocab()`

5. **Query Expansion** (`query_expansion.py`)
   - Input: Original query tokens
   - Output: Expanded query terms dengan similarity scores
   - Functions: `expand_query()`, `expand_query_all()`, `get_expanded_query_terms()`

6. **Evaluator** (`evaluator.py`)
   - Input: Rankings, qrels
   - Output: MAP scores, per-query AP
   - Functions: `compute_map()`, `compute_ap()`, `run_experiment()`, `write_report()`

7. **API** (`api/main.py`)
   - FastAPI server
   - Endpoints: `/api/search`, `/api/expand`, `/api/index/{doc_id}`, `/api/map`

---

## 5. Setup & Running

### Prerequisites
- Python 3.13+
- uv (package manager)

### Install Dependencies
```bash
uv sync
```

### Download NLTK Data
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Run API Server
```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Evaluation
```bash
uv run python -m src.evaluator
```

### Run with Query Expansion
```python
from src.word2vec_engine import init_engine
from src.evaluator import run_experiment

init_engine()  # Load Word2Vec model (requires internet, ~1.6GB)
results = run_experiment(use_expansion=True)
```

### Run Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

---

## 6. API Endpoints

### POST `/api/search`
Search dengan query expansion.

**Request:**
```json
{
  "query": "information retrieval",
  "stemming": true,
  "remove_stopword": true,
  "weighting_scheme": "tfidf_cos",
  "top_n": 5,
  "expand_all": false
}
```

**Response:**
```json
{
  "query_original": ["information", "retrieval"],
  "query_expanded": ["information", "retrieval", "indexing", "document", "search"],
  "expansion_terms": [{"term": "indexing", "score": 0.81}],
  "results_original": [{"doc_id": "DOC001", "title": "...", "similarity": 0.95, "rank": 1}],
  "results_expanded": [...],
  "map_original": 0.1791,
  "map_expanded": 0.1791,
  "per_query_map": [...]
}
```

### POST `/api/expand`
Preview expansion terms.

**Request:**
```json
{
  "terms": ["information", "retrieval"],
  "top_n": 5
}
```

**Response:**
```json
[
  {"term": "indexing", "score": 0.81},
  {"term": "document", "score": 0.78}
]
```

### GET `/api/index/{doc_id}`
Get inverted index untuk dokumen tertentu.

### GET `/api/map`
Get MAP evaluation report.

---

## 7. Key Functions Reference

### `src/evaluator.py`

#### `compute_map(rankings, qrels) -> (per_query_ap, overall_map)`
Compute Mean Average Precision.

**Args:**
- `rankings`: `dict[str, list[str]]` - query_id → list of doc_ids (ranked)
- `qrels`: `dict[str, set[str]]` - query_id → set of relevant doc_ids

**Returns:**
- `per_query_ap`: `dict[str, float]` - AP per query
- `overall_map`: `float` - Mean AP across all queries

#### `run_experiment(...) -> dict`
Run full IR experiment.

**Args:**
- `docs_path`: Path to document collection
- `queries_path`: Path to query file
- `qrels_path`: Path to relevance judgments
- `top_k`: Number of documents to retrieve per query
- `expansion_top_n`: Number of expansion terms
- `use_expansion`: Enable/disable query expansion

#### `write_report(results, output_path)`
Write evaluation report to file.

### `src/query_expansion.py`

#### `expand_query(query_terms, top_n=5) -> list[(term, score)]`
Expand query dengan Word2Vec similarity.

#### `get_expanded_query_terms(query_terms, top_n=5, expand_all=False) -> list[str]`
Get combined original + expanded terms.

### `src/word2vec_engine.py`

#### `init_engine(model_name, local_path, binary) -> Word2VecEngine`
Initialize singleton engine.

#### `get_engine() -> Word2VecEngine`
Get initialized engine instance.

#### `Word2VecEngine.get_similar(term, top_n) -> list[(word, score)]`
Get semantically similar terms.

---

## 8. Data Formats

### CISI Document Format (`.all`)
```
.I 1
.T
Document Title
.A
Author Name
.W
Abstract text here...
.B
(Bibliography)
```

### Qrels Format (TREC)
```
query_id iter doc_id relevance
```
Contoh: `1 0 28 0` (query 1, doc 28, relevance 0)

**Note:** CISI qrels menggunakan binary relevance - presence in file means relevant.

### Query Format
Sama dengan document format, menggunakan `.I` dan `.W` tags.

---

## 9. Evaluation Metrics

### Average Precision (AP)
```
AP = (1/|R|) * Σ (Precision@k * rel(k))
```
dimana |R| = number of relevant documents, rel(k) = 1 jika doc@k relevant.

### Mean Average Precision (MAP)
```
MAP = (1/|Q|) * Σ AP(q)
```
dimana |Q| = number of queries.

---

## 10. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.136.3 | REST API framework |
| gensim | >=4.4.0 | Word2Vec model |
| nltk | >=3.9.4 | Tokenization, stopwords, stemming |
| pysastrawi | >=1.2.1 | Indonesian stemmer (optional) |
| pytest | >=9.0.3 | Testing framework |
| uvicorn | >=0.48.0 | ASGI server |
| python-multipart | >=0.0.30 | Form data parsing |

---

## 11. Testing

### Run Tests
```bash
uv run pytest
```

### Test Structure (Recommended)
```
tests/
├── test_preprocessor.py
├── test_parser.py
├── test_indexer.py
├── test_query_expansion.py
├── test_evaluator.py
└── test_api.py
```

---

## 12. Code Conventions

### Naming
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Type Hints
- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward references

### Docstrings
- Google style docstrings
- Include Args, Returns, Raises sections

---

## 13. Troubleshooting

### Word2Vec Model Download Slow
- Model `word2vec-google-news-300` ~1.6GB
- Download sekali saja, kemudian cache di `~/gensim-data/`
- Alternatif: Train model sendiri dengan `Word2VecEngine.train()`

### NLTK Data Not Found
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Empty Query Results
- Pastikan preprocessing menghasilkan tokens
- Cek apakah terms ada di vocabulary Word2Vec
- Verifikasi inverted index tidak kosong

---

## 14. Future Improvements

- [ ] Implement relevance feedback (Rocchio)
- [ ] Add BM25 ranking
- [ ] Support for other datasets (Cranfield, Medline)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Unit tests coverage > 80%
- [ ] Performance optimization (index caching)

---

*Last updated: June, 3 2026*
*Version: 0.1.0*
