import asyncio
import sys

from loguru import logger

from config.const import (
    TCP_HOST, TCP_PORT, GRPC_HOST, GRPC_PORT
)
from api.general_types import ServerState
from modules.holo_communication.async_tcp_ip_server import TcpIPServer
from modules.vive_communication.tracking_communicator import TrackingCommunicator


async def main():
    server_state = ServerState()  # keep track of server state across the two interfaces
    tcp_server = TcpIPServer(IP=TCP_HOST, port=TCP_PORT, server_state=server_state)
    grpc_server = TrackingCommunicator(IP=GRPC_HOST, port=GRPC_PORT, server_state=server_state)
    await asyncio.gather(grpc_server.start(), tcp_server.start())

if __name__ == "__main__":
    logger.info("Starting Async backend server")
    logger.remove()
    logger.add(sink=sys.stderr, level="DEBUG")
    asyncio.run(main())
