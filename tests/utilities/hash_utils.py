import hashlib
import json
from typing import Any


def hash_set(s: Any) -> str:
    """
    Produce a stable SHA256 hash for a pyomo set or any iterable.
    """
    try:
        sorted_elements = sorted(s)
    except TypeError:
        # elements are of mixed types, fallback to canonicalized typed pairs
        sorted_elements = sorted([(type(e).__name__, str(e)) for e in s])
    s_bytes = json.dumps(sorted_elements, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(s_bytes).hexdigest()


EMPTY_SET_HASH = hash_set([])
EMPTY_SET_SENTINEL = '(empty)'


def encode_hashes(sets_dict: dict[str, str]) -> dict[str, str]:
    """Replace the empty-set hash with a readable sentinel for storage."""
    return {k: EMPTY_SET_SENTINEL if v == EMPTY_SET_HASH else v for k, v in sets_dict.items()}


def decode_hashes(sets_dict: dict[str, str]) -> dict[str, str]:
    """Resolve the empty-set sentinel back to its hash for comparison."""
    return {k: EMPTY_SET_HASH if v == EMPTY_SET_SENTINEL else v for k, v in sets_dict.items()}
