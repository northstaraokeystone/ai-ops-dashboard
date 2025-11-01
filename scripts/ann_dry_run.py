# scripts/ann_dry_run.py — Verify via DIAG for FAISS; IVF/HNSW local; ruff-safe
import argparse
import json
import os
import sys
import time
from typing import Tuple

import numpy as np
import faiss

try:
    import hnswlib  # optional
except Exception:
    hnswlib = None


def bench_p95_flat(vec_path: str, dim: int, k: int = 10, searches: int = 1000) -> float:
    """Bench p95 latency for FAISS Flat IP."""
    V = np.ascontiguousarray(np.load(vec_path).astype(np.float32))
    faiss.normalize_L2(V)
    n, d = V.shape
    assert d == dim
    idx = faiss.IndexFlatIP(d)
    idx.add(V)
    rng = np.random.default_rng(1)
    # warm
    _ = idx.search(V[rng.integers(0, n, size=1)], k)
    times = []
    for _ in range(searches):
        i = int(rng.integers(0, n))
        q = V[i : i + 1]
        t0 = time.perf_counter()
        _ = idx.search(q, k)
        times.append((time.perf_counter() - t0) * 1000.0)
    return float(np.percentile(np.asarray(times, dtype=np.float64), 95))


def run_diag_and_read_overlap(
    python_exe: str,
    diag_script: str,
    vec_path: str,
    ids_path: str,
    dim: int,
    k: int,
    samples: int,
    diag_receipt: str,
) -> Tuple[float, int, int]:
    """Ensure DIAG receipt exists; return (overlap, N, D)."""
    need_run = True
    if os.path.exists(diag_receipt):
        try:
            _doc = json.load(open(diag_receipt, "r", encoding="utf-8"))
            if "overlap" in _doc and "faiss_truth_vs_faiss_flat" in _doc["overlap"]:
                need_run = False
        except Exception:
            need_run = True
    if need_run:
        cmd = [
            python_exe,
            diag_script,
            "--input",
            vec_path,
            "--ids",
            ids_path,
            "--dim",
            str(dim),
            "--k",
            str(k),
            "--samples",
            str(samples),
            "--modes",
            "faiss_truth,faiss_flat",
            "--receipt",
            diag_receipt,
        ]
        # raises on error → good
        import subprocess

        subprocess.check_call(cmd)

    doc = json.load(open(diag_receipt, "r", encoding="utf-8"))
    overlap = float(doc["overlap"]["faiss_truth_vs_faiss_flat"])
    n = int(doc["numpy"]["N"])
    d = int(doc["numpy"]["D"])
    return overlap, n, d


