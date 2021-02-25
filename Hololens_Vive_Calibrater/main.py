import asyncio

from loguru import logger

from modules.holo_communication.async_tcp_ip_server import TcpIPServer
from config.const import (
    TCP_HOST, TCP_PORT
)


async def main():

    tcp_server = TcpIPServer(IP=TCP_HOST, port=TCP_PORT)
    await asyncio.gather(tcp_server.start())

if __name__ == "__main__":
    tcp_server = TcpIPServer(IP=TCP_HOST, port=TCP_PORT)
    logger.info(f"Starting HoloCalibration Server on {TCP_HOST}:{TCP_PORT}")
    asyncio.run(main())
