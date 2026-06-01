from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IR Word2Vec", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"], #React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "IR Word2Vec API"}

@app.post("/api/search")
def expand():
    return {"mesage" : "mangga mas aryo"}