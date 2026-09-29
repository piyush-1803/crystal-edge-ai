# CRYSTAL — Local-First Edge AI Knowledge Network

> **TatHack '26 (Open Challenge)**  
> Autonomous, decentralized edge intelligence with hardware-isolated private memory and peer-synchronized network knowledge.

---

## 1. Overview

**Crystal** is a local-first, peer-to-peer Edge-AI architecture designed for laptops and edge devices. It enables personal computing devices to function as sovereign intelligent nodes capable of answering user queries using both **private personal memory** (which never leaves the physical device) and **explicitly shareable network knowledge** (synchronized across peer nodes over LAN).

Rather than treating a Large Language Model as an ungrounded or centralized knowledge store, Crystal treats the local model (**SmolLM2-135M-Instruct** running via **llama.cpp**) strictly as an **articulation and synthesis layer**. Factual answers are generated *exclusively* from retrieved context with full cryptographic and node provenance (`source_node_id`, `origin: local | peer`). When relevant context is absent, Crystal halts generation and returns a clear insufficient-context response, preventing ungrounded hallucinations.

---

## 2. Problem / Motivation

Modern AI applications suffer from two fundamental architectural flaws:
1. **Cloud Centralization & Privacy Invasion**: Personal context, documents, and chat histories are routinely uploaded to remote servers, exposing private user data to third-party surveillance, leaks, and vendor lock-in.
2. **Ungrounded Hallucinations**: Standard chatbots answer from static weights, blending fact with fiction, fabricating citations, and providing no audit trail of where facts originated.

Crystal solves both problems by bringing the entire retrieval, storage, and inference pipeline to the edge. Each user owns their physical node, personal memories remain strictly air-gapped on local disk, and knowledge sharing requires explicit opt-in over local-area networks.

---

## 3. Core Idea

Every Crystal node maintains two physically distinct storage compartments:
* **Private Personal Memory**: Belongs exclusively to that device. Stored in an isolated SQLite database (`private_memory.sqlite`). It is queried only locally by the node owner and is **never** accessible through remote network queries or peer APIs.
* **Explicitly Shareable Network Knowledge**: Contains knowledge items explicitly approved for discovery. Stored in `network_knowledge.sqlite`. When connected over LAN, peer nodes can discover, query, and synthesize this knowledge.

The local LLM acts solely as a **vocalizer / articulation engine**:
* It reads retrieved facts from Crystal's storage layers.
* It articulates natural-language answers strictly from that retrieved context.
* It attributes sources and origin (`local` vs. `peer`).

---

## 4. Architecture

```text
                           USER QUERY
                               │
                               ▼
                       ┌──────────────┐
                       │ Crystal Node │ (FastAPI on Port 8001 / 8002)
                       └───────┬──────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
 ┌──────────────────────┐              ┌──────────────────────┐
 │ Private Local Memory │              │ Shareable Knowledge  │
 │ (private_memory.db)  │              │ (network_knowl.db)   │
 └──────────────────────┘              └──────────┬───────────┘
   (Zero Network Access)                          │
                                        Peer Query over LAN
                                                  ▼
                                       ┌──────────────────────┐
                                       │ Connected Peer Nodes │ (Node A ↔ Node B)
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                      Retrieved Context + Provenance
                                      (source_node_id, origin: peer/local)
                                                  │
                                                  ▼
                                          Grounding Check
                                         (Has context found?)
                                         ├── NO  ──► Halt & Return "Insufficient Context"
                                         └── YES ──► Construct Strict Contextual Prompt
                                                           │
                                                           ▼
                                                ┌──────────────────────┐
                                                │ SmolLM2 (llama.cpp)  │ (127.0.0.1:8080)
                                                └──────────┬───────────┘
                                                           │
                                                           ▼
                                               Natural-Language Answer
                                              + Provenance Attribution
```

---

## 5. Privacy Boundary

Crystal's privacy architecture is enforced at both the storage and network layer:

* **Physical Database Isolation**:
  * Private memory is stored in `data/<node_id>/private/private_memory.sqlite`.
  * Shareable knowledge is stored in `data/<node_id>/shareable/network_knowledge.sqlite`.
  * There are no foreign keys, shared handles, or cross-database queries between them.
* **Network API Isolation**:
  * The network router exposes `POST /api/knowledge/query` and `POST /api/network/query`.
  * These endpoints query **only** the `NetworkKnowledgeService`.
  * There are **zero** network routes that touch or query `private_memory.sqlite`.
