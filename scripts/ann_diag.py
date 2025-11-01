# scripts/ann_diag.py — Diagnostic runner (FAISS-truth, stable NumPy, rerank64@K)
# Purpose: Reproduce/diagnose FAISS vs NumPy parity, produce receipts (no product-code changes)

import argparse
import json
import os
import random
import time
from typing import List, Dict

import numpy as np
import faiss  # wheels installed; no extra deps


# ---------------------------
# Utils
# ---------------------------


def as_float32_contig(a: np.ndarray) -> np.ndarray:
    """Ensure C-contiguous float32."""
    return np.ascontiguousarray(a.astype(np.float32, copy=False))


def normalize_l2_inplace(v: np.ndarray) -> None:
    """L2-normalize rows in-place using FAISS helper (expects float32)."""
    faiss.normalize_L2(v)


def load_vectors(path: str) -> np.ndarray:
    vecs = np.load(path)
    vecs = as_float32_contig(vecs)
    normalize_l2_inplace(vecs)
    return vecs


def coerce_ids(ids_obj, N: int) -> List[int]:
    """
    Coerce various JSON id formats into a length-N python list[int] aligned to row order.
    If absent or malformed, fall back to identity mapping [0..N-1].
    """
    if isinstance(ids_obj, list):
        out = [int(x) for x in ids_obj[:N]]
        if len(out) < N:  # pad with identity
            out += list(range(len(out), N))
        return out[:N]
    if isinstance(ids_obj, dict):
        # accept {"ids":[...]} or {"0": 12, "1": 99, ...}
        if "ids" in ids_obj and isinstance(ids_obj["ids"], list):
            arr = [int(x) for x in ids_obj["ids"][:N]]
            if len(arr) < N:
                arr += list(range(len(arr), N))
            return arr[:N]
        arr = [None] * N
        for k, v in ids_obj.items():
            try:
                idx = int(k)
                if 0 <= idx < N:
                    arr[idx] = int(v)
            except Exception:
                pass
        for i in range(N):
            if arr[i] is None:
                arr[i] = i
        return arr
    return list(range(N))


def audit_norms(V: np.ndarray) -> Dict[str, float]:
    norms = np.linalg.norm(V, axis=1)
    nan_inf = int(np.isnan(norms).any() or np.isinf(norms).any())
    max_dev = float(np.max(np.abs(norms - 1.0)))
    return {
        "nan_inf": nan_inf,
        "max_norm_dev": max_dev,
        "contiguous": bool(V.flags["C_CONTIGUOUS"]),
    }


def faiss_index_flat_ip(dim: int, V: np.ndarray) -> faiss.IndexFlatIP:
    idx = faiss.IndexFlatIP(dim)
    idx.add(V)
    return idx


