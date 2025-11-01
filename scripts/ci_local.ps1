# scripts/ci_local.ps1
$ErrorActionPreference = 'Stop'

python -m pip install --upgrade pip ruff numpy faiss-cpu

# Lint/format
ruff format --check scripts api
ruff check scripts api

# DIAG → authoritative parity
python scripts/ann_diag.py `
  --input clarity_clean_analysis/02_output/index.npy `
  --ids   clarity_clean_analysis/02_output/index.ids.json `
  --dim 1024 --k 10 --samples 200 `
  --modes faiss_truth,faiss_flat `
  --receipt binder_receipts/ann_diag.json

# VERIFY via DIAG → p95 + merged receipt
python scripts/ann_verify_via_diag.py `
  --input clarity_clean_analysis/02_output/index.npy `
  --ids   clarity_clean_analysis/02_output/index.ids.json `
  --dim 1024 `
  --diag_script scripts/ann_diag.py `
  --diag_receipt binder_receipts/ann_diag.json `
  --verify_receipt binder_receipts/swap_verify.json

# Gate
python - << 'PY'
import json, sys
d=json.load(open("binder_receipts/ann_diag.json","r",encoding="utf-8"))
s=json.load(open("binder_receipts/swap_verify.json","r",encoding="utf-8"))
ok = d["overlap"]["faiss_truth_vs_faiss_flat"] >= 0.99 and s["faiss"]["p95_ms"] <= 150
print("DIAG overlap:", d["overlap"]["faiss_truth_vs_faiss_flat"])
print("VERIFY p95:", s["faiss"]["p95_ms"])
sys.exit(0 if ok else 1)
PY
