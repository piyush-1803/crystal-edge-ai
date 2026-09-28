# Crystal

Crystal is a distributed edge-AI architecture in which independent computing nodes can maintain local private memory while participating in a shared network knowledge layer. Designed for TatHack '26 PS8 (Open Challenge), Crystal enables edge devices (such as ordinary laptops) to function as intelligent nodes while giving users complete ownership over their private personal memory.

---

## Current Stage & Foundation MVP

> **This repository contains the FOUNDATION / MVP architecture for a Crystal Node.** Physical laptop-to-laptop networking, distributed retrieval, and AI orchestration are future implementation stages.

---

## Architecture Overview

```text
Crystal Application
        ↓
Crystal Node (`src/node.py`)
        ↓
Service Layer (`src/services/`)
   ├── PrivateMemoryService (`src/services/private_memory_service.py`)
   └── NetworkKnowledgeService (`src/services/network_knowledge_service.py`)
        ↓
Private Memory / Network Knowledge (`src/storage/`)
   ├── Private Memory (`private_memory.sqlite`)        <-- LOCAL ONLY
   └── Network Knowledge (`network_knowledge.sqlite`)   <-- SHAREABLE
        ↓
Transport Boundary (`src/transport/base.py`)
        ↓
Future LAN / BLE / Mesh Transports
```

---

## Key Components

### 1. Current Node Runtime (`src/node.py`)
Built using Python 3.14 + FastAPI + Uvicorn. Implements node startup, configuration loading, identity initialization, and a health endpoint (`GET /api/health`).

### 2. Configuration-Driven Node Identity (`src/config.py`, `src/identity.py`)
Nodes are identified dynamically via JSON configuration files or environment variables (`node_id`, `node_name`, `host`, `port`, `data_directory`). Pre-configured files are provided for dev testing:
* `config/node_a.json` (Port 8001)
* `config/node_b.json` (Port 8002)
* `config/node_c.json` (Port 8003)

### 3. Private Personal Memory (`src/storage/private_memory.py`)
SQLite database file (`private_memory.sqlite`) storing local, private user facts and notes. Has zero network route exposure.

### 4. Shareable Network Knowledge (`src/storage/network_knowledge.py`)
SQLite database file (`network_knowledge.sqlite`) storing documents explicitly marked as shareable (`is_shareable = True`). Preserves source node attribution (`source_node_id`).

### 5. Separation Between Private Memory & Network Knowledge
Physical database file separation and application-level service separation ensure that network handlers cannot query private memory. **Network knowledge is intentionally separated from private personal memory so future peer requests can access only explicitly shareable knowledge.**

### 6. Service Layer (`src/services/`)
`PrivateMemoryService` and `NetworkKnowledgeService` provide isolated application methods for reading, writing, and searching local data compartments.

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

No node shares a database file or storage directory with another node.

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

Run the complete automated test suite (15 unit tests):

```bash
pytest
```

---

## Starting a Node

To start a single Crystal node using default configuration (Node A on port 8001):

```bash
python -m src.node
```

Or specify an explicit configuration file:

```bash
python -m src.node --config config/node_a.json
```

---

## Health Check

Send a GET request to the node's health endpoint:

```bash
curl http://127.0.0.1:8001/api/health
```

Example JSON response:

```json
{
  "status": "ok",
  "node_id": "node-a",
  "node_name": "Crystal Node A"
}
```

---

## Current Limitations & Future Work

The following capabilities are **NOT YET IMPLEMENTED** in this foundation milestone:

* Physical laptop-to-laptop networking
* LAN peer communication
* Automatic peer discovery
* Distributed knowledge retrieval
* AI orchestration
* Bluetooth / Mesh transport

These features will be introduced in subsequent architectural prompts.
