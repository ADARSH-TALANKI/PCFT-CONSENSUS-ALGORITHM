const $ = (q)=>document.querySelector(q);
const logsEl = $("#logs");
const chainEl = $("#chainView");
const nodeInfo = $("#nodeInfo");
const clientSelect = $("#clientSelect");
const messageInput = $("#messageInput");
const sendBtn = $("#sendBtn");
const refreshBtn = $("#refreshChain");
const forceCommitBtn = $("#forceCommit");
const addClientBtn = $("#addClientBtn");
const newClientId = $("#newClientId");

// --- helpers ---
async function jget(url){ const r=await fetch(url); return r.json(); }
async function jpost(url, body){
  const params = new URLSearchParams(body);
  const r = await fetch(url, { method:"POST", headers:{"Content-Type":"application/x-www-form-urlencoded"}, body: params });
  return r.json();
}

function appendLog(obj){
  const line = JSON.stringify(obj);
  logsEl.textContent += line + "\n";
  logsEl.scrollTop = logsEl.scrollHeight;
}

async function loadClients(){
  const {clients} = await jget("/clients");
  clientSelect.innerHTML = "";
  for(const c of clients){
    const opt = document.createElement("option");
    opt.value = c; opt.textContent = c;
    clientSelect.appendChild(opt);
  }
}

async function loadNodes(){
  const {nodes, primary, view} = await jget("/nodes");
  nodeInfo.innerHTML = `<div>Primary: <b>${primary}</b> &nbsp; | &nbsp; View: <b>${view}</b></div>`;
  const wrap = document.createElement("div");
  for(const n of nodes){
    const div = document.createElement("div");
    div.className = "node" + (n.node_id===primary ? " primary":"");
    const badge = document.createElement("span");
    badge.className = "badge " + (n.alive ? "alive":"dead");
    badge.textContent = n.alive ? "alive" : "down";
    const btn = document.createElement("button");
    btn.textContent = n.alive ? "Toggle Down" : "Toggle Up";
    btn.onclick = async ()=>{
      await jpost("/toggle_node",{node_id:n.node_id});
      await loadNodes();
    };
    div.innerHTML = `<b>${n.node_id}</b>`;
    div.appendChild(badge);
    div.appendChild(btn);
    wrap.appendChild(div);
  }
  nodeInfo.appendChild(wrap);
}

async function loadChain(){
  const data = await jget("/chain");
  chainEl.textContent = JSON.stringify(data, null, 2);
}

// --- wire UI ---
sendBtn.onclick = async ()=>{
  const client_id = clientSelect.value || "alice";
  const message = messageInput.value || "Alice -> Pay 5 to Bob";
  await jpost("/tx", {client_id, message});
  messageInput.value = "";
  await loadChain();
  await loadNodes();
};

refreshBtn.onclick = loadChain;

forceCommitBtn.onclick = async ()=>{
  await jpost("/commit", {});
  await loadChain();
  await loadNodes();
};

addClientBtn.onclick = async ()=>{
  const cid = newClientId.value.trim();
  if(!cid) return;
  const res = await jpost("/add_client", {client_id: cid});
  if(res.ok){ await loadClients(); newClientId.value=""; }
};

// --- init ---
(async function init(){
  await loadClients();
  await loadNodes();
  await loadChain();

  // SSE logs
  const ev = new EventSource("/logs");
  ev.onmessage = (e)=> {
    try{ appendLog(JSON.parse(e.data)); }
    catch{ appendLog({raw:e.data}); }
  };
})();
