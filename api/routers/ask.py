# api/routers/ask.py
from fastapi import APIRouter, Query
from time import perf_counter
from api.services.retrieval_numpy import ask_numpy, ask_numpy_with_stats

router = APIRouter(tags=["retrieval"])


@router.get("/ask")
def ask(
    q: str = Query(..., min_length=2),
    k: int = Query(5, ge=1, le=20),
    debug: int = Query(0, ge=0, le=1),
):
    t0 = perf_counter()
    if debug:
        results, stats = ask_numpy_with_stats(q, k)
    else:
        results = ask_numpy(q, k)
        stats = None
    elapsed_ms = int((perf_counter() - t0) * 1000)
    payload = {"status": "DONE", "k": k, "elapsed_ms": elapsed_ms, "results": results}
    if stats is not None:
        payload["cache"] = stats
    return payload
