# ai-ops-dashboard/api/truthrun/merkle.py
import hashlib
import os
import numpy as np
import json
from typing import List, Optional


def hash_bytes(data: bytes) -> bytes:
    """SHA256 digest on bytes."""
    return hashlib.sha256(data).digest()


def build_merkle_tree(events: List[dict]) -> Optional[bytes]:
    """Build binary Merkle tree root from event batch."""
    if not os.getenv("MERKLE_ANCHOR_ENABLED", "False") == "True":
        return None  # No-op if flagged off

    if not events:
        return None

    # Bytes conversion: JSON dump sorted for determinism
    leaf_bytes = [json.dumps(event, sort_keys=True).encode("utf-8") for event in events]
    leaves = np.array([hash_bytes(b) for b in leaf_bytes], dtype=object)

    # Tree levels: Vectorized build
    tree = [leaves]
    while len(tree[-1]) > 1:
        level = tree[-1]
        next_level = np.empty((len(level) + 1) // 2, dtype=object)
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            combined = left + right
            next_level[i // 2] = hash_bytes(combined)
        tree.append(next_level)

    return tree[-1][0]  # Root digest
