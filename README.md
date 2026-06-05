# Information Retrieval System with Word2Vec Query Expansion

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.13+-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python Version" />
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.136+-009688.svg?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
  </a>
  <a href="https://radimrehurek.com/gensim/">
    <img src="https://img.shields.io/badge/Gensim-4.4+-B8860B.svg?style=flat" alt="Gensim" />
  </a>
  <a href="https://www.nltk.org/">
    <img src="https://img.shields.io/badge/NLTK-3.9+-003366.svg?style=flat" alt="NLTK" />
  </a>
  <a href="https://react.dev/">
    <img src="https://img.shields.io/badge/React-19.2+-61DAFB.svg?style=flat&logo=react&logoColor=black" alt="React" />
  </a>
  <a href="https://www.typescriptlang.org/">
    <img src="https://img.shields.io/badge/TypeScript-6.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white" alt="TypeScript" />
  </a>
  <a href="https://vite.dev/">
    <img src="https://img.shields.io/badge/Vite-8.0+-646CFF.svg?style=flat&logo=vite&logoColor=white" alt="Vite" />
  </a>
  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS-4.3+-06B6D4.svg?style=flat&logo=tailwindcss&logoColor=white" alt="TailwindCSS" />
  </a>
</p>

## Description

This application implements an **Information Retrieval (IR) System** using the Vector Space Model (VSM) and integrates a **Word2Vec Query Expansion** engine. Users can query a collection of documents using standard search terms, and the system automatically suggests semantically similar terms to broaden the search query, retrieving more relevant documents that do not necessarily contain the exact original keywords.

### How it Works:
1. **Document Preprocessing**: Texts are normalized (lowercased, punctuation removed), tokenized, and optionally filtered for stopwords (NLTK stopwords) and stemmed (NLTK Porter Stemmer).
2. **Indexing**: An inverted index is constructed dynamically based on the active preprocessing settings.
3. **Weighting Schemes**: Supports 7 different TF-IDF weighting schemes:
   - `tf_raw` (Raw term frequency)
   - `tf_log` (Logarithmic term frequency)
   - `tf_bin` (Binary term frequency)
   - `tf_aug` (Augmented term frequency)
   - `idf` (Inverse document frequency)
   - `tfidf` (Standard TF-IDF)
   - `tfidf_cos` (TF-IDF with Cosine Normalization)
4. **Query Expansion (Word2Vec)**: Leverages a 300-dimension Google News pre-trained Word2Vec model. It extracts the top-N semantically similar terms using cosine similarity in the vector space, filters out noise (lowercase filter, length check, subword duplicates), and appends them to the search query.
5. **Retrieval & Side-by-Side Comparison**: Searches the index using both the original and expanded queries. The frontend displays the results side-by-side, highlighting documents whose rankings improved as a result of query expansion.
6. **MAP (Mean Average Precision) Evaluation**: Performs offline benchmarks evaluating all 112 queries against relevance judgments (`qrels`) for **28 combinations** of parameters (2 stemming states × 2 stopword states × 7 weighting schemes). Shows exact Average Precision (AP) per query.

