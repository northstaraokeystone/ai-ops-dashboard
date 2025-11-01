# scripts/ann_verify_via_diag.py — Verify via DIAG (single source of truth)
import argparse
import json
import os
import subprocess
import sys
import time
import numpy as np
import faiss


def run_diag_if_needed(python_exe, diag_script, inp, ids, dim, k, samples, receipt):
    if os.path.exists(receipt):
        try:
            doc = json.load(open(receipt, "r", encoding="utf-8"))
            if "overlap" in doc and "faiss_truth_vs_faiss_flat" in doc["overlap"]:
                return doc
        except Exception:
            pass
    # Run DIAG to produce the receipt
    cmd = [
        python_exe,
        diag_script,
        "--input",
        inp,
        "--ids",
        ids,
        "--dim",
        str(dim),
        "--k",
        str(k),
        "--samples",
        str(samples),
        "--modes",
        "faiss_truth,faiss_flat",  # minimal modes needed
        "--receipt",
        receipt,
    ]
    subprocess.check_call(cmd)
    return json.load(open(receipt, "r", encoding="utf-8"))


def bench_p95(v_path, dim, k=10, searches=1000):
    V = np.ascontiguousarray(np.load(v_path).astype(np.float32))
    faiss.normalize_L2(V)
    N, D = V.shape
    assert D == dim
    idx = faiss.IndexFlatIP(D)
    idx.add(V)
    rng = np.random.default_rng(1)
    # warm
    _ = idx.search(V[rng.integers(0, N, 1)], k)
    times = []
    for _ in range(searches):
        i = int(rng.integers(0, N))
        t0 = time.perf_counter()
        _ = idx.search(V[i : i + 1], k)
        times.append((time.perf_counter() - t0) * 1000.0)
    return float(np.percentile(np.asarray(times, dtype=np.float64), 95))


def main():
    ap = argparse.ArgumentParser(
        description="ANN verify via DIAG (no product-code changes)"
    )
    ap.add_argument(
        "--input", required=True
    )  # clarity_clean_analysis/02_output/index.npy
    ap.add_argument(
        "--ids", required=True
    )  # clarity_clean_analysis/02_output/index.ids.json
    ap.add_argument("--dim", type=int, default=1024)
    ap.add_argument("--diag_script", default="scripts/ann_diag.py")
    ap.add_argument("--diag_receipt", default="binder_receipts/ann_diag.json")
    ap.add_argument("--verify_receipt", default="binder_receipts/swap_verify.json")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--samples", type=int, default=200)
    args = ap.parse_args()

    python_exe = sys.executable
    os.makedirs(os.path.dirname(args.diag_receipt), exist_ok=True)
    os.makedirs(os.path.dirname(args.verify_receipt), exist_ok=True)

    # 1) Ensure DIAG receipt exists (or run DIAG to produce it)
    diag = run_diag_if_needed(
        python_exe,
        args.diag_script,
        args.input,
        args.ids,
        args.dim,
        args.k,
        args.samples,
        args.diag_receipt,
    )

    # 2) Read authoritative parity from DIAG
    overlap = float(diag["overlap"]["faiss_truth_vs_faiss_flat"])
    N = int(diag["numpy"]["N"])
    D = int(diag["numpy"]["D"])

    # 3) Bench FAISS Flat p95 locally
    p95_ms = bench_p95(args.input, args.dim, k=args.k, searches=1000)

    # 4) Merge/write verify receipt
    gates = {"overlap_threshold": 0.99, "p95_threshold_ms": 150}
    rec = {"numpy": {"N": N, "D": D}, "gates": gates, "gates_pass": {}}
    if os.path.exists(args.verify_receipt):
        try:
            rec.update(json.load(open(args.verify_receipt, "r", encoding="utf-8")))
        except Exception:
            pass
    rec["faiss"] = {
        "overlap_at_10": overlap,
        "p95_ms": p95_ms,
        "params": {"source": "diag+local_bench"},
    }
    rec["gates_pass"]["faiss"] = (
        overlap >= gates["overlap_threshold"] and p95_ms <= gates["p95_threshold_ms"]
    )
    json.dump(rec, open(args.verify_receipt, "w", encoding="utf-8"), indent=2)

    # 5) Echo summary
    print(
        json.dumps(
            {
                "verify_via_diag": True,
                "overlap_at_10": overlap,
                "p95_ms": p95_ms,
                "receipt": args.verify_receipt,
                "pass": rec["gates_pass"]["faiss"],
            }
        )
    )


if __name__ == "__main__":
    import time

    main()
