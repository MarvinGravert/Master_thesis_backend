import time
import asyncio

import grpc
import grpc.experimental.aio
from loguru import logger

from holoViveCom_pb2 import (
    LighthouseState, TrackerState, CalibrationInfo,
)
import holoViveCom_pb2_grpc


from config.const import (
    TCP_HOST, TCP_PORT, GRPC_HOST, GRPC_PORT
)
from config.api_types import VRState
from modules.holo_communication.async_tcp_ip_server import TcpIPServer
from modules.vive_communication.vive_communicator import ViveCommunicator


async def main():
    vr_state = VRState()  # keep track of server state across the two interfaces
    tcp_server = TcpIPServer(IP=TCP_HOST, port=TCP_PORT, vr_state=vr_state)
    grpc_server = ViveCommunicator(IP=GRPC_HOST, port=GRPC_PORT, vr_state=vr_state)
    await asyncio.gather(grpc_server.start(), tcp_server.start())


if __name__ == "__main__":
    logger.info("Starting Async backend server")
    asyncio.run(main())
