import math
import pickle
from functools import lru_cache
from gensim.models import KeyedVectors, Word2Vec
from pathlib import Path
import gensim.downloader as api

DEFAULT_MODEL_PATH = "models/word2vec.model"
CACHE_PATH = "output/expansion_cache.pkl"

class Word2VecEngine:
    """
    Wrapper Word2Vec model untuk keperluan query expansion.
    """

    def __init__(self):
        self.model = None
        self.model_path = None
        self._loaded = False
        self._disk_cache = {}

    def load_pretrained_from_gensim(self, model_name = "word2vec-google-news-300") -> None:
        self.model      = api.load(model_name)
        if hasattr(self.model, 'fill_norms'):
            self.model.fill_norms()
        self._loaded    = True
        self.model_path = model_name
        self._load_disk_cache()

    def _load_disk_cache(self):
        """Muat persistent memory (disk cache) supaya restart server cepat."""
        if Path(CACHE_PATH).exists():
            try:
                with open(CACHE_PATH, "rb") as f:
                    self._disk_cache = pickle.load(f)
            except Exception:
                self._disk_cache = {}

    def save_disk_cache(self):
        """Simpan cache yang sudah dipelajari kembali ke disk."""
        Path(CACHE_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(self._disk_cache, f)

    def train(
        self,
        tokenized_docs: list[list[str]],
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 2,
        workers: int = 4,
        epochs: int = 10,
        save_path: str = DEFAULT_MODEL_PATH,
    ) -> None:
        if not tokenized_docs:
            raise ValueError("tokenized_docs kosong, tidak bisa training.")

        w2v = Word2Vec(
            sentences=tokenized_docs,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=workers,
            epochs=epochs,
        )

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        w2v.save(save_path)

        self.model = w2v.wv
        if hasattr(self.model, 'fill_norms'):
            self.model.fill_norms()
        self.model_path = save_path
        self._loaded = True
        self._load_disk_cache()

    def _get_similar_internal(self, term: str) -> list[tuple[str, float]]:
        self._check_loaded()

        if term in self._disk_cache:
            return self._disk_cache[term]

        if not self.is_in_vocab(term):
            self._disk_cache[term] = []
            return []

        try:
            raw = self.model.most_similar(term, topn=150)
            results = []
            for word, score in raw:
                if not word.islower():
                    continue
                if '_' in word:
                    continue
                if len(word) < 3:
                    continue
                if term in word or word in term:
                    continue
                if len(word) > 20:
                    continue
                results.append((word, score))

            self._disk_cache[term] = results
            return results
        except Exception:
            self._disk_cache[term] = []
            return []

    def get_similar(self, term: str, top_n: int = 10) -> list[tuple[str, float]]:
        term = term.lower().strip()
        results = self._get_similar_internal(term)
        return results[:top_n]

    def similarity(self, term1: str, term2: str) -> float:
        self._check_loaded()
        if not self.is_in_vocab(term1) or not self.is_in_vocab(term2):
            return 0.0
        try:
            return float(self.model.similarity(term1, term2))
        except Exception:
            return 0.0

    def is_in_vocab(self, term: str) -> bool:
        self._check_loaded()
        return term.lower().strip() in self.model

    def get_vocab_size(self) -> int:
        self._check_loaded()
        return len(self.model)

    def _check_loaded(self) -> None:
        if not self._loaded or self.model is None:
            raise RuntimeError("Model belum di-load.")

_engine_instance: Word2VecEngine | None = None

def get_engine() -> Word2VecEngine:
    if _engine_instance is None:
        raise RuntimeError("Engine belum diinisialisasi.")
    return _engine_instance

def init_engine(
    model_name: str = "word2vec-google-news-300",
    local_path: str = None,
    binary: bool = False,
) -> Word2VecEngine:
    global _engine_instance
    _engine_instance = Word2VecEngine()

    if local_path:
        _engine_instance.model = KeyedVectors.load_word2vec_format(local_path, binary=binary)
        if hasattr(_engine_instance.model, 'fill_norms'):
            _engine_instance.model.fill_norms()
        _engine_instance._loaded = True
        _engine_instance.model_path = local_path
        _engine_instance._load_disk_cache()
    else:
        _engine_instance.load_pretrained_from_gensim(model_name)

    return _engine_instance