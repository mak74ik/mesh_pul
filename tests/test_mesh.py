import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import MeshNode


class TestMeshNetwork(unittest.IsolatedAsyncioTestCase):
    async def test_multihop_gossip_propagation(self):
        # Create 3 nodes: NodeA (19101) <-> NodeB (19102) <-> NodeC (19103)
        # NodeA is NOT directly connected to NodeC!
        node_a = MeshNode(node_id="NodeA", host="127.0.0.1", port=19101, peers=["127.0.0.1:19102"])
        node_b = MeshNode(node_id="NodeB", host="127.0.0.1", port=19102, peers=["127.0.0.1:19101", "127.0.0.1:19103"])
        node_c = MeshNode(node_id="NodeC", host="127.0.0.1", port=19103, peers=["127.0.0.1:19102"])

        await node_a.start()
        await node_b.start()
        await node_c.start()

        # NodeA broadcasts message "Hello Mesh Multihop"
        msg_id = await node_a.broadcast("Hello Mesh Multihop")

        # Allow network time for gossip relay through NodeB to NodeC
        for _ in range(20):
            await asyncio.sleep(0.1)
            if any(m.get("msg_id") == msg_id for m in node_c.received_messages):
                break

        # Check that NodeC received the message via NodeB
        self.assertTrue(
            any(m.get("msg_id") == msg_id for m in node_c.received_messages),
            f"NodeC failed to receive gossiped message from NodeA! Received: {node_c.received_messages}",
        )

        await node_a.stop()
        await node_b.stop()
        await node_c.stop()


if __name__ == "__main__":
    unittest.main()
