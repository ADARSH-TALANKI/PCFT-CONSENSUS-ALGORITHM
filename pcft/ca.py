import random
from .logger import LOG

class CertificateAuthority:
    def __init__(self):
        self.keys: dict[str, tuple[int,int]] = {}

    async def issue_keys(self, client_id: str):
        sk = random.randint(1, 10**9)
        pk = sk * 2
        self.keys[client_id] = (sk, pk)
        await LOG.log("SETUP", "issued keypair", client_id=client_id, pk=pk)
        return sk, pk
