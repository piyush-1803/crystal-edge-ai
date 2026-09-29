# Crystal

Crystal is a distributed edge-AI architecture in which independent computing nodes can maintain local private memory while participating in a shared network knowledge layer. Designed for TatHack '26 PS8 (Open Challenge), Crystal enables edge devices (such as ordinary laptops) to function as intelligent nodes while giving users complete ownership over their private personal memory.

---

## Current Stage & Foundation MVP

> **Node-to-Node Shareable Knowledge API and Peer Client implemented.** Node B can now send queries to Node A over HTTP/LAN and retrieve Node A's shareable knowledge with full source attribution, while Node A's private memory remains completely unexposed.

---

## Architecture Overview

```text
Laptop B (Node B)                                     Laptop A (Node A)
┌────────────────────────┐                             ┌────────────────────────┐
│  PeerClient            │  POST /api/knowledge/query  │  FastAPI Runtime       │
│  (src/network/)        ├────────────────────────────►│  (src/node.py)         │
└────────────────────────┘    (HTTP Query over LAN)    └───────────┬────────────┘
                                                                   │
                                                                   ▼
                                                       NetworkKnowledgeService
                                                       (src/services/)
                                                                   │
                                                                   ▼
                                                       NetworkKnowledgeStore
                                                       (network_knowledge.sqlite)
```

---

## Key Components

### 1. Current Node Runtime (`src/node.py`)
Built using Python 3.14 + FastAPI + Uvicorn. Implements node startup, configuration loading, identity initialization, health endpoint (`GET /api/health`), and shareable knowledge query endpoint (`POST /api/knowledge/query`).

### 2. Configuration-Driven Node Identity & Peers (`src/config.py`, `src/identity.py`)
Nodes are identified dynamically via JSON configuration files or environment variables (`node_id`, `node_name`, `host`, `port`, `data_directory`, `peers`). Pre-configured files:
* `config/node_a.json` (Port 8001)
* `config/node_b.json` (Port 8002, configured with Node A peer)
* `config/node_c.json` (Port 8003)

### 3. Shareable Knowledge API (`POST /api/knowledge/query`)
Public REST endpoint (`src/api/knowledge.py`) allowing peer nodes to query explicitly shareable network knowledge (`is_shareable = True`).
* **Request**: `{"query": "quantum computing"}`
* **Response**: `{"results": [{"id": "...", "content": "...", "source_node_id": "node-a", "is_shareable": true}]}`
* **Privacy Guarantee**: Queries **ONLY** `network_knowledge.sqlite`. Has zero access to `private_memory.sqlite`.

### 4. HTTP Peer Client (`src/network/peer_client.py`)
Reusable `PeerClient` allowing Node B to query a target peer node over HTTP/LAN. Parses results and fails cleanly (returns empty list) if the peer is offline or unreachable.

### 5. Private Personal Memory (`src/storage/private_memory.py`)
SQLite database file (`private_memory.sqlite`) storing local, private user facts and notes. Has zero network route exposure.

### 6. Separation Between Private Memory & Network Knowledge
Physical database file separation and application-level service separation ensure that network handlers cannot query private memory. **Network knowledge is intentionally separated from private personal memory so peer requests access only explicitly shareable knowledge.**

---

## Physical Node Model

**Each physical laptop runs an independent Crystal node.**

When deployed across multiple laptops on a local network, each laptop runs its own instance of the node software:

```text
Laptop A (192.168.1.10)              Laptop B (192.168.1.11)
Crystal Node A                        Crystal Node B
├── Config (node_id: node-a)          ├── Config (node_id: node-b)
├── Data Dir (./data/node_a/)         ├── Data Dir (./data/node_b/)
├── Private Memory (Local Only)       ├── Private Memory (Local Only)
└── Network Knowledge (Shareable)     └── Network Knowledge (Shareable)
```

---

## Setup & Environment

1. Ensure Python 3.14+ is installed.
2. Create and activate a Python virtual environment:

```bash
py -3 -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running Tests

Run the complete automated test suite (24 unit/integration tests):

```bash
pytest
```

---

## Running Crystal

### Option A: Running From Source

1. Activate your virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the node:
```bash
python run_crystal.py --config config/node_a.json
```
or via module:
```bash
python -m src.node --config config/node_a.json
```

3. Open the web workspace at `http://localhost:8001/`.

---

### Option B: Running the Packaged Executable

A standalone Windows bundle is built inside `dist/crystal/` requiring no pre-installed Python environment:

1. Launch Node A:
```powershell
.\dist\crystal\crystal.exe --config config/node_a.json --port 8001
```

2. Access the frontend in your browser:
```text
http://127.0.0.1:8001/
```

To build or rebuild the package locally:
```powershell
pip install pyinstaller
pyinstaller --name crystal --onedir --clean --add-data "static;static" --add-data "config;config" run_crystal.py
```

---

## Deploying & Running on Node B (Second Machine)

To test multi-node networking across physical or virtual machines:

1. **Install/Deploy on Node B**:
   - Copy the `dist/crystal` folder (or clone this repository and set up environment) on the second machine.
   - **Important**: Node B must have the Crystal node application actively installed and running for Crystal discovery and peer connections to succeed.

2. **Start Node B**:
```powershell
.\dist\crystal\crystal.exe --config config/node_b.json --port 8002
```
*(Or specify the remote host binding explicitly, e.g. `--host 0.0.0.0 --port 8002`)*

3. **Connect From Node A**:
   - In Node A's web interface (`http://localhost:8001/`), navigate to the **Network** view.
   - Use the **Connect to Specific IP / Port** form to enter Node B's LAN IP address and port (e.g. `192.168.1.X:8002`) and click **Connect**.
   - Once connected, both nodes will share and search designated shareable network knowledge while keeping local private memory strictly isolated.

> **Note on LAN Discovery**: Automatic same-machine loopback discovery is verified. For two separate physical computers on LAN, peer endpoints can be linked by specifying the target IP in `config/node_*.json` or through the Network interface manual connection input. Zero-configuration UDP broadcast discovery across physical subnets is undergoing active validation.

---

## Web Frontend & Cognitive Workspace

Crystal includes an editorial ambient web interface matching the design specifications:
* Warm slate/ivory canvas with Georgia & JetBrains Mono typography
* Edge-aware Chat Interface with memory integration cards and suggestion chips
* Network Interface with Click-to-Connect and federated knowledge retrieval
* Direct integration with `GET /api/health` and shareable knowledge queries
* Responsive layout supporting desktop and mobile drawer navigation

---

## Current Status & Next Steps

* **Verified**: Same-machine multi-node connectivity (`127.0.0.1:8001` ↔ `127.0.0.1:8002`), Click-to-Connect UI, storage isolation, and standalone Windows packaging.
* **In Progress**: Physical two-laptop Wi-Fi LAN discovery and broadcast beacon protocol.


