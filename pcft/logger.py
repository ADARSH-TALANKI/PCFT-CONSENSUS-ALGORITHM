import asyncio
import json
from typing import AsyncGenerator

class AsyncLogBus:
    """
    Async broadcast queue to feed Server-Sent Events (SSE).
    """
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, phase: str, msg: str, **kv):
        payload = {"phase": phase, "msg": msg, **kv}
        await self.queue.put(payload)

    async def stream(self) -> AsyncGenerator[str, None]:
        while True:
            item = await self.queue.get()
            yield f"data: {json.dumps(item, separators=(',',':'))}\n\n"

LOG_BUS = AsyncLogBus()

class Logger:
    def __init__(self):
        self.step = 0

    async def log(self, phase: str, msg: str, **kv):
        self.step += 1
        base = {"t": self.step, "phase": phase, "msg": msg, **kv}
        await LOG_BUS.publish(**base)

LOG = Logger()
