import asyncio

from loguru import logger

from modules.worker import WorkerClass
from modules.async_tcp_ip_server import TcpIPServer

from config.api_types import ServerState
from config.const import (
    TCP_HOST, WAYPOINT_MANAGER_TCP_PORT
)


async def main():
    server_state = ServerState()
    queue = asyncio.Queue()
    tcp_server = TcpIPServer(IP=TCP_HOST, port=WAYPOINT_MANAGER_TCP_PORT, queue=queue)
    await asyncio.gather(tcp_server.start(), WorkerClass().worker(queue=queue, server_state=server_state))

if __name__ == "__main__":
    logger.info("Starting Waypoint Service")

    asyncio.run(main())
