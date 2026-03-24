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