* **Zero Remote File System Access**: Peer nodes communicate exclusively via validated JSON HTTP payloads; Node B never directly accesses Node A's file system or databases.

---

## 6. Grounded AI

Crystal enforces grounded generation in `src/api/chat.py`:

1. **Context Retrieval**: On receiving a query, Crystal queries local private memory (for personal context) and the peer network (for shared domain knowledge).
2. **Grounding Validation**: If no matching records are retrieved, Crystal **blocks** model generation and immediately returns:
   > *"Insufficient retrieved context: no relevant local memory or network knowledge records were found for this query."*
   The model is never invoked to guess or invent ungrounded facts.
3. **Strict Articulation Prompt**: When context exists, prompt assembly wraps the retrieved text snippets and instructs the model:
   > *"Answer the question strictly and concisely using ONLY the provided context. If the answer cannot be found in the context, state that context is insufficient. Do not fabricate facts."*
4. **Provenance Tracking**: Every response returned to the frontend contains a `sources` array with `source_node_id`, `origin` (`local` or `peer`), and document `title`.

---

## 7. Node Architecture

For the TatHack '26 demonstration, Crystal runs as two independent nodes:

| Node | Name | Port | Storage Path | Peer Peering |
| :--- | :--- | :--- | :--- | :--- |
| **Node A** | Crystal Node A | `8001` | `./data/node_a` | Standalone Knowledge Provider |
| **Node B** | Crystal Node B | `8002` | `./data/node_b` | Peers with Node A (`127.0.0.1:8001`) |

Configurations:
* `config/demo_node_a.json`: Defines Node A on port 8001 with storage at `./data/node_a`.
* `config/demo_node_b.json`: Defines Node B on port 8002 with storage at `./data/node_b` and pre-configured peer link to Node A.

---

## 8. Project Structure

```text
crystal-edge-ai/
├── bin/                              # llama-server executable & MSVC runtime DLLs (ignored)
├── config/                           # Node configurations
│   ├── demo_node_a.json              # Node A config (Port 8001)
│   ├── demo_node_b.json              # Node B config (Port 8002, peers with Node A)
│   ├── node_a.json                   # Standard Node A config
│   ├── node_b.json                   # Standard Node B config
│   └── node_c.json                   # Auxiliary node config
├── data/                             # Isolated per-node storage compartments
│   ├── node_a/                       # Node A data directory
│   │   ├── private/                  # Node A private database (private_memory.sqlite)
│   │   └── shareable/                # Node A shareable database & ingested fixtures
│   │       └── articles/             # Tracked text article fixtures
│   └── node_b/                       # Node B data directory
│       ├── private/                  # Node B private database
│       └── shareable/                # Node B shareable database
├── models/                           # GGUF quantized models (ignored)
│   └── SmolLM2-135M-Instruct.Q4_K_M.gguf
├── src/                              # Core application source code
│   ├── api/                          # FastAPI REST routers
│   │   ├── chat.py                   # Grounded local chat endpoint (/api/chat)
│   │   ├── health.py                 # Node health check (/api/health)
│   │   ├── knowledge.py              # Public shareable knowledge query (/api/knowledge/query)
│   │   └── network.py                # Network scan, connect, and status (/api/network/*)
│   ├── inference/                    # Local AI inference services
│   │   └── local_model_service.py    # llama-server HTTP client & grounding interface
│   ├── ingestion/                    # Knowledge ingestion pipeline
│   │   └── article_ingester.py       # Ingests text files into shareable storage
│   ├── network/                      # Peer-to-peer transport & connection management
│   │   ├── connection_manager.py     # Session peer management & aggregated network search
│   │   └── peer_client.py            # Clean-failing HTTP peer client
│   ├── services/                     # Application domain services
│   │   ├── network_knowledge_service.py # Shareable knowledge operations
│   │   └── private_memory_service.py    # Private memory operations
│   ├── storage/                      # SQLite persistence repositories
│   │   ├── network_knowledge.py      # Network knowledge store
│   │   └── private_memory.py         # Private memory store
│   ├── config.py                     # NodeConfig dataclass & loader
│   ├── identity.py                   # Node identity dataclass
│   └── node.py                       # FastAPI application factory & CLI entrypoint
├── static/                           # Single-page web application frontend
│   ├── assets/
│   │   └── crystal-logo.png          # Transparent warm white & golden amber prism logo
│   └── index.html                    # Editorial interface with Dark Mode & multi-node tabs
├── tests/                            # Automated test suite (34 tests)
│   ├── test_api_privacy.py           # Privacy boundary & route exposure tests
│   ├── test_chat_api.py              # Grounded generation, provenance, & unique fact tests
│   ├── test_config.py                # Configuration loading tests
│   ├── test_frontend.py              # UI serving, logo asset, & dark mode tests
│   ├── test_health.py                # Health endpoint tests
│   ├── test_identity.py              # Node identity tests
│   ├── test_ingestion.py             # Knowledge ingestion tests
│   ├── test_knowledge_api.py         # Shareable knowledge API tests
│   ├── test_multi_node.py            # Multi-node configuration tests
│   ├── test_network_interface.py     # Network connect & lifecycle tests
│   ├── test_network_knowledge.py     # Shareable storage CRUD tests
│   ├── test_private_memory.py        # Private memory CRUD tests
│   ├── test_services.py              # Domain service isolation tests
│   └── test_storage_isolation.py     # Physical database file isolation tests
├── .gitignore                        # Git exclusion rules (ignores models, dbs, binaries)
├── crystal.spec                      # PyInstaller packaging specification
├── requirements.txt                  # Python dependencies
├── run_crystal.py                    # Packaged standalone launcher & desktop wrapper
└── README.md                         # Project documentation
```

