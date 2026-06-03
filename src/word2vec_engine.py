import math
from functools import lru_cache
from gensim.models import KeyedVectors, Word2Vec
from pathlib import Path
import gensim.downloader as api

DEFAULT_MODEL_PATH = "models/word2vec.model"

class Word2VecEngine:
    """
    Wrapper Word2Vec model untuk keperluan query expansion.
    Mendukung dua mode:
      - load pre-trained model (KeyedVectors atau Word2Vec)
      - train dari koleksi dokumen
    """

    def __init__(self):
        self.model = None
        self.model_path = None
        self._loaded = False

    def load_pretrained_from_gensim(self, model_name = "word2vec-google-news-300") -> None:
        self.model      = api.load(model_name)
        # Fill L2 norms instantly to avoid lazy-loading on first query
        if hasattr(self.model, 'fill_norms'):
            self.model.fill_norms()
        self._loaded    = True
        self.model_path = model_name

    def train(
        self,
        tokenized_docs: list[list[str]],    # list of token lists, output dari preprocessor.py
        vector_size: int = 100,             # dimensi embedding (100-300)
        window: int = 5,                    # ukuran context window
        min_count: int = 2,                 # abaikan kata yang muncul < min_count kali
        workers: int = 4,                   # jumlah thread training
        epochs: int = 10,                   # jumlah epoch training
        save_path: str = DEFAULT_MODEL_PATH,# lokasi simpan model setelah training
    ) -> None:
        """
        Train Word2Vec dari koleksi dokumen yang sudah di-tokenisasi.
        Contoh input tokenized_docs:
            [
                ["information", "retrieval", "system"],
                ["document", "indexing", "inverted"]
            ]
        """
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

        # Simpan model
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        w2v.save(save_path)

        self.model = w2v.wv
        if hasattr(self.model, 'fill_norms'):
            self.model.fill_norms()
        self.model_path = save_path
        self._loaded = True

    @lru_cache(maxsize=10000)
    def _cached_get_similar(self, term: str) -> list[tuple[str, float]]:
        self._check_loaded()

        if not self.is_in_vocab(term):
            return []

        try:
            # Selalu minta jumlah yang besar agar bisa di-slice oleh caller tanpa cache miss
            raw = self.model.most_similar(term, topn=150)

            results = []
            for word, score in raw:
                # Filter 1: lowercase saja — buang proper noun
                if not word.islower():
                    continue
                # Filter 2: buang kata dengan underscore (frasa Google News)
                if '_' in word:
                    continue
                # Filter 3: buang yang terlalu pendek
                if len(word) < 3:
                    continue
                # Filter 4: buang kata yang terlalu mirip dengan input (variasi typo)
                # Kalau kata input ada di dalam kata hasil, kemungkinan besar itu noise
                if term in word or word in term:
                    continue

                # Filter 5: buang kata yang terlalu panjang (gabungan kata tanpa spasi)
                if len(word) > 20:
                    continue

                results.append((word, score))

            return results

        except Exception as e:
            return []

    def get_similar(self, term: str, top_n: int = 10) -> list[tuple[str, float]]:
        """
        Args:
            term  : kata yang dicari kemiripannya (sudah di-preprocess)
            top_n : jumlah kata yang dikembalikan

        Returns:
            list of (word, cosine_similarity_score), sudah diurutkan descending
            Contoh: [("indexing", 0.81), ("document", 0.78), ("search", 0.75)]
        """
        term = term.lower().strip()
        results = self._cached_get_similar(term)
        return results[:top_n]

    
    def similarity(self, term1: str, term2: str) -> float:
        """
        Hitung cosine similarity antara dua kata.
        """
        self._check_loaded()

        if not self.is_in_vocab(term1) or not self.is_in_vocab(term2):
            return 0.0

        try:
            return float(self.model.similarity(term1, term2))
        except Exception:
            return 0.0

    def is_in_vocab(self, term: str) -> bool:
        """Cek apakah kata ada di vocab model."""
        self._check_loaded()
        return term.lower().strip() in self.model

    def get_vocab_size(self) -> int:
        """Kembalikan jumlah kata dalam vocab model."""
        self._check_loaded()
        return len(self.model)

    def _check_loaded(self) -> None:
        if not self._loaded or self.model is None:
            raise RuntimeError(
                "Model belum di-load. Panggil load_pretrained() atau train() dulu."
            )

    def __repr__(self) -> str:
        if self._loaded:
            return f"Word2VecEngine(path='{self.model_path}', vocab={len(self.model)})"
        return "Word2VecEngine(not loaded)"

# SINGLETON — dipakai di queryExpansion.py

_engine_instance: Word2VecEngine | None = None

def get_engine() -> Word2VecEngine:
    """
    Kembalikan instance Word2VecEngine yang sudah di-load.
    Panggil init_engine() dulu sebelum ini.
    """
    if _engine_instance is None:
        raise RuntimeError("Engine belum diinisialisasi. Panggil init_engine() dulu.")
    return _engine_instance

def init_engine(
    model_name: str = "word2vec-google-news-300",
    local_path: str = None,
    binary: bool = False,
) -> Word2VecEngine:
    """
    Inisialisasi engine sekali saja di awal program.

    Contoh — pakai gensim downloader (default):
        init_engine()

    Contoh — pakai file lokal:
        init_engine(local_path="models/custom.model")
        init_engine(local_path="models/GoogleNews.bin", binary=True)
    """
    global _engine_instance
    _engine_instance = Word2VecEngine()

    if local_path:
        _engine_instance.load_pretrained(local_path, binary=binary)
    else:
        _engine_instance.load_pretrained_from_gensim(model_name)

    return _engine_instance