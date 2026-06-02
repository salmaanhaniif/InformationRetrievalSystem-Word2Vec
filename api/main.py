from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal

# requirements from src
from src.query_expansion import expand_query, expand_query_all
from src.word2vec_engine import init_engine

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


@app.on_event("startup")
async def startup():
    init_engine()

WeightingScheme = Literal[
    "tf_raw", "tf_log", "tf_bin", "tf_aug", "idf", "tfidf", "tfidf_cos"
]

class SearchRequest(BaseModel):
    query: str
    stemming: bool = True
    remove_stopword: bool = True
    weighting_scheme: WeightingScheme = "tfidf_cos"
    top_n: int = 5
    expand_all: bool = False

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
    top_n: int = 5

# Endpoints

@app.get("/")
def root():
    return {"status": "ok", "message": "IR Word2Vec API — lihat /docs"}

@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    pass

@app.post("/api/expand", response_model=list[ExpansionTerm])
def expand(req: ExpandRequest):
    """
    Expand query terms menggunakan Word2Vec.
    Berguna untuk preview expansion sebelum search.
    """
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
    pass


@app.get("/api/map", response_model=list[QueryMapResult])
def get_map_report():
    pass


@app.post("/api/batch")
def batch_search(queries: list[str]):
    pass