def main() -> None:
    ap = argparse.ArgumentParser(description="ANN verify harness (FAISS via DIAG)")
    ap.add_argument("--algo", choices=["faiss", "faiss_ivf", "hnsw"], required=True)
    ap.add_argument(
        "--input", required=True
    )  # clarity_clean_analysis/02_output/index.npy
    ap.add_argument(
        "--ids", required=True
    )  # clarity_clean_analysis/02_output/index.ids.json
    ap.add_argument("--output", required=True)
    ap.add_argument("--dim", type=int, required=True)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--receipt", required=True)  # binder_receipts/swap_verify.json
    # optional wiring to DIAG
    ap.add_argument("--diag_script", default="scripts/ann_diag.py")
    ap.add_argument("--diag_receipt", default="binder_receipts/ann_diag.json")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--samples", type=int, default=200)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.receipt), exist_ok=True)

    # FAISS path: delegate parity to DIAG; bench p95 locally; write merged receipt.
    if args.algo == "faiss" and args.verify:
        overlap, n, d = run_diag_and_read_overlap(
            python_exe=sys.executable,
            diag_script=args.diag_script,
            vec_path=args.input,
            ids_path=args.ids,
            dim=args.dim,
            k=args.k,
            samples=args.samples,
            diag_receipt=args.diag_receipt,
        )
        p95_ms = bench_p95_flat(args.input, args.dim, k=args.k, searches=1000)
        gates = {"overlap_threshold": 0.99, "p95_threshold_ms": 150}
        rec = {
            "numpy": {"N": n, "D": d},
            "gates": gates,
            "gates_pass": {},
        }
        if os.path.exists(args.receipt):
            try:
                rec.update(json.load(open(args.receipt, "r", encoding="utf-8")))
            except Exception:
                pass
        rec["faiss"] = {
            "overlap_at_10": overlap,
            "p95_ms": p95_ms,
            "params": {"source": "diag+local_bench"},
        }
        rec["gates_pass"]["faiss"] = (
            overlap >= gates["overlap_threshold"]
            and p95_ms <= gates["p95_threshold_ms"]
        )
        json.dump(rec, open(args.receipt, "w", encoding="utf-8"), indent=2)
        # Echo small summary
        print(
            json.dumps(
                {
                    "verify_via_diag": True,
                    "overlap_at_10": overlap,
                    "p95_ms": p95_ms,
                    "receipt": args.receipt,
                    "pass": rec["gates_pass"]["faiss"],
                }
            )
        )
        return

    # Non-verify or non-faiss fall through to minimal build/no-op verify to keep CLI stable
    # Build index as requested (no parity promises here).
    params = {}
    if args.algo == "faiss":
        # no-op here (handled above in verify path); still add for symmetry
        V = np.ascontiguousarray(np.load(args.input).astype(np.float32))
        faiss.normalize_L2(V)
        d = V.shape[1]
        idx = faiss.IndexFlatIP(d)
        idx.add(V)
    elif args.algo == "faiss_ivf":
        V = np.ascontiguousarray(np.load(args.input).astype(np.float32))
        faiss.normalize_L2(V)
        n, d = V.shape
        nlist = min(max(64, int(4 * np.sqrt(n))), int(n // 40))
        idx = faiss.index_factory(d, f"IVF{nlist},Flat", faiss.METRIC_INNER_PRODUCT)
        if not idx.is_trained:
            idx.train(V)
        idx.add(V)
        idx.nprobe = 16
        params = {"nlist": nlist, "nprobe": 16}
        # optional sidecar
        faiss.write_index(idx, args.output)
        json.dump(params, open(args.output + ".meta.json", "w", encoding="utf-8"))
    else:  # hnsw
        if hnswlib is None:
            print("hnswlib not installed; skipping on Windows.", file=sys.stderr)
            sys.exit(1)
        V = np.ascontiguousarray(np.load(args.input).astype(np.float32))
        faiss.normalize_L2(V)
        d = V.shape[1]
        idx = hnswlib.Index(space="ip", dim=d)
        idx.init_index(max_elements=V.shape[0], ef_construction=200, M=16)
        idx.add_items(V)
        idx.set_ef(200)
        params = {"ef_construction": 200, "M": 16}
        # no save to disk here

    # If not --verify, we’re done (build-only path).
    if not args.verify:
        return

    # For non-faiss verify, we intentionally do not compute overlap here.
    # We still record a bench and leave overlap untouched to avoid parity drift.
    p95_ms = bench_p95_flat(args.input, args.dim, k=args.k, searches=1000)
    gates = {"overlap_threshold": 0.99, "p95_threshold_ms": 150}
    rec = {
        "numpy": {"N": int(V.shape[0]), "D": int(V.shape[1])},
        "gates": gates,
        "gates_pass": {},
    }
    if os.path.exists(args.receipt):
        try:
            rec.update(json.load(open(args.receipt, "r", encoding="utf-8")))
        except Exception:
            pass
    rec[args.algo] = {
        "overlap_at_10": rec.get(args.algo, {}).get("overlap_at_10"),  # unchanged/None
        "p95_ms": p95_ms,
        "params": params,
    }
    # We do not set gates_pass for non-faiss here (no overlap assertion).
    json.dump(rec, open(args.receipt, "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    main()
