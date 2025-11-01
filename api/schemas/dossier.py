# api/schemas/dossier.py

from pydantic import BaseModel


class Claim(BaseModel):
    text: str
    chunk_ids: list[str]
    confidence: float = 0.5
    notes: str | None = None


class Contradiction(BaseModel):
    claim: str
    conflict_with_chunk_id: str
    resolution_hypothesis: str | None = None


class Receipts(BaseModel):
    config_hash: str
    dataset_hash: str
    seed: int = 0
    merkle_root: str = ""
    signature: str = ""
    key_id: str = ""
    timestamp: str


class Dossier(BaseModel):
    executive_summary: str
    claims: list[Claim]
    contradictions_identified: list[Contradiction] = []
    next_questions_uncovered: list[str] = []
    receipts: Receipts
