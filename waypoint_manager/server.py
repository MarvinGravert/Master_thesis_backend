import asyncio

from loguru import logger

from modules.worker import WorkerClass
from modules.async_tcp_ip_server import TcpIPServer
from modules.grpc_server import ViveCommunicator
from config.api_types import ServerState
from config.const import (
    TCP_HOST, WAYPOINT_MANAGER_TCP_PORT, GRPC_HOST, WAYPOINT_MANAGER_GRPC_PORT
)


async def main():
    server_state = ServerState()
    queue = asyncio.Queue()
    tcp_host = TCP_HOST
    tcp_port = WAYPOINT_MANAGER_TCP_PORT
    tcp_server = TcpIPServer(IP=tcp_host, port=tcp_port, queue=queue)
    grpc_host = GRPC_HOST
    grpc_port = WAYPOINT_MANAGER_GRPC_PORT
    grpc_server = ViveCommunicator(IP=grpc_host, port=grpc_port,
                                   queue=queue, server_state=server_state)
    await asyncio.gather(grpc_server.start(), tcp_server.start(), WorkerClass().worker(queue=queue, server_state=server_state))

if __name__ == "__main__":
    logger.info("Starting HoloCalibration Service")

    asyncio.run(main())