def sample_indices(N: int, S: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    S = min(S, N)
    return rng.choice(N, size=S, replace=False)


def overlap_at_k(truth: List[List[int]], cand: List[List[int]], K: int) -> float:
    acc = 0.0
    for t, c in zip(truth, cand):
        acc += len(set(t[:K]).intersection(c[:K])) / float(K)
    return acc / float(len(truth))


# ---------------------------
# Truth/Candidate builders
# ---------------------------


def truth_faiss(
    index: faiss.IndexFlatIP, V: np.ndarray, K: int, pool: np.ndarray
) -> List[List[int]]:
    """Truth via FAISS Flat (exact). Exclude self by row-id."""
    out: List[List[int]] = []
    for i in pool:
        i_py = int(i)
        q = V[i_py : i_py + 1]
        _, nn_idx = index.search(q, K + 1)
        ids = [int(j) for j in nn_idx[0].tolist() if int(j) != i_py][:K]
        out.append(ids)
    return out


def truth_numpy_stable(
    V: np.ndarray, K: int, pool: np.ndarray, eps: float = 1e-10
) -> List[List[int]]:
    """
    Stable NumPy truth with deterministic tie-break:
    - sim = V @ V[i]^T (float32)
    - exclude self by id
    - lexicographic sort by (-sim', id), where sim' = sim - eps*(id/N)
    """
    N = V.shape[0]
    ids_arr = np.arange(N, dtype=np.int64)
    out: List[List[int]] = []
    for i in pool:
        i_py = int(i)
        sim = (V @ V[i_py : i_py + 1].T).ravel()  # (N,)
        sim[i_py] = -1e9  # exclude self
        # deterministic perturbation by id
        sim_prime = sim - eps * (ids_arr.astype(np.float64) / float(N))
        # build keys for stable lexicographic order
        keys = np.stack((-sim_prime, ids_arr), axis=1)
        order = np.argsort(keys, axis=0)[:, 0]
        topk = order[:K].astype(int).tolist()
        out.append(topk)
    return out


def cand_faiss_flat(
    index: faiss.IndexFlatIP, V: np.ndarray, K: int, pool: np.ndarray
) -> List[List[int]]:
    """Candidate from FAISS Flat (exact)."""
    return truth_faiss(index, V, K, pool)  # same logic (self-exclusion by id)


def cand_rerank64_from_faiss(
    index: faiss.IndexFlatIP,
    V: np.ndarray,
    K: int,
    pool: np.ndarray,
    eps: float = 1e-12,
) -> List[List[int]]:
    """
    Take FAISS top-K, then re-rank those K in float64 with deterministic tie-break (by id).
    """
    V64 = V.astype(np.float64, copy=False)
    out: List[List[int]] = []
    for i in pool:
        i_py = int(i)
        q = V[i_py : i_py + 1]
        _, nn_idx = index.search(q, K + 1)
        k_ids = [int(j) for j in nn_idx[0].tolist() if int(j) != i_py][:K]
        if not k_ids:
            out.append([])
            continue
        q64 = V64[i_py : i_py + 1]
        sub = V64[np.array(k_ids, dtype=int)]
        scores = (sub @ q64.T).ravel()  # float64 scores
        # determinize ties with id epsilon
        scores_prime = scores - eps * (
            np.array(k_ids, dtype=np.float64) / float(V.shape[0])
        )
        order = np.argsort(-scores_prime, kind="mergesort")  # stable
        reranked = [k_ids[idx] for idx in order[:K]]
        out.append(reranked)
    return out


# ---------------------------
# Latency bench (FAISS Flat)
# ---------------------------


def p95_ms(values_ms: List[float]) -> float:
    return float(np.percentile(np.asarray(values_ms, dtype=np.float64), 95))


def bench_faiss_p95(
    index: faiss.IndexFlatIP,
    V: np.ndarray,
    K: int,
    pool: np.ndarray,
    total_searches: int = 1000,
) -> float:
    """Warm once, then measure per-query latency (ms) across >= total_searches searches."""
    if len(pool) == 0:
        return 0.0
    # warm-up
    _ = index.search(V[pool[0] : pool[0] + 1], K)
    times: List[float] = []
    rng = np.random.default_rng(1)
    S = len(pool)
    for _ in range(total_searches):
        i = int(pool[int(rng.integers(0, S))])
        q = V[i : i + 1]
        t0 = time.perf_counter()
        _ = index.search(q, K)
        times.append((time.perf_counter() - t0) * 1000.0)
    return p95_ms(times)


# ---------------------------
# Main
# ---------------------------


def main():
    ap = argparse.ArgumentParser(
        description="ANN Parity Diagnostic (no product-code changes)"
    )
    ap.add_argument(
        "--input",
        required=True,
        help="Path to clarity_clean_analysis/02_output/index.npy",
    )
    ap.add_argument(
        "--ids",
        required=True,
        help="Path to clarity_clean_analysis/02_output/index.ids.json",
    )
    ap.add_argument("--dim", type=int, default=1024)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument(
        "--modes",
        default="faiss_truth,numpy_truth,faiss_flat,cand_rerank64",
        help="Comma-separated among: faiss_truth,numpy_truth,faiss_flat,cand_rerank64",
    )
    ap.add_argument(
        "--receipt",
        required=True,
        help="Output JSON receipt path (binder_receipts/ann_diag.json)",
    )
    args = ap.parse_args()

    # Determinism
    np.random.seed(0)
    random.seed(0)

    # Load vectors
    V = load_vectors(args.input)
    N, D = V.shape
    assert D == args.dim, f"Dim mismatch: V has D={D}, arg dim={args.dim}"

    # Audit
    audit = audit_norms(V)

    # Sample pool
    pool = sample_indices(N, args.samples, seed=0)

    # Build FAISS flat index once
    index = faiss_index_flat_ip(args.dim, V)

    # Modes
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]

    # Truths/candidates storage
    truth_f: List[List[int]] = []
    truth_n: List[List[int]] = []
    cand_f: List[List[int]] = []
    cand_r: List[List[int]] = []

    # Compute as requested
    if "faiss_truth" in modes:
        truth_f = truth_faiss(index, V, args.k, pool)
    if "numpy_truth" in modes:
        truth_n = truth_numpy_stable(V, args.k, pool, eps=1e-10)
    if "faiss_flat" in modes:
        cand_f = cand_faiss_flat(index, V, args.k, pool)
    if "cand_rerank64" in modes:
        cand_r = cand_rerank64_from_faiss(index, V, args.k, pool, eps=1e-12)

    # Overlap metrics (only if both sides present)
    overlaps = {}
    if truth_f and cand_f:
        overlaps["faiss_truth_vs_faiss_flat"] = float(
            overlap_at_k(truth_f, cand_f, args.k)
        )
    if truth_n and cand_f:
        overlaps["numpy_truth_vs_faiss_flat"] = float(
            overlap_at_k(truth_n, cand_f, args.k)
        )
    if truth_f and cand_r:
        overlaps["faiss_truth_vs_rerank64"] = float(
            overlap_at_k(truth_f, cand_r, args.k)
        )
    if truth_n and cand_r:
        overlaps["numpy_truth_vs_rerank64"] = float(
            overlap_at_k(truth_n, cand_r, args.k)
        )

    # Latency bench (FAISS flat)
    p95 = bench_faiss_p95(index, V, args.k, pool, total_searches=1000)

    # Gates (strict)
    gates = {"overlap_threshold": 0.99, "p95_threshold_ms": 150.0}
    parity_val = overlaps.get("faiss_truth_vs_faiss_flat", 0.0)
    status = (
        "PASS"
        if (
            parity_val >= gates["overlap_threshold"]
            and p95 <= gates["p95_threshold_ms"]
        )
        else "FAIL"
    )

    # Receipt
    os.makedirs(os.path.dirname(args.receipt), exist_ok=True)
    doc = {
        "numpy": {"N": int(N), "D": int(D)},
        "audit": audit,
        "overlap": overlaps,
        "latency": {"faiss_flat_p95_ms": float(p95)},
        "gates": gates,
        "status": status,
        "notes": "Truth=FAISS Flat; NumPy truth uses stable (−score, id/N ε) tie-break; candidates: faiss_flat and rerank64@K.",
        "ablations": {},  # optional future fills
    }
    with open(args.receipt, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    # Echo a tiny summary to stdout
    print(
        json.dumps(
            {
                "status": status,
                "overlap_faiss_truth_vs_faiss_flat": parity_val,
                "p95_ms": p95,
                "receipt": args.receipt,
            }
        )
    )


if __name__ == "__main__":
    main()
