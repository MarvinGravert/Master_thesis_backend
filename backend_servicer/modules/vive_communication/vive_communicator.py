
from typing import List

import numpy as np
from loguru import logger
import grpc
import grpc.experimental.aio


from holoViveCom_pb2 import (
    LighthouseState, CalibrationInfo, Quaternion,
    HandheldController, TrackerState, Status, Tracker)
import holoViveCom_pb2_grpc

from config.api_types import VRState


class ViveCommunicator(holoViveCom_pb2_grpc.BackendServicer):

    def __init__(self, IP: str, port: int, vr_state: VRState) -> None:
        super().__init__()
        self._IP = IP
        self._port = port
        self._vr_state = vr_state

    async def start(self):
        logger.info("Server started")
        grpc.experimental.aio.init_grpc_aio()  # initialize the main loop

        server = grpc.experimental.aio.server()

        server.add_insecure_port(f"{self._IP}:{self._port}")

        holoViveCom_pb2_grpc.add_BackendServicer_to_server(

            self, server

        )

        await server.start()

        await server.wait_for_termination()

    async def LighthouseReport(self, request, context) -> Status:
        """receives update about all the connected VRObjects and update
        internal state

        Data is streamed in continously. If the client ends the stream a
        status message is sent

        Args:
            request ([type]): [description]
            context ([type]): [description]

        Returns:
            Status: [description]
        """
        logger.info(f"Received a connection from {context.peer()}")
        async for part in request:
            logger.debug("Received information update")
            self._vr_state.update_state(part)

        return Status()

    async def ProvideTrackerInfo(self, request, context) -> TrackerState:
        """returns information regarding tracker currently registered with the server

        this is a unary unary RPC the incoming message is irrelevant to us

        waits until tracker has been set before returning information
        Args:
            request ([type]): [description]
            context ([type]): [description]

        Returns:
            TrackerState: [description]
        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.info("Providing Information about Trackers")
        await self._vr_state._holo_tracker_set_event.wait()
        await self._vr_state._calibration_tracker_set_event.wait()
        logger.info("Collected all information about trackers, returning data")
        return TrackerState(
            holoTracker=self._vr_state.holo_tracker.get_as_grpc_object(),
            caliTracker=self._vr_state.calibration_tracker.get_as_grpc_object())

    async def UpdateCalibrationInfo(self, request, context):
        return super().UpdateCalibrationInfo(request, context)
