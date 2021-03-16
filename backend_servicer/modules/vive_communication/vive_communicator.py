
from typing import List
import asyncio

import numpy as np
from loguru import logger
import grpc
import grpc.experimental.aio


from holoViveCom_pb2 import (
    LighthouseState, CalibrationInfo, Quaternion,
    HandheldController, Status, Tracker, Empty)
import holoViveCom_pb2_grpc

from config.api_types import VRState


class ViveCommunicator(holoViveCom_pb2_grpc.BackendServicer):

    def __init__(self, IP: str, port: int, vr_state: VRState) -> None:
        super().__init__()
        self._IP = IP
        self._port = port
        self._vr_state = vr_state

    async def start(self):
        logger.info(f"Async gRPC Server started on {self._IP}:{self._port}")
        grpc.experimental.aio.init_grpc_aio()  # initialize the main loop

        server = grpc.experimental.aio.server()

        server.add_insecure_port(f"{self._IP}:{self._port}")

        holoViveCom_pb2_grpc.add_BackendServicer_to_server(

            self, server

        )

        await server.start()
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            # Shuts down the server with 0 seconds of grace period. During the
            # grace period, the server won't accept new connections and allow
            # existing RPCs to continue within the grace period.
            await server.stop(0)

    async def LighthouseReport(self, stream, context) -> Status:
        """receives update about all the connected VRObjects and update
        internal state

        Data is streamed in continously. If the client ends the stream a
        status message is sent
        """
        logger.info(f"Received a connection from {context.peer()}")

        async for part in stream:
            logger.debug(f"Received information {part}")
            # Holo Tracker
            if part.HasField("holoTracker"):
                if self._vr_state._holo_tracker_set_event.is_set():
                    self._vr_state.update_holo_tracker(part.holoTracker)
                else:
                    self._vr_state.init_holo_tracker(part.holoTracker)
            # Calibration Tracker
            if part.HasField("caliTracker"):
                if self._vr_state._calibration_tracker_set_event.is_set():
                    self._vr_state.update_calibration_tracker(part.caliTracker)
                else:
                    self._vr_state.init_calibration_tracker(part.caliTracker)
            # Controller
            if part.HasField("controller"):
                if self._vr_state._controller_set_event.is_set():
                    self._vr_state.update_controller(part.controller)
                else:
                    self._vr_state.init_controller(part.controller)
            # tell subscribers about an update in data
            # problem here=>update is triggered if maybe only device is detected
            if part is not None:
                for event in self._vr_state.new_state_subscriber.values():
                    event.set()
        return Status()

    async def ProvideLighthouseState(self, request, context):
        """returns information regarding tracker currently registered with the server

        this is a unary unary RPC the incoming message is irrelevant to us

        waits until tracker has been set before returning information
        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Checking if both trackers have been initialized")
        num_uniq_states: int = request.numberSamples
        client_id = str(context.peer())
        self._vr_state.new_state_subscriber[client_id] = asyncio.Event()
        await self._vr_state._holo_tracker_set_event.wait()
        await self._vr_state._calibration_tracker_set_event.wait()
        await self._vr_state._controller_set_event.wait()
        logger.info(f"Trackers are ready. Startin to assemble {num_uniq_states} unique data")
        for _ in range(num_uniq_states):
            # wait until a new state arrives
            await self._vr_state.new_state_subscriber[client_id].wait()
            self._vr_state.new_state_subscriber[client_id].clear()
            logger.debug("yielding new tracker information")
            yield LighthouseState(
                controller=self._vr_state.controller.get_as_grpc_object(),
                holoTracker=self._vr_state.holo_tracker.get_as_grpc_object(),
                caliTracker=self._vr_state.calibration_tracker.get_as_grpc_object())
        logger.debug(f"Connection {client_id} done. Cleaning up")
        del self._vr_state.new_state_subscriber[client_id]

    async def UpdateCalibrationInfo(self, request, context) -> Empty:
        """receives calibration and updates internal calibration


        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Processing received calibration update")
        self._vr_state.calibration.set_calibration_via_grpc_object(request)
        logger.info("New calibration has been set and will be incorparated into the information flow")
        return Empty()

    async def ChangeStatus(self, request, context) -> Empty:
        """Changes the internal state 

        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Change the system state")
        self._vr_state.status = request.status
        logger.info(f"New State has been set to: {self._vr_state.status}")
        return Empty()
