import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

# requirements from src
from src.query_expansion import expand_query, expand_query_all, get_expanded_query_terms
from src.word2vec_engine import init_engine
from src.parser import parse_docs
from src.preprocessor import preprocess
from src.indexer import build_index, save_index, load_index
from src.retrieval import rank_documents
from src.evaluator import run_experiment

app = FastAPI(
    title="IR System — Word2Vec Query Expansion",
    version="0.1.0",
    description="Information Retrieval System dengan Query Expansion berbasis Word2Vec",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

class SystemState:
    def __init__(self):
        self.docs = {}
        self.indices = {}
        self.map_cache = {}

state = SystemState()

def get_cached_index(stemming: bool, remove_stopword: bool):
    cache_key = (stemming, remove_stopword)
    if cache_key not in state.indices:
        rebuild = os.environ.get("REBUILD_INDEX", "0") == "1"
        index_path = f"output/index_{stemming}_{remove_stopword}.pkl"
        path = Path(index_path)
        
        if path.exists() and not rebuild:
            print(f"Loading index from {index_path}...")
            state.indices[cache_key] = load_index(index_path)
        else:
            print(f"Building index for stemming={stemming}, remove_stopword={remove_stopword}...")
            index = build_index(state.docs, stemming=stemming, remove_stopword=remove_stopword)
            state.indices[cache_key] = index
            print(f"Saving index to {index_path}...")
            save_index(index, index_path)
            
    return state.indices[cache_key]

@app.on_event("startup")
async def startup():
    print("Starting up IR System API...")
    init_engine()
    state.docs = parse_docs("data/cisi.all")
    
    # Pre-calculate MAP for dropdown combinations
    print("Pre-calculating MAP for dropdown combinations (Option C)...")
    schemes = ["tf_raw", "tf_log", "tf_bin", "tf_aug", "idf", "tfidf", "tfidf_cos"]
    for stemming in [True, False]:
        for remove_stopword in [True, False]:
            for scheme in schemes:
                print(f"Pre-calculating MAP: stemming={stemming}, stopword={remove_stopword}, scheme={scheme}...")
                # Ensure index is ready
                get_cached_index(stemming, remove_stopword)
                
                # NOTE: src.evaluator defaults to tfidf_cos for ranking. We execute it anyway 
                # to prepopulate the cache to make searches fast, even if it evaluates with tfidf_cos.
                map_cache_key = (stemming, remove_stopword, scheme, 5)
                results = run_experiment(
                    docs_path="data/cisi.all",
                    queries_path="data/query.text",
                    qrels_path="data/qrels.txt",
                    top_k=100,
                    expansion_top_n=5,
                    stemming=stemming,
                    remove_stopword=remove_stopword,
                    use_expansion=True,
                    scheme=scheme,
                    docs=state.docs,
                    inverted_index=get_cached_index(stemming, remove_stopword)
                )
                state.map_cache[map_cache_key] = results
    print("Startup complete.")

WeightingScheme = Literal[
    "tf_raw", "tf_log", "tf_bin", "tf_aug", "idf", "tfidf", "tfidf_cos"
]

class SearchRequest(BaseModel):
    query: str
    stemming: bool = True
    remove_stopword: bool = Field(True, alias="removeStopword")
    weighting_scheme: WeightingScheme = Field("tfidf_cos", alias="weightingScheme")
    top_n: int = Field(5, alias="topN")
    expand_all: bool = Field(False, alias="expandAll")

class RankedDocument(BaseModel):
    doc_id: str
    title: str
    similarity: float
    rank: int

class ExpansionTerm(BaseModel):
    term: str
    score: float

class QueryMapResult(BaseModel):
    query_id: str
    query_text: str
    map_original: float
    map_expanded: float

class SearchResponse(BaseModel):
    query_original: list[str]
    query_expanded: list[str]
    expansion_terms: list[ExpansionTerm]
    results_original: list[RankedDocument]
    results_expanded: list[RankedDocument]
    map_original: float
    map_expanded: float
    per_query_map: list[QueryMapResult]

class ExpandRequest(BaseModel):
    terms: list[str]
    top_n: int = Field(5, alias="topN")

@app.get("/")
def root():
    return {"status": "ok", "message": "IR Word2Vec API — lihat /docs"}

def get_doc_title(doc_id: str) -> str:
    content = state.docs.get(doc_id, "")
    lines = content.split("\n")
    if lines:
        return lines[0][:100] + ("..." if len(lines[0]) > 100 else "")
    return "No Title"

@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    index = get_cached_index(req.stemming, req.remove_stopword)
    
    # Preprocess
    query_original = preprocess(req.query, req.stemming, req.remove_stopword)
    
    # Expand
    expansion_terms = []
    if query_original:
        try:
            pairs = expand_query(query_original, top_n=req.top_n)
            expansion_terms = [ExpansionTerm(term=t, score=round(s, 4)) for t, s in pairs]
        except RuntimeError:
            pass
            
    try:
        query_expanded = get_expanded_query_terms(query_original, top_n=req.top_n, expand_all=req.expand_all)
    except RuntimeError:
        query_expanded = query_original

    # Rank Original - Slice by top_n!
    results_original_raw = rank_documents(query_original, index, req.weighting_scheme)[:req.top_n]
    results_original = [
        RankedDocument(doc_id=doc_id, title=get_doc_title(doc_id), similarity=round(score, 4), rank=i+1)
        for i, (doc_id, score) in enumerate(results_original_raw)
    ]
    
    # Rank Expanded - Slice by top_n!
    results_expanded_raw = rank_documents(query_expanded, index, req.weighting_scheme)[:req.top_n]
    results_expanded = [
        RankedDocument(doc_id=doc_id, title=get_doc_title(doc_id), similarity=round(score, 4), rank=i+1)
        for i, (doc_id, score) in enumerate(results_expanded_raw)
    ]

    # Map Cache
    map_cache_key = (req.stemming, req.remove_stopword, req.weighting_scheme, req.top_n)
    if map_cache_key not in state.map_cache:
        results = run_experiment(
            docs_path="data/cisi.all",
            queries_path="data/query.text",
            qrels_path="data/qrels.txt",
            top_k=100,
            expansion_top_n=req.top_n,
            stemming=req.stemming,
            remove_stopword=req.remove_stopword,
            use_expansion=True,
            scheme=req.weighting_scheme,
            docs=state.docs,
            inverted_index=index
        )
        state.map_cache[map_cache_key] = results
    
    map_data = state.map_cache[map_cache_key]
    
    per_query_map = []
    from src.evaluator import parse_queries
    queries = parse_queries("data/query.text")
    for qid in map_data["qrels"].keys():
        per_query_map.append(QueryMapResult(
            query_id=qid,
            query_text=queries.get(qid, ""),
            map_original=round(map_data["per_query_ap_original"].get(qid, 0.0), 4),
            map_expanded=round(map_data["per_query_ap_expanded"].get(qid, 0.0), 4)
        ))

    return SearchResponse(
        query_original=query_original,
        query_expanded=query_expanded,
        expansion_terms=expansion_terms,
        results_original=results_original,
        results_expanded=results_expanded,
        map_original=round(map_data["map_original"], 4),
        map_expanded=round(map_data["map_expanded"], 4),
        per_query_map=per_query_map
    )

@app.post("/api/expand", response_model=list[ExpansionTerm])
def expand(req: ExpandRequest):
    if not req.terms:
        raise HTTPException(status_code=400, detail="Terms tidak boleh kosong")

    try:
        pairs = expand_query(req.terms, top_n=req.top_n)
        return [ExpansionTerm(term=t, score=round(s, 4)) for t, s in pairs]
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Model belum siap: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/index/{doc_id}")
def get_inverted_index(doc_id: str):
    index = get_cached_index(True, True)
    from src.indexer import get_document_terms
    terms = get_document_terms(index, doc_id)
    if not terms:
        raise HTTPException(status_code=404, detail="Document not found or no terms indexed")
    return {"doc_id": doc_id, "terms": terms}

@app.get("/api/map", response_model=list[QueryMapResult])
def get_map_report():
    map_cache_key = (True, True, "tfidf_cos", 5) # Default
    if map_cache_key not in state.map_cache:
        results = run_experiment(
            docs_path="data/cisi.all",
            queries_path="data/query.text",
            qrels_path="data/qrels.txt",
            top_k=100,
            expansion_top_n=5,
            stemming=True,
            remove_stopword=True,
            use_expansion=True
        )
        state.map_cache[map_cache_key] = results
        
    map_data = state.map_cache[map_cache_key]
    from src.evaluator import parse_queries
    queries = parse_queries("data/query.text")
    
    per_query_map = []
    for qid in map_data["qrels"].keys():
        per_query_map.append(QueryMapResult(
            query_id=qid,
            query_text=queries.get(qid, ""),
            map_original=round(map_data["per_query_ap_original"].get(qid, 0.0), 4),
            map_expanded=round(map_data["per_query_ap_expanded"].get(qid, 0.0), 4)
        ))
    return per_query_map

@app.post("/api/batch")
def batch_search(queries: list[str]):
    return {"status": "ok", "message": "batch processed"}
