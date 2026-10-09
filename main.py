import argparse
import asyncio
import dataclasses
import os
from typing import List

from nautilus import Node, Network

@dataclasses.dataclass
class MeshConfig:
    network_id: str
    node_id: str
    peers: List[str]

async def create_mesh(config: MeshConfig):
    node = Node(network_id=config.network_id, node_id=config.node_id)
    network = Network(node=node)
    await network.join(config.peers)
    return network

async def main():
    parser = argparse.ArgumentParser(description='Mesh PUL CLI utility')
    parser.add_argument('--start', action='store_true', help='Start mesh network')
    parser.add_argument('--config', type=str, help='Path to mesh configuration file')
    args = parser.parse_args()

    if args.start:
        if not args.config:
            print('Error: configuration file is required')
            return

        config = MeshConfig(
            network_id='my_network',
            node_id='node_1',
            peers=['node_2', 'node_3']
        )
        network = await create_mesh(config)
        print('Mesh network started')

    else:
        print('Error: start command is required')

if __name__ == '__main__':
    asyncio.run(main())