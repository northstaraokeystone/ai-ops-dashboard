import hashlib
import json
import uuid  # Import the uuid module
from datetime import datetime  # Import the datetime module
from typing import Any


def _json_serializer(obj: Any) -> str:
    """
    Custom JSON serializer for objects not serializable by default json code.
    Handles UUID and datetime objects.
    """
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _recursive_sort_and_clean(data: Any) -> Any:
    """
    Recursively sorts all keys in dictionaries and removes keys with None values.
    """
    if isinstance(data, dict):
        return {k: _recursive_sort_and_clean(v) for k, v in sorted(data.items()) if v is not None}
    if isinstance(data, list):
        return [_recursive_sort_and_clean(item) for item in data]
    return data


class CryptographyService:
    """
    Handles all cryptographic operations for the Fulcrum protocol.
    """

    @staticmethod
    def generate_hash(data: dict[str, Any]) -> str:
        """
        Generates a deterministic hash for a given data dictionary.
        """
        canonical_data = _recursive_sort_and_clean(data)

        # Use our custom serializer by passing it to the `default` argument
        serialized_data = json.dumps(
            canonical_data,
            separators=(",", ":"),
            ensure_ascii=False,
            default=_json_serializer,  # THIS IS THE FIX
        ).encode("utf-8")

        hasher = hashlib.sha256(serialized_data)
        return hasher.hexdigest()
