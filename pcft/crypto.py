import hashlib
import json
from typing import Any

def sha256_bytes(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()

def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode())

def hash_obj(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True).encode())
