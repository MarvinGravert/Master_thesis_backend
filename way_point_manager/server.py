import asyncio

from loguru import logger

from modules.worker import worker
from modules.async_tcp_ip_server import TcpIPServer
from config.const import TCP_HOST, WAYPOINT_MANAGER_PORT


async def main():
    queue = asyncio.Queue()
    tcp_host = TCP_HOST
    tcp_port = WAYPOINT_MANAGER_PORT
    tcp_server = TcpIPServer(IP=tcp_host, port=tcp_port, queue=queue)
    await asyncio.gather(tcp_server.start(), worker(queue))

if __name__ == "__main__":
    logger.info("Starting HoloCalibration Service")

    asyncio.run(main())
