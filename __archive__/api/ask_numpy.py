import argparse
import json
import yaml
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# load cfg + artifacts
cfg = yaml.safe_load(
    Path("clarity_clean_analysis/04_configs/augury.local.yaml").read_text()
)
X = np.load(cfg["paths"]["index"])  # normalized matrix (index.npy)
id_map = {
    int(k): v for k, v in json.loads(Path(cfg["paths"]["id_map"]).read_text()).items()
}

# quick chunk_id -> content map
cid2text = {}
with Path(cfg["paths"]["corpus"]).open("r", encoding="utf-8") as f:
    for line in f:
        j = json.loads(line)
        cid2text[j["chunk_id"]] = j["content"]

embed = SentenceTransformer(cfg["embeddings"]["model"])  # BAAI/bge-large-en-v1.5


def topk(query, k):
    q = embed.encode([query])[0].astype("float32")
    q /= np.linalg.norm(q) + 1e-12  # cosine via dot
    sims = X @ q
    idxs = np.argsort(-sims)[:k].tolist()
    return [
        {"chunk_id": id_map[i], "score": float(sims[i]), "text": cid2text[id_map[i]]}
        for i in idxs
    ]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    results = topk(args.query, args.k)
    print(
        json.dumps(
            {"status": "DONE", "k": args.k, "results": results},
            ensure_ascii=False,
            indent=2,
        )
    )
