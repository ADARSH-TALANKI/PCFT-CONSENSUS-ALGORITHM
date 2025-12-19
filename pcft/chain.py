from typing import List
from .logger import LOG
from .block import Block
from .node import Node

class Blockchain:
    def __init__(self, nodes: List[Node], batch_size: int = 3):
        self.nodes = nodes
        self.primary = nodes[0]
        self.replicas = nodes[1:]
        self.batch_size = batch_size
        self.chain: List[Block] = [self._genesis()]
        self.mempool: List[dict] = []
        self.view = 1
        self.tx_nonce = 0

    def _genesis(self) -> Block:
        return Block(height=0, prev_hash="0"*64, txs=[], timestamp=0.0)

    async def submit_tx(self, tx: dict):
        # FORWARD
        self.tx_nonce = tx["nonce"]
        await LOG.log("FORWARD", "primary broadcast", primary=self.primary.node_id,
                      view=self.view, nonce=self.tx_nonce)
        for r in self.replicas:
            await LOG.log("FORWARD", "replica received", node=r.node_id,
                          view=self.view, nonce=self.tx_nonce)

        # VERIFY
        votes = 0
        for n in self.nodes:
            if await n.verify(tx):
                votes += 1

        # FINISH
        majority = (len(self.nodes)//2) + 1
        if votes >= majority:
            self.mempool.append(tx)
            await LOG.log("FINISH", "majority reached; client notified",
                          votes=votes, required=majority, view=self.view, nonce=self.tx_nonce)
            if len(self.mempool) >= self.batch_size:
                await self._commit_block()
        else:
            await LOG.log("FINISH", "consensus failed; client notified",
                          votes=votes, required=majority, view=self.view, nonce=self.tx_nonce)

    async def _commit_block(self):
        txs = self.mempool[:self.batch_size]
        self.mempool = self.mempool[self.batch_size:]
        prev_hash = self.chain[-1].hash
        block = Block(height=len(self.chain), prev_hash=prev_hash, txs=txs)
        self.chain.append(block)
        await LOG.log("FINISH", "block committed", height=block.height,
                      tx_count=len(txs), hash=block.hash[:16], prev=block.prev_hash[:16])
        await self._rotate_view()

    async def _rotate_view(self):
        idx = self.nodes.index(self.primary)
        self.primary = self.nodes[(idx+1) % len(self.nodes)]
        self.replicas = [n for n in self.nodes if n is not self.primary]
        self.view += 1
        await LOG.log("FORWARD", "view change (new primary)", view=self.view, primary=self.primary.node_id)

    def validate_chain(self) -> bool:
        for i, blk in enumerate(self.chain):
            if i == 0:
                if blk.prev_hash != "0"*64: return False
                continue
            if blk.prev_hash != self.chain[i-1].hash: return False
            if blk.merkle_root != blk._merkle_root(): return False
            if blk.hash != blk._hash_block(): return False
        return True