### System Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend (React + Vite + TypeScript)"]
        UI["SearchPage.tsx\n• ParameterPanel (sidebar)\n• SearchBar (input)\n• TabBar (Results/Expansion/MAP)\n• ResultsTab (side-by-side comparison)\n• ExpansionTab (term pills + score table)\n• MapReportTab (metric cards + per-query table)\n• Dark mode toggle"]
    end

    subgraph API["Backend API (FastAPI)"]
        API_MAIN["api/main.py\n\nEndpoints:\n• POST /api/search\n• POST /api/expand\n• GET /api/index/{doc_id}\n• GET /api/map\n• POST /api/index/rebuild\n• POST /api/map/recalculate/single\n• POST /api/map/recalculate/all\n\nFeatures:\n• SystemState cache (docs, indices, MAP)\n• MAP cache persistence (pickle)\n• Index cache per preprocessing config\n• Benchmark loop (28 variations)"]
    end

    subgraph Core["Core Modules (src/)"]
        direction TB

        PARSER["parser.py\n• parse_docs() - parse CISI file\n• parse_text() - parse raw string\n• Tags: .I .T .A .W .B\n• Output: dict[doc_id, content]"]

        PREPROC["preprocessor.py\n• preprocess()\n• _normalize_text() - lowercase, regex\n• _tokenize() - split on space\n• _remove_stopwords() - NLTK\n• _stem_tokens() - PorterStemmer"]

        INDEXER["indexer.py\n• build_index() - inverted index\n• save_index() - JSON/Pickle\n• load_index()\n• get_document_terms()"]

        WEIGHTING["weighting.py\n• get_weight() - term weight per scheme\n• get_n_docs() - collection size\n• 7 schemes: tf_raw, tf_log,\n  tf_bin, tf_aug, idf, tfidf, tfidf_cos"]

        RETRIEVAL["retrieval.py\n• rank_documents() - cosine similarity\n• compute_query_weight()\n• Uses weighting.py for TF-IDF\n• Returns sorted (doc_id, score)"]

        W2V_ENGINE["word2vec_engine.py\n• Word2VecEngine class\n• init_engine() - singleton\n• get_engine()\n• get_similar() - with 5 filters\n• similarity()\n• train() - custom model\n• save_disk_cache()"]

        QEXPAND["query_expansion.py\n• expand_query() - top_n terms\n• expand_query_all() - unlimited\n• get_expanded_query_terms()\n• format_expansion_detail()"]

        EVALUATOR["evaluator.py\n• parse_qrels() - auto-detect format\n• parse_queries()\n• compute_ap() - per query\n• compute_map() - overall\n• run_experiment() - full benchmark\n• format_report() / write_report()"]
    end

    subgraph Data["Data Layer"]
        CISI["data/cisi.all\n1460 documents"]
        QUERY["data/query.text\n112 test queries"]
        QRELS["data/qrels.txt\n76 queries with qrels\n(binary relevance)"]
        IDX_CACHE["output/index_*.pkl\nCached inverted indices\n(per stemming/stopword config)"]
        MAP_CACHE["output/map_cache.pkl\nCached MAP results\n(28 variations)"]
        W2V_MODEL["word2vec-google-news-300\n~1.6GB, 3M vocab, 300 dim"]
    end

    %% Client to API
    UI -->|HTTP POST /api/search| API_MAIN
    UI -->|HTTP POST /api/expand| API_MAIN
    UI -->|HTTP GET /api/map| API_MAIN
    UI -->|"HTTP GET /api/index/{doc_id}"| API_MAIN

    %% API to Core
    API_MAIN --> PARSER
    API_MAIN --> PREPROC
    API_MAIN --> INDEXER
    API_MAIN --> WEIGHTING
    API_MAIN --> RETRIEVAL
    API_MAIN --> W2V_ENGINE
    API_MAIN --> QEXPAND
    API_MAIN --> EVALUATOR

    %% Core flows
    PARSER -->|"dict[doc_id, content]"| PREPROC
    PREPROC -->|"list[tokens]"| INDEXER
    PREPROC -->|query tokens| QEXPAND
    PREPROC -->|query tokens| RETRIEVAL
    INDEXER -->|inverted index| WEIGHTING
    INDEXER -->|inverted index| RETRIEVAL
    WEIGHTING -->|term weights| RETRIEVAL
    QEXPAND -->|expanded terms| RETRIEVAL
    W2V_ENGINE -->|similar words| QEXPAND
    RETRIEVAL -->|ranked doc_ids| EVALUATOR

    %% Data connections
    CISI -->|read| PARSER
    QUERY -->|read| EVALUATOR
    QRELS -->|read| EVALUATOR
    IDX_CACHE -.->|load/save| INDEXER
    MAP_CACHE -.->|load/save| API_MAIN
    W2V_MODEL -.->|load| W2V_ENGINE
