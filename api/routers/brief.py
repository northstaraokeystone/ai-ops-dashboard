# api/routers/brief.py
from fastapi import APIRouter, Query
from pathlib import Path
from datetime import datetime, timezone
import yaml
import hashlib

from api.schemas.dossier import Dossier, Claim, Receipts
from api.services.retrieval_numpy import ask_numpy  # reuse retrieval

router = APIRouter(tags=["briefs"])

CFG_PATH = Path("clarity_clean_analysis/04_configs/augury.local.yaml")


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


@router.get("/brief", response_model=Dossier)
def brief(q: str = Query(..., min_length=2), k: int = Query(5, ge=1, le=10)):
    cfg = yaml.safe_load(CFG_PATH.read_text())
    corpus_p = Path(cfg["paths"]["corpus"])

    # simple evidence: top-k chunks from retrieval
    results = ask_numpy(q, k)
    claims = []
    for r in results:
        # take first line/sentence as claim text (trim to 240 chars)
        claim_text = (r["text"].splitlines()[0] or r["text"]).strip()[:240]
        claims.append(
            Claim(
                text=claim_text,
                chunk_ids=[r["chunk_id"]],
                confidence=min(max(r["score"], 0.0), 1.0),
            )
        )

    # executive summary = first claim or fallback to query
    summary = claims[0].text if claims else q

    # receipts: dataset hash from corpus; config hash = sha256 of yaml
    receipts = Receipts(
        config_hash=hashlib.sha256(CFG_PATH.read_bytes()).hexdigest(),
        dataset_hash=_sha256(corpus_p),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    dossier = Dossier(
        executive_summary=summary,
        claims=claims,
        contradictions_identified=[],
        next_questions_uncovered=[],
        receipts=receipts,
    )
    return dossier