---

## 9. Requirements

* **Operating System**: Windows 10/11 x64 (tested and verified on Windows 11).
* **Python**: Python 3.10 to 3.14 (verified on Python 3.14.6).
* **Local LLM Runtime**: Official `llama.cpp` Windows x64 CPU binary (`llama-server.exe`).
* **Model**: `SmolLM2-135M-Instruct.Q4_K_M.gguf` (135M parameters, Q4_K_M quantized, ~105 MB).

---

## 10. Installation

### 1. Clone the Repository
```powershell
git clone https://github.com/piyush-1803/crystal-edge-ai.git
cd crystal-edge-ai
```

### 2. Create and Activate Virtual Environment
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 11. Running Node A

Start Node A on port 8001:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m src.node --config config/demo_node_a.json
```
* **URL**: `http://127.0.0.1:8001/`
* **Health Check**: `http://127.0.0.1:8001/api/health`

---

## 12. Running Node B

In a separate terminal, start Node B on port 8002:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m src.node --config config/demo_node_b.json
```
* **URL**: `http://127.0.0.1:8002/`
* **Health Check**: `http://127.0.0.1:8002/api/health`

---

## 13. Running Local AI Runtime

Launch `llama-server.exe` with SmolLM2 on port 8080:
```powershell
.\bin\llama-server.exe -m models\SmolLM2-135M-Instruct.Q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 2048
```
* **Endpoint**: `http://127.0.0.1:8080/health`
* Crystal's `LocalModelService` automatically connects to `http://127.0.0.1:8080/completion`.

---

## 14. Running the Packaged Application

Crystal includes a standalone PyInstaller build specification (`crystal.spec`).

Build the executable:
```powershell
.\.venv\Scripts\pyinstaller.exe crystal.spec --noconfirm
```
Run the packaged binary:
```powershell
# Run Node A
.\dist\crystal\crystal.exe --config config/demo_node_a.json --headless

# Run Node B
.\dist\crystal\crystal.exe --config config/demo_node_b.json --headless
```

---

## 15. Testing

Execute the complete automated test suite:
```powershell
.\.venv\Scripts\pytest.exe -v
```

**Verified Test Result**:
```text
34 passed, 1 warning in 3.25s (100% pass rate)
```

Test coverage includes:
* **Storage Isolation**: Verifies physical separation of `private_memory.sqlite` and `network_knowledge.sqlite`.
* **API Privacy**: Confirms zero network routes expose private memory.
* **Network Query**: Verifies remote peer search over LAN with attribution.
* **Grounded Chat**: Proves local LLM only articulates retrieved facts and returns insufficient context when no facts are found.
* **Unique Fact Provenance**: Tests synthetic fact retrieval across nodes (`AURORA-7429`).
* **Frontend & Dark Mode**: Verifies UI assets, transparent warm logo, and dark mode toggling.

---

## 16. Manual Demo: Grounded Peer Knowledge Retrieval

Follow this factual demonstration script for judges:

### Step 1: Start the Runtimes
1. Start `llama-server.exe` on port `8080`.
2. Start Node A on port `8001`.
3. Start Node B on port `8002`.

