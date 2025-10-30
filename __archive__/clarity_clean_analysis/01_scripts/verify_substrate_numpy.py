import json
import yaml
import hashlib
from pathlib import Path
import numpy as np


def sha256(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


cfg = yaml.safe_load(
    Path("clarity_clean_analysis/04_configs/augury.local.yaml").read_text()
)
paths = {
    k: Path(v)
    for k, v in cfg["paths"].items()
    if k in ("corpus", "index", "id_map", "manifest")
}
violations = []

# existence
for name, p in paths.items():
    if not p.exists():
        violations.append(f"Missing {name}")

status = "DONE"
counts = {"jsonl_lines": 0, "id_map_len": 0, "index_total": 0}
sha_match = {"corpus": False, "index": False}
dim = 0

if not violations:
    # corpus lines
    counts["jsonl_lines"] = sum(1 for _ in paths["corpus"].open("r", encoding="utf-8"))
    # id_map
    id_map = json.loads(paths["id_map"].read_text(encoding="utf-8"))
    counts["id_map_len"] = len(id_map)
    # index.npy
    X = np.load(paths["index"])
    dim = int(X.shape[1])
    counts["index_total"] = int(X.shape[0])
    # manifest sha checks
    mf = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    sha = mf.get("sha256", {})
    sha_match["corpus"] = sha.get("corpus", "") == sha256(paths["corpus"])
    sha_match["index"] = sha.get("index", "") == sha256(paths["index"])
    # consistency
    if not (counts["jsonl_lines"] == counts["id_map_len"] == counts["index_total"]):
        violations.append("Count mismatch (jsonl vs id_map vs index)")
    if dim != int(cfg["embeddings"]["dim"]):
        violations.append(f"Dim mismatch: data {dim} vs cfg {cfg['embeddings']['dim']}")
else:
    status = "ABSTAIN"

print(
    json.dumps(
        {
            "status": status,
            "counts": counts,
            "dim": dim or cfg["embeddings"]["dim"],
            "sha256_match": sha_match,
            "paths": {k: str(v) for k, v in paths.items()},
            "violations": violations,
        },
        indent=2,
    )
)
