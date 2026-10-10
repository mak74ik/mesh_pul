# MeshPUL (`mesh_pul`)

> **Decentralized asynchronous P2P Mesh Network Node & Gossip Flooding CLI.**  
> Built and tested autonomously by **Auto Qwen AI**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/mak74ik/mesh_pul/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 🌟 Overview

`MeshPUL` creates a decentralized, zero-dependency peer-to-peer mesh network between machines. Nodes connect, exchange heartbeats, discover topology, and broadcast messages across multi-hop relay links using TTL-scoped gossip flooding.

---

## 🚀 Usage

### 1. Start Node 1 (Bootstrap Node)
```bash
python3 main.py run --node-id node1 --port 9101
```

### 2. Start Node 2 (Connected to Node 1)
```bash
python3 main.py run --node-id node2 --port 9102 --peer 127.0.0.1:9101
```

### 3. Start Node 3 (Connected to Node 2)
```bash
python3 main.py run --node-id node3 --port 9103 --peer 127.0.0.1:9102
```

Packets broadcast from `node1` will automatically relay through `node2` and reach `node3` with zero central servers.

---

## 🧪 Testing

Run multi-hop gossip relay integration tests:
```bash
python3 -m unittest discover -s tests
```

---

## 👥 Credits

Developed autonomously by **Auto Qwen AI**:
- 🤖 **Autonomous Engine**: Auto Qwen AI Pipeline
- 🌐 **Protocol**: Decentralized UDP Gossip Flooding with TTL Relay
- 🛡️ **Quality Assurance**: Automated Multi-Hop Network Tests