### Step 2: Open Node B
Navigate to `http://127.0.0.1:8002/` in your browser. Verify the UI identifies itself as **Crystal Node B** and the Network tab shows Node A connected.

### Step 3: Query the Unique Peer Fact
Ask Node B:
> *"What is the Crystal demo codename?"*

**Observed Result**:
* **Answer**: `"The Crystal demo codename is 'AURORA-7429'."`
* **Sources**: Identifies `source_node_id: node-a`, `origin: peer`, `title: Demo Codename`.
* **Network Indicator**: `network_used: true`.

### Step 4: Disconnect Node A
In Node B's Network interface (or via API), disconnect Node A:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/network/disconnect" -Method Post `
  -ContentType "application/json" -Body '{"node_id":"node-a"}'
```

### Step 5: Ask Again (Failure-Safe Grounding)
Ask Node B again:
> *"What is the Crystal demo codename?"*

**Observed Result**:
* **Answer**: `"Insufficient retrieved context: no relevant local memory or network knowledge records were found for this query."`
* **Sources**: `[]`.
* **Network Indicator**: `network_used: false`.
* **Conclusion**: The model **refuses** to hallucinate or guess without retrieved context.

### Step 6: Reconnect Node A
Reconnect Node A:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/network/connect" -Method Post `
  -ContentType "application/json" -Body '{"host":"127.0.0.1","port":8001,"node_id":"node-a"}'
```
Ask the query a third time; the answer `"AURORA-7429"` is retrieved and articulated once again.

---

## 17. API Reference

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/api/health` | `GET` | Health check probe returning node status, ID, and name. |
| `/api/chat` | `POST` | Grounded chat endpoint: retrieves local/peer context and articulates response via local LLM. |
| `/api/knowledge/query` | `POST` | Public shareable knowledge query. Queries strictly `network_knowledge.sqlite`. |
| `/api/network/status` | `GET` | Returns active transport type (`local_lan`), identity, and connected peer list. |
| `/api/network/scan` | `POST` | Scans local subnet candidate IPs via `/api/health` probes. |
| `/api/network/connect` | `POST` | Initiates real connection handshake with a target peer. |
| `/api/network/disconnect` | `POST` | Disconnects an active peer from the session. |
| `/api/network/query` | `POST` | Aggregates shareable search across local storage and all connected peers. |

---

## 18. Packaging

Crystal packages as a standalone Windows application using PyInstaller:
```powershell
.\.venv\Scripts\pyinstaller.exe crystal.spec --noconfirm
```
Output directory: `dist/crystal/`
* Bundles the Crystal application runtime, web frontend (`static/`), default configurations (`config/`), and article fixtures.
* Runtime SQLite databases and GGUF model files remain external to ensure complete data sovereignty and avoid accidental data bundling.

---

## 19. Privacy and Security

* **No Cloud Telemetry**: Zero network requests are made to third-party APIs, analytics, or cloud inference providers.
* **Isolated Private Storage**: Personal memories are inaccessible from any public or peer network route.
* **Explicit Sharing Model**: Knowledge must be ingested with `is_shareable = True` to participate in the network knowledge layer.
* **Sovereign Encryption Ready**: Because storage uses standard isolated SQLite files, volumes can be encrypted using OS-level BitLocker or SQLCipher.

---

## 20. Hackathon Demo Value

Crystal demonstrates the viability of a **post-cloud, decentralized AI future**:
* Proves that small, quantized models (135M parameters) running locally on commodity CPU can provide high-quality responses when paired with precise edge retrieval.
* Eliminates cloud operational costs and token pricing.
* Guarantees total data privacy and sovereignty for users.
* Solves the hallucination problem via application-level grounding constraints.

---

## 21. Limitations & Future Work

* **Context Window**: Current local runtime uses a 2048-token context window; long documents are automatically truncated to fit.
* **Keyword Matching**: Retrieval uses SQLite `LIKE` substring search; future iterations will integrate local vector embeddings (e.g. `all-MiniLM-L6-v2`) via SQLite-VSS.
* **Transport Protocol**: Current transport uses HTTP over LAN; Bluetooth Low Energy (BLE) and Wi-Fi Direct transports are architectural roadmap items.

---

## 22. License / Credits

Developed for **TatHack '26 — PS8 (Open Challenge)**.
* **Team**: Crystal Edge-AI Team
* **License**: MIT License
