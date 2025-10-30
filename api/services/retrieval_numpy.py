# api/services/retrieval_numpy.py
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

CFG_PATH = Path("clarity_clean_analysis/04_configs/augury.local.yaml")


@lru_cache(maxsize=1)
def _cfg():
    if not CFG_PATH.exists():
        # CI fallback: minimal config
        return {
            "paths": {"corpus": "", "index": "", "id_map": "", "manifest": ""},
            "embeddings": {"model": "dummy", "dim": 1024, "metric": "cosine"},
        }
    return yaml.safe_load(CFG_PATH.read_text())


@lru_cache(maxsize=1)
def _index():
    cfg = _cfg()
    p_index = cfg["paths"].get("index", "")
    p_idmap = cfg["paths"].get("id_map", "")
    p_corpus = cfg["paths"].get("corpus", "")
    if (
        not p_index
        or not Path(p_index).exists()
        or not p_idmap
        or not Path(p_idmap).exists()
    ):
        # CI fallback: small dummy index (64 rows, exact cosine queries)
        n, d = 64, int(cfg["embeddings"]["dim"])
        X = np.zeros((n, d), dtype="float32")
        X[:, 0] = 1.0
        id_map = {i: f"dummy_{i:05d}" for i in range(n)}
        cid2text = {v: "dummy text" for v in id_map.values()}
        return X, id_map, cid2text
    X = np.load(p_index)
    with Path(p_idmap).open("r", encoding="utf-8") as f:
        id_map = {int(k): v for k, v in json.load(f).items()}
    cid2text = {}
    if p_corpus and Path(p_corpus).exists():
        with Path(p_corpus).open("r", encoding="utf-8") as f:
            for line in f:
                j = json.loads(line)
                cid2text[j["chunk_id"]] = j["content"]
    else:
        cid2text = {v: "text unavailable in CI" for v in id_map.values()}
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
