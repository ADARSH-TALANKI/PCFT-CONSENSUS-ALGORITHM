import time
from typing import List
from .crypto import hash_obj, sha256_text

class Block:
    def __init__(self, height: int, prev_hash: str, txs: List[dict], timestamp: float|None=None):
        self.height = height
        self.prev_hash = prev_hash
        self.txs = txs[:]
        self.timestamp = timestamp or time.time()
        self.merkle_root = self._merkle_root()
        self.hash = self._hash_block()

    def _merkle_root(self) -> str:
        leaves = [hash_obj(tx) for tx in self.txs] or ["0"*64]
        layer = leaves
        while len(layer) > 1:
            nxt = []
            for i in range(0, len(layer), 2):
                a = layer[i]
                b = layer[i+1] if i+1 < len(layer) else layer[i]
                nxt.append(sha256_text(a + b))
            layer = nxt
        return layer[0]

    def _hash_block(self) -> str:
        header = {
            "height": self.height,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
        }
        return hash_obj(header)

    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "hash": self.hash,
            "tx_count": len(self.txs),
        }
