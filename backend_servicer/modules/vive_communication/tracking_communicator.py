from dataclasses import dataclass
import asyncio
from typing import Dict, List

from loguru import logger
import grpc
import grpc.experimental.aio

import holoViveCom_pb2
import holoViveCom_pb2_grpc

from api.general_types import ServerState
from config.const import (
    WAYPOINT_MANAGER_HOST, WAYPOINT_MANAGER_PORT
)

from api.general_types import (
    Controller, Trackable, TrackableFactory, Tracker, ServerState, Command
)


class TrackingCommunicator(holoViveCom_pb2_grpc.BackendServicer):

    def __init__(self, IP: str, port: int, server_state: ServerState) -> None:
        super().__init__()
        self._IP = IP
        self._port = port
        self.server_state = server_state  # TODO: Look into singleton pattern for python

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

    async def Report(self, stream, context) -> holoViveCom_pb2.Empty:
        """receives updates about all the connected VRObjects and updates
        internal state

        Data is streamed in continously
        """
        logger.info(f"Received a connection from {context.peer()}")
        factory = TrackableFactory()
        async for part in stream:
            logger.debug(f"Received information {part}")
            trackable_list = factory.generateTrackables(grpc_message=part)
            # using trackables keyed by name
            # new trackables are written into list, existing ones are overwritten
            for trackable in trackable_list:
                self.server_state.message_obj_dict[trackable.name] = trackable

        return holoViveCom_pb2.Empty()

    async def SendCommand(self, request, context) -> holoViveCom_pb2.Empty:
        """Receive command and write into message_obj_dict
        """
        logger.info(f"Received a connection from {context.peer()}")
        self.server_state.message_obj_dict["command"] = Command(command=request.command)
        logger.info(f"New Command has been issued: {self.server_state.status}")
        return holoViveCom_pb2.Empty()
