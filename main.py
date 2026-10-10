#!/usr/bin/env python3
"""
MeshPUL: Zero-config P2P Mesh Network Node & Gossip Broadcast CLI.
Built autonomously by Auto Qwen AI.
"""

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple


class MeshNode:
    """
    Decentralized asynchronous P2P mesh node using UDP gossip flooding.
    Supports peer discovery, heartbeat liveness, and multi-hop gossip messaging.
    """

    def __init__(self, node_id: str, host: str = "127.0.0.1", port: int = 9100, peers: Optional[List[str]] = None):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Set[Tuple[str, int]] = set()
        self.seen_messages: Set[str] = set()
        self.received_messages: List[dict] = []
        self._sock = None
        self._running = False

        if peers:
            for p in peers:
                self.add_peer(p)

    def add_peer(self, peer_str: str):
        try:
            parts = peer_str.strip().split(":")
            h = parts[0]
            p = int(parts[1]) if len(parts) > 1 else self.port
            if (h, p) != (self.host, self.port):
                self.peers.add((h, p))
        except Exception:
            pass

    async def start(self):
        loop = asyncio.get_running_loop()
        self._running = True

        # Async UDP endpoint
        class MeshProtocol(asyncio.DatagramProtocol):
            def __init__(self, node):
                self.node = node

            def datagram_received(self, data, addr):
                asyncio.create_task(self.node.handle_packet(data, addr))

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: MeshProtocol(self), local_addr=(self.host, self.port)
        )
        self._transport = transport
        print(f"[*] MeshNode '{self.node_id}' running on {self.host}:{self.port}")

        # Start background heartbeat
        asyncio.create_task(self._heartbeat_loop())

    async def stop(self):
        self._running = False
        if hasattr(self, "_transport") and self._transport:
            self._transport.close()

    async def _heartbeat_loop(self):
        while self._running:
            await asyncio.sleep(5)
            # Send PING to all known peers
            ping_pkt = json.dumps({"type": "PING", "sender": self.node_id, "host": self.host, "port": self.port}).encode()
            for h, p in list(self.peers):
                try:
                    self._transport.sendto(ping_pkt, (h, p))
                except Exception:
                    pass

    async def broadcast(self, payload_text: str) -> str:
        msg_id = str(uuid.uuid4())[:8]
        pkt_dict = {
            "type": "GOSSIP",
            "msg_id": msg_id,
            "origin": self.node_id,
            "ttl": 5,
            "content": payload_text,
            "timestamp": time.time(),
        }
        self.seen_messages.add(msg_id)
        raw = json.dumps(pkt_dict).encode("utf-8")

        for h, p in list(self.peers):
            try:
                self._transport.sendto(raw, (h, p))
            except Exception:
                pass
        return msg_id

    async def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        try:
            msg = json.loads(data.decode("utf-8"))
            mtype = msg.get("type")

            if mtype == "PING":
                sender_id = msg.get("sender")
                s_port = msg.get("port", addr[1])
                self.peers.add((addr[0], s_port))
                # Send PONG
                pong = json.dumps({"type": "PONG", "sender": self.node_id, "port": self.port}).encode()
                self._transport.sendto(pong, addr)

            elif mtype == "PONG":
                s_port = msg.get("port", addr[1])
                self.peers.add((addr[0], s_port))

            elif mtype == "GOSSIP":
                msg_id = msg.get("msg_id")
                if not msg_id or msg_id in self.seen_messages:
                    return

                self.seen_messages.add(msg_id)
                self.received_messages.append(msg)
                print(f"[>] Mesh Message [{msg_id}] from {msg.get('origin')}: {msg.get('content')}")

                # Re-broadcast (gossip relay) if TTL > 1
                ttl = msg.get("ttl", 1) - 1
                if ttl > 0:
                    msg["ttl"] = ttl
                    forward_bytes = json.dumps(msg).encode("utf-8")
                    for h, p in list(self.peers):
                        if (h, p) != addr:
                            self._transport.sendto(forward_bytes, (h, p))

        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="MeshPUL: Decentralized P2P Mesh Gossip CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    run_p = subparsers.add_parser("run", help="Start local mesh node")
    run_p.add_argument("--node-id", default=None, help="Unique identifier for this node")
    run_p.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    run_p.add_argument("--port", type=int, default=9100, help="UDP port to listen on")
    run_p.add_argument("--peer", action="append", default=[], help="Initial peer address (host:port)")

    args = parser.parse_args()

    if args.command == "run":
        nid = args.node_id or f"node_{os.getpid()}"
        node = MeshNode(node_id=nid, host=args.host, port=args.port, peers=args.peer)

        async def run_loop():
            await node.start()
            while True:
                await asyncio.sleep(1)

        try:
            asyncio.run(run_loop())
        except KeyboardInterrupt:
            print("\n[*] Mesh node stopped.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()