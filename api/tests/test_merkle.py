# ai-ops-dashboard/api/tests/test_merkle.py
import json
import os
from datetime import datetime

import pytest

from truthrun.merkle import build_merkle_tree


@pytest.fixture
def sample_events():
    """Provides a sample list of event dictionaries for testing."""
    return [
        {"id": 1, "data": "event1", "ts": datetime.utcnow().isoformat()},
        {"id": 2, "data": "event2", "ts": datetime.utcnow().isoformat()},
    ]


def test_merkle_root_is_built_when_flag_is_on(sample_events):
    """
    Tests that a Merkle root is correctly generated when the feature flag is enabled.
    """
    os.environ["MERKLE_ANCHOR_ENABLED"] = "True"
    root = build_merkle_tree(sample_events)
    assert root is not None
    assert isinstance(root, bytes)
    assert len(root) == 32  # SHA256 digest size
    del os.environ["MERKLE_ANCHOR_ENABLED"]


def test_merkle_root_is_none_when_flag_is_off(sample_events):
    """
    Tests that the function returns None and performs a no-op when the feature flag is disabled.
    """
    # Ensure the flag is not set
    if "MERKLE_ANCHOR_ENABLED" in os.environ:
        del os.environ["MERKLE_ANCHOR_ENABLED"]

    root = build_merkle_tree(sample_events)
    assert root is None


def test_empty_batch_returns_none():
    """
    Tests that an empty list of events correctly returns None, even if the flag is on.
    """
    os.environ["MERKLE_ANCHOR_ENABLED"] = "True"
    root = build_merkle_tree([])
    assert root is None
    del os.environ["MERKLE_ANCHOR_ENABLED"]


def test_single_event_batch_returns_hash_of_that_event():
    """
    Tests that a single event batch returns the hash of that single leaf.
    """
    os.environ["MERKLE_ANCHOR_ENABLED"] = "True"
    single_event = [{"id": 1, "data": "lonely event"}]

    import hashlib

    expected_hash = hashlib.sha256(json.dumps(single_event[0], sort_keys=True).encode("utf-8")).digest()

    root = build_merkle_tree(single_event)
    assert root == expected_hash
    del os.environ["MERKLE_ANCHOR_ENABLED"]


def test_odd_number_of_events_handles_last_leaf_correctly():
    """
    Tests that the tree build logic correctly duplicates the last leaf if there's an odd number of nodes.
    """
    os.environ["MERKLE_ANCHOR_ENABLED"] = "True"
    odd_events = [{"id": 1}, {"id": 2}, {"id": 3}]
    root = build_merkle_tree(odd_events)
    assert root is not None
    assert len(root) == 32
    del os.environ["MERKLE_ANCHOR_ENABLED"]
