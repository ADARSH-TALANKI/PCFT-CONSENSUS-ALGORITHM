from .logger import LOG
from .ca import CertificateAuthority
from .crypto import sha256_text

class Node:
    def __init__(self, node_id: str, ca: CertificateAuthority):
        self.node_id = node_id
        self.ca = ca
        self.is_alive = True

    async def verify(self, tx: dict) -> bool:
        if not self.is_alive:
            return False
        cid = tx["client_id"]
        if cid not in self.ca.keys:
            return False
        sk, _ = self.ca.keys[cid]
        expected = sha256_text(tx["hash"] + str(sk))
        ok = (expected == tx["proof"])
        await LOG.log("VERIFY", "replica verified" if ok else "replica rejected",
                      node=self.node_id, client_id=cid, view=tx["view"], nonce=tx["nonce"])
        return ok
