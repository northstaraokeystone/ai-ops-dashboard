import json
import hashlib
from typing import Any, Dict


def _recursive_sort_and_clean(data: Any) -> Any:
    """
    Recursively sorts all keys in dictionaries and removes keys with None values.
    This is the core of our deterministic canonicalization.
    """
    if isinstance(data, dict):
        # Sort dictionary keys and filter out None values, then recurse
        return {
            k: _recursive_sort_and_clean(v)
            for k, v in sorted(data.items())
            if v is not None
        }
    if isinstance(data, list):
        # Recurse on each item in the list
        return [_recursive_sort_and_clean(item) for item in data]
    return data


class CryptographyService:
    """
    Handles all cryptographic operations for the Fulcrum protocol.
    Ensures crypto-agility by centralizing all crypto logic here.
    """

    @staticmethod
    def generate_hash(data: Dict[str, Any]) -> str:
        """
        Generates a deterministic hash for a given data dictionary.

        This process is the heart of our verifiability:
        1. Recursively sorts all keys and removes null values to ensure that
           logically identical objects always have the same representation.
        2. Serializes the cleaned object to a compact JSON string.
        3. Hashes the resulting string using the SHA-256 algorithm.

        Returns:
            A hex-encoded string of the SHA-256 hash.
        """
        # 1. Canonicalize the data object
        canonical_data = _recursive_sort_and_clean(data)

        # 2. Serialize to a compact, deterministic JSON string
        #    separators=(',', ':') removes whitespace.
        #    ensure_ascii=False is important for consistent handling of unicode.
        serialized_data = json.dumps(
            canonical_data, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

        # 3. Hash the resulting byte string
        hasher = hashlib.sha256(serialized_data)
        return hasher.hexdigest()
