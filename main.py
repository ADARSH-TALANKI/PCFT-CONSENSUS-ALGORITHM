import asyncio, random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# top of app/main.py
from fastapi import FastAPI, Request, Form


from .pcft.logger import LOG, LOG_BUS
from .pcft.ca import CertificateAuthority
from .pcft.client import Client
from .pcft.node import Node
from .pcft.chain import Blockchain

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ---- In-memory singleton state ----
STATE = {
    "ca": None,
    "nodes": [],
    "clients": {},
    "chain": None
}

@app.on_event("startup")
async def startup():
    random.seed(7)
    ca = CertificateAuthority()
    nodes = [Node(f"N{i}", ca) for i in range(5)]
    nodes[4].is_alive = False
    await LOG.log("SETUP", "node status initialized",
                  alive=[n.node_id for n in nodes if n.is_alive],
                  down=[n.node_id for n in nodes if not n.is_alive])

    # default clients
    alice = Client("alice", ca); await alice.init_keys()
    bob   = Client("bob", ca);   await bob.init_keys()

    chain = Blockchain(nodes, batch_size=3)

    STATE.update({
        "ca": ca,
        "nodes": nodes,
        "clients": {"alice": alice, "bob": bob},
        "chain": chain
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------ SSE logs ------
@app.get("/logs")
async def logs():
    return StreamingResponse(LOG_BUS.stream(), media_type="text/event-stream")

# ------ Read state ------
@app.get("/nodes")
async def nodes():
    ns = [{"node_id": n.node_id, "alive": n.is_alive} for n in STATE["nodes"]]
    return {"nodes": ns, "primary": STATE["chain"].primary.node_id, "view": STATE["chain"].view}

@app.get("/chain")
async def chain():
    return {"chain": [b.to_dict() for b in STATE["chain"].chain], "valid": STATE["chain"].validate_chain()}

@app.get("/clients")
async def clients():
    return {"clients": list(STATE["clients"].keys())}

# ------ Actions ------

@app.post("/commit")
async def commit():
    # force commit current mempool (if not empty)
    if STATE["chain"].mempool:
        await STATE["chain"]._commit_block()
        return {"ok": True}
    return {"ok": False, "reason": "mempool empty"}


@app.post("/tx")
async def submit_tx(
    client_id: str = Form(...),
    message: str = Form(...)
):
    if client_id not in STATE["clients"]:
        return JSONResponse({"error": "unknown client"}, status_code=400)
    chain = STATE["chain"]
    client = STATE["clients"][client_id]
    chain.tx_nonce += 1
    tx = await client.create_tx(message, view=chain.view, nonce=chain.tx_nonce)
    await chain.submit_tx(tx)
    return {"ok": True}

@app.post("/toggle_node")
async def toggle_node(
    node_id: str = Form(...)
):
    for n in STATE["nodes"]:
        if n.node_id == node_id:
            n.is_alive = not n.is_alive
            await LOG.log("SETUP", "node toggled", node=node_id, alive=n.is_alive)
            return {"ok": True, "alive": n.is_alive}
    return JSONResponse({"error": "node not found"}, status_code=404)

@app.post("/add_client")
async def add_client(
    client_id: str = Form(...)
):
    if client_id in STATE["clients"]:
        return JSONResponse({"error": "client exists"}, status_code=400)
    c = Client(client_id, STATE["ca"])
    await c.init_keys()
    STATE["clients"][client_id] = c
    return {"ok": True}
