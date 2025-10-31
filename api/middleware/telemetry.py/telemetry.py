from time import perf_counter
import os
import json
import hashlib
import yaml
import pathlib
from datetime import datetime

CONFIG_PATH = pathlib.Path("clarity_clean_analysis/04_configs/augury.local.yaml")
IDS_PATH = pathlib.Path("clarity_clean_analysis/02_output/index.ids.json")

CACHE = {
    "seen": set(),
    "count": None,
    "index_backend": None,
    "model": "BAAI/bge-large-en-v1.5",
    "dim": 1024,
}


def _load_cfg():
    try:
        cfg = yaml.safe_load(open(CONFIG_PATH, "r", encoding="utf-8"))
        CACHE["index_backend"] = (cfg.get("index") or {}).get("backend", "numpy")
    except Exception:
        CACHE["index_backend"] = "numpy"
    try:
        CACHE["count"] = len(json.load(open(IDS_PATH, "r", encoding="utf-8")))
    except Exception:
        CACHE["count"] = None


async def telemetry_middleware(request, call_next):
    if str(os.getenv("LOG_TELEMETRY", "")).lower() not in ("1", "true", "yes", "on"):
        return await call_next(request)
    t0 = perf_counter()
    response = await call_next(request)
    elapsed_ms = int((perf_counter() - t0) * 1000)
    route = request.url.path
    qs = dict(request.query_params)
    k = int(qs.get("k")) if "k" in qs else None
    q = qs.get("q", "")
    qh = hashlib.sha256(q.encode("utf-8")).hexdigest()[:16] if q else None
    if CACHE["count"] is None or CACHE["index_backend"] is None:
        _load_cfg()
    cache_hit = 1 if (qh and qh in CACHE["seen"]) else 0
    if qh:
        CACHE["seen"].add(qh)
    line = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "route": route,
        "elapsed_ms": elapsed_ms,
        "status": response.status_code,
        "k": k,
        "cache_hit": cache_hit,
        "query_hash": qh,
        "model": CACHE["model"],
        "dim": CACHE["dim"],
        "index_backend": CACHE["index_backend"],
        "count": CACHE["count"],
    }
    print(json.dumps(line), flush=True)
    return response
