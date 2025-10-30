import json
import hashlib
from pathlib import Path

base = Path("clarity_clean_analysis/02_output")
corpus = base / "corpus_raw_research_final.jsonl"
index = base / "index.npy"
manifest = base / "index_manifest.json"


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


m = json.loads(manifest.read_text(encoding="utf-8"))
m.setdefault("sha256", {})
m["sha256"]["corpus"] = sha(corpus)
m["sha256"]["index"] = sha(index)
m["index_path"] = str(index).replace("\\", "/")
manifest.write_text(json.dumps(m, indent=2), encoding="utf-8")
print("REFRESHED")
