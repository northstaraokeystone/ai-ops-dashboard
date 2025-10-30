import json
import yaml
import numpy as np
import time
from pathlib import Path

cfg = yaml.safe_load(
    Path("clarity_clean_analysis/04_configs/augury.local.yaml").read_text()
)
X = np.load(cfg["paths"]["index"])  # index.npy (normalized matrix)
id_map = {
    int(k): v for k, v in json.loads(Path(cfg["paths"]["id_map"]).read_text()).items()
}

t0 = time.time()
q = X[0]  # self-query
sims = X @ q  # cosine via dot product
top5_idx = np.argsort(-sims)[:5].tolist()
print(
    {
        "status": "DONE",
        "count": int(X.shape[0]),
        "dim": int(X.shape[1]),
        "top5": [id_map[i] for i in top5_idx],
        "p95_ms": int((time.time() - t0) * 1000),
    }
)
