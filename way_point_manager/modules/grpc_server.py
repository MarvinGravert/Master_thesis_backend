import asyncio
from typing import Dict

from loguru import logger
import grpc
import grpc.experimental.aio

from holoViveCom_pb2 import (
    LighthouseState, Empty)
import holoViveCom_pb2_grpc

from config.api_types import VRObject, VRState
from config.const import (
    BACKEND_HOST, BACKEND_PORT
)


class ViveCommunicator(holoViveCom_pb2_grpc.BackendServicer):

    def __init__(self, IP: str, port: int, queue: asyncio.Queue) -> None:
        super().__init__()
        self._IP = IP
        self._port = port
        self._queue = queue

    async def start(self):
        logger.info(f"Async gRPC Server started on {self._IP}:{self._port}")
        grpc.experimental.aio.init_grpc_aio()  # initialize the main loop

        server = grpc.experimental.aio.server()

        server.add_insecure_port(f"{self._IP}:{self._port}")

        holoViveCom_pb2_grpc.add_BackendServicer_to_server(self, server)

        await server.start()
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            # Shuts down the server with 0 seconds of grace period. During the
            # grace period, the server won't accept new connections and allow
            # existing RPCs to continue within the grace period.
            await server.stop(0)

    async def PlaceWayPoint(self, request, context) -> Empty:
        """receives the controller pose when a button pressed (menu button)
        this is then put into the queue to be transformed into robot KOS
        """
        logger.info(f"waypoint: Received a connection from {context.peer()}")
        controller_obj = VRObject.set_pose_via_grpc_object(request.controller)
        logger.debug(f"Received: {controller_obj}")
        await self._queue.put(controller_obj)
        logger.info("Controller way point put into queue")
        return Empty()