```

---

## Table of Contents

1. [Description](#description)
2. [Setup & Dependencies](#setup--dependencies)
   - [Prerequisites](#prerequisites)
   - [Backend Installation](#1-backend-installation)
   - [Frontend Installation](#2-frontend-installation)
3. [How to Run](#how-to-run)
   - [Running the Backend API Server](#1-running-the-backend-api-server)
   - [Running the Frontend Dev Server](#2-running-the-frontend-dev-server)
   - [Running CLI Experiments/Evaluator](#3-running-cli-experiments-evaluator)
4. [Creators](#creators)

---

## Setup & Dependencies

### Prerequisites
- **Python 3.13+** installed.
- **Node.js 18+** installed.
- Recommended Python package manager: **`uv`** (Astral's fast Python packaging tool).

---

### 1. Backend Installation

1. Clone this repository and navigate to the project directory:
   ```bash
   git clone https://github.com/salmaanhaniif/InformationRetrievalSystem-Word2Vec.git
   cd InformationRetrievalSystem-Word2Vec
   ```

2. Sync/install Python dependencies:
   * Using `uv` (recommended):
     ```bash
     uv sync
     ```
   * Using `pip` (alternative):
     ```bash
     pip install -r requirements.txt
     ```

3. **CRITICAL STEP**: Download the NLTK stopword corpora:
   * Using `uv`:
     ```bash
     uv run python -c "import nltk; nltk.download('stopwords')"
     ```
   * Using standard Python:
     ```bash
     python -c "import nltk; nltk.download('stopwords')"
     ```

---

### 2. Frontend Installation

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Return to the root folder:
   ```bash
   cd ..
   ```

---

## How to Run

Running the application requires launching both the **Backend API Server** and the **Frontend React Client**.

### 1. Running the Backend API Server

Open a terminal at the project root and run:
* Using `uv`:
  ```bash
  uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
  ```
* Using standard python:
  ```bash
  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
  ```

> [!NOTE]
> **First Run Behaviour:**
> - The backend will automatically download the ~1.6 GB pre-trained `word2vec-google-news-300` model using Gensim API if it is not already present.
> - The server will automatically perform benchmark calculations for all 28 parameter combinations (which takes a few minutes).
> - All results and index matrices are saved in `output/` so that subsequent startups are nearly instantaneous.

You can inspect the backend API docs via Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### 2. Running the Frontend Dev Server

Open a second terminal window, navigate to the `frontend/` directory, and start the development server:
```bash
cd frontend
npm run dev
```

Open your web browser and go to **[http://localhost:5173](http://localhost:5173)** to interact with the search panel, adjust weights/stemming, and inspect MAP reports.

---

### 3. Running CLI Experiments / Evaluator

To run the offline evaluator directly in the console and export the evaluation metrics without launching the web application:
* Using `uv`:
  ```bash
  uv run python -m src.evaluator
  ```
* Using standard python:
  ```bash
  python -m src.evaluator
  ```

This outputs a summary of Mean Average Precision (MAP) metrics and writes a complete breakdown report per query to `map_report.txt`.

---

## Creators

<table>
    <tr align="left">
        <td><b>NIM</b></td>
        <td><b>Name</b></td>
        <td align="center"><b>GitHub</b></td>
    </tr>
    <tr align="left">
        <td>13523017</td>
        <td>Orvin Andika Ikhsan Abhista</td>
        <td align="center" >
            <div style="margin-right: 20px;">
            <a href="https://github.com/orvin14" >
                <img src="https://avatars.githubusercontent.com/u/165545664?v=4" width="48px;" alt=""/> 
                <br/> <sub><b> @orvin14 </b></sub>
            </a><br/>
            </div>
        </td>
    </tr>
    <tr align="left">
        <td>13523100</td>
        <td>Aryo Wisanggeni</td>
        <td align="center" >
            <div style="margin-right: 20px;">
            <a href="https://github.com/Staryo40" >
                <img src="https://avatars.githubusercontent.com/u/139449070?v=4" width="48px;" alt=""/> 
                <br/> <sub><b> @Staryo40 </b></sub>
            </a><br/>
            </div>
        </td>
    </tr>
    <tr align="left">
        <td>13523027</td>
        <td>Fajar Kurniawan</td>
        <td align="center" >
            <div style="margin-right: 20px;">
            <a href="https://github.com/Fajar2k5" >
                <img src="https://avatars.githubusercontent.com/u/37618824?v=4" width="48px;" alt=""/> 
                <br/> <sub><b> @Fajar2k5 </b></sub>
            </a><br/>
            </div>
        </td>
    </tr>
    <tr align="left">
        <td>13523056</td>
        <td>Salman Hanif</td>
        <td align="center" >
            <div style="margin-right: 20px;">
            <a href="https://github.com/salmaanhaniif" >
                <img src="https://avatars.githubusercontent.com/u/165023067?v=4" width="48px;" alt=""/> 
                <br/> <sub><b> @salmaanhaniif </b></sub>
            </a><br/>
            </div>
        </td>
    </tr>
    <tr align="left">
        <td>13523072</td>
        <td>Sabilul Huda</td>
        <td align="center" >
            <div style="margin-right: 20px;">
            <a href="https://github.com/bill2247" >
                <img src="https://avatars.githubusercontent.com/u/154667955?v=4" width="48px;" alt=""/> 
                <br/> <sub><b> @bill2247 </b></sub>
            </a><br/>
            </div>
        </td>
    </tr>
</table>
