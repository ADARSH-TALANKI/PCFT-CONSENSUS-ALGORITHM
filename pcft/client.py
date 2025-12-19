from .crypto import sha256_text
from .logger import LOG
from .ca import CertificateAuthority

class Client:
    def __init__(self, client_id: str, ca: CertificateAuthority):
        self.client_id = client_id
        self.sk = None
        self.pk = None
        self.ca = ca

    async def init_keys(self):
        self.sk, self.pk = await self.ca.issue_keys(self.client_id)

    async def create_tx(self, message: str, view: int, nonce: int) -> dict:
        h = sha256_text(message)
        proof = sha256_text(h + str(self.sk))
        tx = {
            "client_id": self.client_id,
            "hash": h,
            "proof": proof,
            "opaque_payload": f"[{len(message)} bytes hidden]",
            "view": view,
            "nonce": nonce,
        }
        await LOG.log("REQUEST", "client created request",
                      client_id=self.client_id, h=h[:12], view=view, nonce=nonce)
        return tx
