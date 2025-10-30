# api/schemas/dossier.py
from pydantic import BaseModel
from typing import List, Optional


class Claim(BaseModel):
    text: str
    chunk_ids: List[str]
    confidence: float = 0.5
    notes: Optional[str] = None


class Contradiction(BaseModel):
    claim: str
    conflict_with_chunk_id: str
    resolution_hypothesis: Optional[str] = None


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
    claims: List[Claim]
    contradictions_identified: List[Contradiction] = []
    next_questions_uncovered: List[str] = []
    receipts: Receipts
