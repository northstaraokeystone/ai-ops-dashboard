import json
import hashlib
import sys
from pathlib import Path
import yaml
import numpy as np


def sha256(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cfg(p):
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


def main(cfg_path):
    cfg = load_cfg(cfg_path)
    paths = cfg["paths"]
    emb = cfg["embeddings"]
    corpus = Path(paths["corpus"])
    idx = Path(paths["index"])  # we'll write embeddings .npy here
    idmap = Path(paths.get("id_map", str(idx.with_suffix(".ids.json"))))
    manifest = Path(paths.get("manifest", str(idx.with_name("index_manifest.json"))))
    dim_expected = int(emb["dim"])

    if not corpus.exists():
        print(f"ABSTAIN: missing corpus {corpus}")
        sys.exit(2)

    ids, vecs = [], []
    with corpus.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            j = json.loads(line)
            ids.append(j["chunk_id"])
            vecs.append(j["mean_chunk_embedding"])
    X = np.asarray(vecs, dtype="float32")
    if X.size == 0:
        print("ABSTAIN: empty corpus")
        sys.exit(2)

    # L2-normalize for cosine
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    Xn = X / norms
    data_dim = Xn.shape[1]
    if data_dim != dim_expected:
        print(f"NOTE: data dim {data_dim} != cfg {dim_expected}; using {data_dim}")

    # save as .npy (index = normalized embeddings)
    idx.parent.mkdir(parents=True, exist_ok=True)
    np.save(idx, Xn)  # writes index.npy if idx endswith .npy; else uses given name

    # id map
    idmap.write_text(
        json.dumps({i: cid for i, cid in enumerate(ids)}, indent=2), encoding="utf-8"
    )

    # manifest
    manifest.write_text(
        json.dumps(
            {
                "index_type": "brutecosine",
                "count": len(ids),
                "dim": int(data_dim),
                "metric": "cosine",
                "embed_model": emb["model"],
                "corpus_path": str(corpus),
                "index_path": str(
                    idx if str(idx).endswith(".npy") else str(idx) + ".npy"
                ),
                "id_map_path": str(idmap),
                "sha256": {"corpus": sha256(corpus)},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "DONE",
                "paths": {
                    "corpus": str(corpus),
                    "index": str(
                        idx if str(idx).endswith(".npy") else str(idx) + ".npy"
                    ),
                    "id_map": str(idmap),
                    "manifest": str(manifest),
                },
                "counts": {
                    "jsonl_lines": len(ids),
                    "id_map_len": len(ids),
                    "index_total": len(ids),
                },
                "dim": {
                    "data": int(data_dim),
                    "expected": dim_expected,
                    "normalized": True,
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python clarity_clean_analysis/01_scripts/build_brutecosine_index.py clarity_clean_analysis/04_configs/augury.local.yaml"
        )
        sys.exit(1)
    main(sys.argv[1])
