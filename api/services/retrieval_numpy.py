# api/services/retrieval_numpy.py
from pathlib import Path
import json
import yaml
import numpy as np
from functools import lru_cache
import os  # ✅ add

CFG_PATH = Path("clarity_clean_analysis/04_configs/augury.local.yaml")


@lru_cache(maxsize=1)
def _cfg():
    return yaml.safe_load(CFG_PATH.read_text())


@lru_cache(maxsize=1)
def _index():
    cfg = _cfg()
    X = np.load(cfg["paths"]["index"])  # normalized matrix (index.npy)
    with Path(cfg["paths"]["id_map"]).open("r", encoding="utf-8") as f:
        id_map = {int(k): v for k, v in json.load(f).items()}
    cid2text = {}
    with Path(cfg["paths"]["corpus"]).open("r", encoding="utf-8") as f:
        for line in f:
            j = json.loads(line)
            cid2text[j["chunk_id"]] = j["content"]
    return X, id_map, cid2text


@lru_cache(maxsize=1)
def _embedder():
    """
    Lazy, CI-safe embedder:
    - If EMBEDDER_BACKEND=dummy or sentence_transformers is missing → use a tiny dummy.
    - Otherwise load SentenceTransformer(model) locally.
    """
    backend = os.getenv("EMBEDDER_BACKEND", "st").lower()
    if backend == "dummy":

        class Dummy:
            def encode(self, arr):
                dim = int(_cfg()["embeddings"]["dim"])
                v = np.zeros((1, dim), dtype="float32")
                v[0, 0] = 1.0  # simple unit vector for stable sims
                return v

        return Dummy()
    try:
        from sentence_transformers import SentenceTransformer  # lazy import ✅

        return SentenceTransformer(_cfg()["embeddings"]["model"])
    except Exception:
        # Auto-fallback in CI where the lib isn't installed
        class Dummy:
            def encode(self, arr):
                dim = int(_cfg()["embeddings"]["dim"])
                v = np.zeros((1, dim), dtype="float32")
                v[0, 0] = 1.0
                return v

        return Dummy()


@lru_cache(maxsize=512)
def _ask_cached(q_norm: str, k: int):
    X, id_map, cid2text = _index()
    emb = _embedder()
    q = emb.encode([q_norm])[0].astype("float32")
    q /= np.linalg.norm(q) + 1e-12
    sims = X @ q
    idxs = np.argsort(-sims)[:k].tolist()
    # tuples are fine to cache
    return tuple((id_map[i], float(sims[i]), cid2text[id_map[i]]) for i in idxs)


def _normalize_q(s: str) -> str:
    return " ".join(s.strip().split()).lower()


def ask_numpy(query: str, k: int = 5):
    qn = _normalize_q(query)
    res = _ask_cached(qn, k)
    return [
        {"chunk_id": cid, "score": score, "text": text} for (cid, score, text) in res
    ]


def ask_numpy_with_stats(query: str, k: int = 5):
    """Run ask with cache stats before/after to reveal hit/miss deltas."""
    before = _ask_cached.cache_info()
    res = ask_numpy(query, k)  # uses the cached path
    after = _ask_cached.cache_info()
    stats = {
        "hits_total": after.hits,
        "misses_total": after.misses,
        "hit_delta": after.hits - before.hits,
        "miss_delta": after.misses - before.misses,
        "cache_size": after.currsize,
    }
    return res, stats
